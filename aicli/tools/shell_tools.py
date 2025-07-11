"""Safe shell execution tools for the AI agent."""

import subprocess
import shlex
from typing import List, Set, Optional
from langchain_core.tools import BaseTool
from pathlib import Path


class SafeShellTool(BaseTool):
    """Safe shell command execution tool."""
    
    name: str = "shell"
    description: str = """Execute safe shell commands. Only whitelisted commands are allowed.
    Common allowed commands: git, npm, pip, pytest, ls, cat, grep, find
    
    Examples:
    - "ls -la" - list directory contents
    - "npm install" - install npm packages
    - "pytest tests/" - run tests
    - "pip list" - show installed packages
    """
    
    def __init__(self, whitelist: List[str], require_confirmation: bool = True):
        super().__init__()
        self.whitelist: Set[str] = set(whitelist)
        self.require_confirmation = require_confirmation
        
        # Add some basic safe commands
        self.whitelist.update(['ls', 'cat', 'grep', 'find', 'head', 'tail', 'wc'])
    
    def _run(self, command: str) -> str:
        """Execute shell command safely."""
        try:
            # Parse command
            parts = shlex.split(command.strip())
            if not parts:
                return "No command provided"
            
            base_command = parts[0].lower()
            
            # Check if command is whitelisted
            if not self._is_command_allowed(base_command):
                return f"Command '{base_command}' is not in the whitelist of allowed commands.\\nAllowed: {', '.join(sorted(self.whitelist))}"
            
            # Additional safety checks
            if self._is_dangerous_command(command):
                return f"Command appears to be dangerous and is blocked: {command}"
            
            # Execute command
            result = subprocess.run(
                parts,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=".",
                shell=False  # Never use shell=True for security
            )
            
            # Format output
            output_parts = []
            
            if result.stdout:
                output_parts.append(f"Output:\\n{result.stdout}")
                
            if result.stderr:
                output_parts.append(f"Errors:\\n{result.stderr}")
            
            if result.returncode != 0:
                output_parts.append(f"Exit code: {result.returncode}")
            
            if not output_parts:
                output_parts.append("Command completed successfully (no output)")
            
            return "\\n\\n".join(output_parts)
            
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds"
        except FileNotFoundError:
            return f"Command not found: {parts[0]}"
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    def _is_command_allowed(self, command: str) -> bool:
        """Check if command is in whitelist."""
        return command in self.whitelist
    
    def _is_dangerous_command(self, command: str) -> bool:
        """Check for potentially dangerous command patterns."""
        dangerous_patterns = [
            'rm -rf', 'rm -f', 'del ', 'format ', 'fdisk',
            'mkfs', 'dd if=', 'dd of=', '> /dev/', 'chmod 777',
            'chmod +x', 'sudo ', 'su ', 'passwd', 'useradd',
            'userdel', 'kill -9', 'killall', 'pkill',
            'wget ', 'curl ', 'ssh ', 'scp ', 'rsync ',
            'mount ', 'umount ', 'systemctl', 'service ',
            'iptables', 'firewall', 'netsh', 'ifconfig',
            'route ', 'ping -f', 'nmap ', 'nc ', 'netcat'
        ]
        
        command_lower = command.lower()
        return any(pattern in command_lower for pattern in dangerous_patterns)


class TestRunnerTool(BaseTool):
    """Tool for running tests safely."""
    
    name: str = "test_runner"
    description: str = """Run tests using various test frameworks.
    Supported frameworks: pytest, unittest, npm test, jest
    
    Examples:
    - "pytest" - run all pytest tests
    - "pytest tests/test_api.py" - run specific test file
    - "unittest discover" - run unittest tests
    - "npm test" - run npm tests
    """
    
    def _run(self, test_command: str) -> str:
        """Run tests."""
        try:
            parts = shlex.split(test_command.strip())
            if not parts:
                return "No test command provided"
            
            framework = parts[0].lower()
            
            # Validate test framework
            allowed_frameworks = {'pytest', 'python', 'npm', 'jest', 'unittest'}
            if framework not in allowed_frameworks:
                return f"Test framework '{framework}' not supported. Allowed: {', '.join(allowed_frameworks)}"
            
            # Execute test command
            result = subprocess.run(
                parts,
                capture_output=True,
                text=True,
                timeout=120,  # Longer timeout for tests
                cwd="."
            )
            
            # Format output
            output_parts = []
            
            if result.stdout:
                # Truncate very long output
                stdout = result.stdout
                if len(stdout) > 5000:
                    stdout = stdout[:5000] + "\\n... (output truncated)"
                output_parts.append(f"Test Output:\\n{stdout}")
            
            if result.stderr:
                stderr = result.stderr
                if len(stderr) > 2000:
                    stderr = stderr[:2000] + "\\n... (errors truncated)"
                output_parts.append(f"Test Errors:\\n{stderr}")
            
            # Add summary
            if result.returncode == 0:
                output_parts.append("✅ Tests passed!")
            else:
                output_parts.append(f"❌ Tests failed (exit code: {result.returncode})")
            
            return "\\n\\n".join(output_parts)
            
        except subprocess.TimeoutExpired:
            return "Test execution timed out after 2 minutes"
        except Exception as e:
            return f"Error running tests: {str(e)}"