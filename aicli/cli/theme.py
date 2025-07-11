"""Beautiful Rich theme for AICLI."""

from rich.theme import Theme
from rich.style import Style


class AICliTheme:
    """Custom theme for AICLI with Claude Code-inspired colors."""
    
    @staticmethod
    def get_theme() -> Theme:
        """Get the AICLI Rich theme."""
        return Theme({
            # Base colors
            "primary": "bright_cyan",
            "secondary": "bright_blue", 
            "accent": "bright_magenta",
            "success": "bright_green",
            "warning": "bright_yellow",
            "error": "bright_red",
            "info": "bright_white",
            "muted": "dim white",
            
            # UI components
            "panel.border": "bright_cyan",
            "panel.title": "bright_white bold",
            "progress.bar": "bright_cyan",
            "progress.percentage": "bright_white",
            "progress.description": "bright_blue",
            
            # Code syntax highlighting
            "code.keyword": "bright_magenta",
            "code.string": "bright_green", 
            "code.number": "bright_cyan",
            "code.comment": "dim",
            "code.function": "bright_blue",
            "code.class": "bright_yellow",
            "code.variable": "bright_white",
            
            # Diff highlighting
            "diff.added": "bright_green",
            "diff.removed": "bright_red",
            "diff.modified": "bright_yellow",
            "diff.header": "bright_cyan bold",
            
            # REPL components
            "prompt": "bright_cyan bold",
            "prompt.user": "bright_white",
            "prompt.ai": "bright_blue",
            "response.thinking": "dim italic",
            "response.code": "bright_white on grey11",
            
            # Status indicators
            "status.connecting": "bright_yellow",
            "status.thinking": "bright_blue",
            "status.executing": "bright_magenta",
            "status.complete": "bright_green",
            "status.error": "bright_red",
            
            # Tool execution
            "tool.name": "bright_cyan bold",
            "tool.input": "bright_white",
            "tool.output": "dim white",
            "tool.error": "bright_red",
            
            # Session management
            "session.active": "bright_green",
            "session.archived": "dim",
            "session.name": "bright_cyan",
            
            # File operations
            "file.path": "bright_blue",
            "file.added": "bright_green",
            "file.modified": "bright_yellow", 
            "file.deleted": "bright_red",
            "file.size": "dim",
            
            # Help and documentation
            "help.command": "bright_cyan",
            "help.description": "bright_white",
            "help.example": "dim italic",
            
            # Configuration
            "config.key": "bright_cyan",
            "config.value": "bright_white",
            "config.section": "bright_yellow bold",
        })
    
    @staticmethod
    def get_syntax_theme() -> str:
        """Get the syntax highlighting theme name."""
        return "monokai"
    
    @staticmethod
    def get_spinner_style() -> str:
        """Get the spinner style for loading indicators."""
        return "dots"
    
    @staticmethod  
    def get_progress_style() -> dict:
        """Get progress bar styling."""
        return {
            "bar_width": 40,
            "complete_style": "bright_cyan",
            "finished_style": "bright_green",
            "pulse_style": "bright_blue",
        }