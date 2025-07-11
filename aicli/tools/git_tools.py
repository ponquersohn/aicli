"""Git operation tools for the AI agent."""

import subprocess
from typing import List, Dict, Any, Optional
from langchain_core.tools import BaseTool
from pathlib import Path


class GitTool(BaseTool):
    """Tool for Git operations."""
    
    name: str = "git"
    description: str = """Execute git commands safely. Supported commands:
    - status: Show git status
    - diff: Show git diff
    - log: Show recent commits
    - blame <file>: Show git blame for a file
    - branch: Show branches
    - add <file>: Stage a file
    - commit <message>: Commit staged changes
    
    Input should be the git command without 'git' prefix.
    Example: "status", "diff", "log --oneline -10"
    """
    
    def _run(self, command: str) -> str:
        """Execute git command."""
        try:
            # Parse command
            parts = command.strip().split()
            if not parts:
                return "No git command provided"
            
            git_cmd = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            # Validate command for safety
            if not self._is_safe_command(git_cmd):
                return f"Git command '{git_cmd}' is not allowed for safety reasons"
            
            # Build full git command
            full_command = ["git", git_cmd] + args
            
            # Execute command
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=30,
                cwd="."
            )
            
            if result.returncode != 0:
                return f"Git command failed:\\nError: {result.stderr}"
            
            output = result.stdout.strip()
            if not output:
                output = "Command completed successfully (no output)"
            
            return f"Git {command}:\\n{output}"
            
        except subprocess.TimeoutExpired:
            return "Git command timed out"
        except Exception as e:
            return f"Error executing git command: {str(e)}"
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if git command is safe to execute."""
        # Allow read-only and basic write operations
        safe_commands = {
            'status', 'diff', 'log', 'show', 'blame', 'branch',
            'ls-files', 'ls-tree', 'cat-file', 'rev-parse',
            'add', 'commit', 'checkout', 'switch', 'restore'
        }
        
        # Dangerous commands to avoid
        dangerous_commands = {
            'push', 'pull', 'fetch', 'merge', 'rebase', 'reset',
            'rm', 'clean', 'gc', 'prune', 'reflog', 'fsck',
            'remote', 'config', 'init', 'clone'
        }
        
        return command in safe_commands and command not in dangerous_commands


class GitAnalysisTool(BaseTool):
    """Tool for advanced Git analysis."""
    
    name: str = "git_analysis" 
    description: str = """Analyze git repository information.
    Supported analyses:
    - recent_changes: Show recently modified files
    - file_history <file>: Show history of a specific file
    - contributors: Show repository contributors
    - stats: Show repository statistics
    """
    
    def _run(self, analysis_type: str) -> str:
        """Perform git analysis."""
        try:
            parts = analysis_type.strip().split()
            if not parts:
                return "No analysis type provided"
            
            analysis = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            if analysis == "recent_changes":
                return self._get_recent_changes()
            elif analysis == "file_history" and args:
                return self._get_file_history(args[0])
            elif analysis == "contributors":
                return self._get_contributors()
            elif analysis == "stats":
                return self._get_repo_stats()
            else:
                return f"Unknown analysis type: {analysis}"
                
        except Exception as e:
            return f"Error performing git analysis: {str(e)}"
    
    def _get_recent_changes(self) -> str:
        """Get recently changed files."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-status", "HEAD~10..HEAD"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return "Could not get recent changes"
            
            if not result.stdout.strip():
                return "No recent changes found"
            
            return f"Recent changes:\\n{result.stdout}"
            
        except Exception as e:
            return f"Error getting recent changes: {str(e)}"
    
    def _get_file_history(self, filepath: str) -> str:
        """Get history of a specific file."""
        try:
            if not Path(filepath).exists():
                return f"File not found: {filepath}"
            
            result = subprocess.run(
                ["git", "log", "--oneline", "-10", "--", filepath],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return f"Could not get history for {filepath}"
            
            if not result.stdout.strip():
                return f"No git history found for {filepath}"
            
            return f"History of {filepath}:\\n{result.stdout}"
            
        except Exception as e:
            return f"Error getting file history: {str(e)}"
    
    def _get_contributors(self) -> str:
        """Get repository contributors."""
        try:
            result = subprocess.run(
                ["git", "shortlog", "-sn", "--all"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return "Could not get contributors"
            
            return f"Repository contributors:\\n{result.stdout}"
            
        except Exception as e:
            return f"Error getting contributors: {str(e)}"
    
    def _get_repo_stats(self) -> str:
        """Get repository statistics."""
        try:
            # Get basic stats
            stats = []
            
            # Total commits
            result = subprocess.run(
                ["git", "rev-list", "--all", "--count"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                stats.append(f"Total commits: {result.stdout.strip()}")
            
            # Branches
            result = subprocess.run(
                ["git", "branch", "-a"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                branch_count = len([l for l in result.stdout.split('\\n') if l.strip()])
                stats.append(f"Total branches: {branch_count}")
            
            # File count
            result = subprocess.run(
                ["git", "ls-files"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                file_count = len([l for l in result.stdout.split('\\n') if l.strip()])
                stats.append(f"Tracked files: {file_count}")
            
            return "Repository statistics:\\n" + "\\n".join(stats)
            
        except Exception as e:
            return f"Error getting repository stats: {str(e)}"