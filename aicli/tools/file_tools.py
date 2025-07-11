"""File operation tools for the AI agent."""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_core.tools import BaseTool
from pydantic import Field
import fnmatch


class FileReadTool(BaseTool):
    """Tool for reading file contents."""
    
    name: str = "file_read"
    description: str = "Read the contents of a file. Input should be a file path."
    
    def _run(self, file_path: str) -> str:
        """Read file contents."""
        try:
            path = Path(file_path)
            if not path.exists():
                return f"File not found: {file_path}"
            
            if not path.is_file():
                return f"Path is not a file: {file_path}"
            
            # Check file size (limit to 1MB for safety)
            if path.stat().st_size > 1024 * 1024:
                return f"File too large to read: {file_path} (>1MB)"
            
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return f"Contents of {file_path}:\\n{content}"
            
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"


class FileSearchTool(BaseTool):
    """Tool for searching files and content."""
    
    name: str = "file_search"
    description: str = """Search for files and content in the project.
    Input should be a search query. Examples:
    - "*.py" - find all Python files
    - "function main" - find files containing "function main"
    - "class MyClass" - find files with class definitions
    """
    
    def _run(self, query: str) -> str:
        """Search for files and content."""
        try:
            results = []
            
            # If query looks like a file pattern, search by filename
            if any(char in query for char in ['*', '?', '.']):
                results = self._search_by_pattern(query)
            else:
                # Search by content
                results = self._search_by_content(query)
            
            if not results:
                return "No files found matching the search criteria."
            
            # Format results
            if len(results) > 20:
                results = results[:20]
                truncated_msg = f"\\n(Showing first 20 of {len(results)} results)"
            else:
                truncated_msg = ""
            
            formatted_results = "\\n".join([
                f"- {result['file']}" + (f": {result['context']}" if 'context' in result else "")
                for result in results
            ])
            
            return f"Search results:{truncated_msg}\\n{formatted_results}"
            
        except Exception as e:
            return f"Error searching: {str(e)}"
    
    def _search_by_pattern(self, pattern: str) -> List[Dict[str, str]]:
        """Search files by filename pattern."""
        results = []
        
        for root, dirs, files in os.walk("."):
            # Skip common directories to ignore
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if fnmatch.fnmatch(file, pattern):
                    file_path = os.path.join(root, file)
                    results.append({"file": file_path})
        
        return results
    
    def _search_by_content(self, query: str) -> List[Dict[str, str]]:
        """Search files by content."""
        results = []
        query_lower = query.lower()
        
        for root, dirs, files in os.walk("."):
            # Skip common directories to ignore
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                # Only search in text files
                if not self._is_text_file(file):
                    continue
                
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines):
                        if query_lower in line.lower():
                            context = line.strip()
                            if len(context) > 100:
                                context = context[:100] + "..."
                            
                            results.append({
                                "file": file_path,
                                "line": i + 1,
                                "context": context
                            })
                            break  # Only show first match per file
                            
                except Exception:
                    continue  # Skip files that can't be read
        
        return results
    
    def _is_text_file(self, filename: str) -> bool:
        """Check if file is likely a text file."""
        text_extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.scss',
            '.json', '.xml', '.yaml', '.yml', '.md', '.txt', '.rst',
            '.sql', '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat',
            '.c', '.cpp', '.cc', '.h', '.hpp', '.java', '.kt', '.scala',
            '.go', '.rs', '.rb', '.php', '.pl', '.r', '.swift', '.dart',
            '.vim', '.lua', '.tcl', '.awk', '.sed', '.grep', '.diff',
            '.patch', '.log', '.cfg', '.conf', '.ini', '.env'
        }
        
        return Path(filename).suffix.lower() in text_extensions


class FileWriteTool(BaseTool):
    """Tool for writing file contents (with safety checks)."""
    
    name: str = "file_write"
    description: str = """Write content to a file. Input should be in format:
    file_path|||content
    Example: main.py|||print("Hello World")
    """
    
    def _run(self, input_str: str) -> str:
        """Write content to file."""
        try:
            if "|||" not in input_str:
                return "Invalid format. Use: file_path|||content"
            
            file_path, content = input_str.split("|||", 1)
            file_path = file_path.strip()
            
            path = Path(file_path)
            
            # Safety checks
            if path.is_absolute() and not str(path).startswith(os.getcwd()):
                return "Cannot write files outside the current project directory"
            
            # Create backup if file exists
            if path.exists():
                backup_path = path.with_suffix(path.suffix + '.backup')
                path.rename(backup_path)
            
            # Create directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Successfully wrote to {file_path}"
            
        except Exception as e:
            return f"Error writing file: {str(e)}"