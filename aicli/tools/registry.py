"""Tool registry for managing LangChain tools."""

from typing import List, Dict, Any
from langchain_core.tools import Tool
from langchain_experimental.tools import PythonREPLTool

from ..utils.config import Config
from .file_tools import FileReadTool, FileSearchTool
from .git_tools import GitTool
from .shell_tools import SafeShellTool


class ToolRegistry:
    """Registry for managing and providing tools to the AI agent."""
    
    @staticmethod
    def get_tools(config: Config) -> List[Tool]:
        """Get all available tools based on configuration."""
        tools = []
        
        # Always include basic file tools
        tools.extend([
            FileReadTool(),
            FileSearchTool(),
        ])
        
        # Add Git tools
        tools.append(GitTool())
        
        # Add Python REPL tool
        tools.append(PythonREPLTool())
        
        # Add shell tools if enabled
        if config.security.enable_shell_tools:
            tools.append(SafeShellTool(
                whitelist=config.security.shell_whitelist,
                require_confirmation=config.security.confirm_destructive
            ))
        
        return tools
    
    @staticmethod
    def get_tool_info() -> Dict[str, Dict[str, Any]]:
        """Get information about available tools."""
        return {
            "file_read": {
                "name": "File Reader",
                "description": "Read and analyze project files",
                "category": "file_operations",
                "always_enabled": True,
            },
            "file_search": {
                "name": "File Search",
                "description": "Search for files and content in the project",
                "category": "file_operations", 
                "always_enabled": True,
            },
            "git": {
                "name": "Git Operations",
                "description": "Perform git operations like status, diff, log",
                "category": "version_control",
                "always_enabled": True,
            },
            "python_repl": {
                "name": "Python REPL",
                "description": "Execute Python code safely",
                "category": "code_execution",
                "always_enabled": True,
            },
            "shell": {
                "name": "Shell Commands",
                "description": "Execute safe shell commands",
                "category": "system",
                "always_enabled": False,
                "requires_config": "security.enable_shell_tools",
            },
        }