"""Interactive REPL interface for AICLI."""

import sys
import readline
from typing import Optional, List
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from rich.columns import Columns
from rich.align import Align

from .theme import AICliTheme
from ..utils.config import Config
from ..agent.core import AIAgent


class InteractiveInterface:
    """Beautiful interactive REPL interface."""
    
    def __init__(self, config: Config):
        self.config = config
        self.console = Console(theme=AICliTheme.get_theme())
        self.agent = AIAgent(config)
        self.session_active = True
        self.command_history: List[str] = []
        self._setup_readline()
        
    def run(self):
        """Start the interactive REPL."""
        try:
            while self.session_active:
                self._process_input()
        except KeyboardInterrupt:
            self._handle_exit()
        except EOFError:
            self._handle_exit()
    
    def _process_input(self):
        """Process a single input from the user."""
        try:
            # Get user input with beautiful prompt
            user_input = self._get_user_input()
            
            if not user_input.strip():
                return
                
            # Handle special commands
            if user_input.startswith('/'):
                self._handle_command(user_input)
                return
            
            # Add to history
            self.command_history.append(user_input)
            
            # Show thinking indicator and process with AI
            self._show_ai_response(user_input)
            
        except KeyboardInterrupt:
            self.console.print("\n[dim]Use /exit to quit[/dim]")
    
    def _setup_readline(self):
        """Configure readline for command history and navigation."""
        # Enable history
        readline.parse_and_bind("tab: complete")
        readline.parse_and_bind("set show-all-if-ambiguous on")
        readline.parse_and_bind("set completion-ignore-case on")
        
        # Set up history
        readline.set_history_length(1000)
        
        # Load history from previous sessions if it exists
        try:
            readline.read_history_file(".aicli_history")
        except FileNotFoundError:
            pass
    
    def _get_user_input(self) -> str:
        """Get user input with a beautiful prompt and full navigation support."""
        # Display the prompt using Rich
        prompt_text = Text()
        prompt_text.append("💬 ", style="bright_cyan")
        prompt_text.append("You", style="bright_white bold")
        prompt_text.append(" › ", style="bright_cyan")
        
        # Print the prompt without newline
        self.console.print(prompt_text, end="")
        
        try:
            # Use input() with readline support for full navigation
            user_input = input()
            
            # Add to readline history if not empty
            if user_input.strip():
                readline.add_history(user_input)
                # Save history to file
                try:
                    readline.write_history_file(".aicli_history")
                except:
                    pass
            
            return user_input
        except (EOFError, KeyboardInterrupt):
            print()  # Print newline for clean exit
            raise
    
    def _show_ai_response(self, user_input: str):
        """Show AI response with beautiful formatting."""
        # Create thinking indicator
        thinking_text = Text()
        thinking_text.append("🤖 ", style="bright_blue")
        thinking_text.append("AICLI", style="bright_blue bold")
        thinking_text.append(" is thinking...", style="dim italic")
        
        with Live(
            Spinner("dots", text=thinking_text, style="bright_blue"),
            console=self.console,
            refresh_per_second=10
        ):
            try:
                # Get AI response
                response = self.agent.execute(user_input)
                
                # Display AI response
                self._display_response(response)
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
    
    def _display_response(self, response: str):
        """Display AI response with beautiful formatting."""
        # AI response header
        ai_header = Text()
        ai_header.append("🤖 ", style="bright_blue")
        ai_header.append("AICLI", style="bright_blue bold")
        ai_header.append(" › ", style="bright_blue")
        
        self.console.print(ai_header, end="")
        self.console.print()
        
        # Parse and display response with markdown
        if self._looks_like_markdown(response):
            markdown = Markdown(response)
            panel = Panel(
                markdown,
                border_style="bright_blue",
                padding=(1, 2),
            )
            self.console.print(panel)
        else:
            # Simple text response
            self.console.print(response, style="bright_white")
        
        self.console.print()
    
    def _looks_like_markdown(self, text: str) -> bool:
        """Check if text contains markdown formatting."""
        markdown_indicators = ['```', '`', '**', '*', '#', '- ', '1. ', '[', ']']
        return any(indicator in text for indicator in markdown_indicators)
    
    def _handle_command(self, command: str):
        """Handle special commands starting with /."""
        command = command.lower().strip()
        
        if command in ['/exit', '/quit', '/q']:
            self._handle_exit()
        elif command in ['/help', '/h']:
            self._show_help()
        elif command in ['/clear', '/cls']:
            self._clear_screen()
        elif command in ['/history']:
            self._show_history()
        elif command in ['/config']:
            self._show_config()
        elif command.startswith('/model '):
            self._change_model(command[7:])
        elif command.startswith('/session '):
            self._handle_session_command(command[9:])
        else:
            self.console.print(f"❌ Unknown command: {command}", style="error")
            self.console.print("💡 Type [bright_cyan]/help[/bright_cyan] for available commands")
    
    def _handle_exit(self):
        """Handle graceful exit."""
        self.console.print("\n👋 Thanks for using AICLI! Goodbye!", style="bright_yellow")
        self.session_active = False
        sys.exit(0)
    
    def _show_help(self):
        """Display help information."""
        help_content = """
# 🤖 AICLI Commands

## Basic Commands
- `/help` or `/h` - Show this help message
- `/exit` or `/quit` - Exit AICLI
- `/clear` - Clear the screen
- `/history` - Show command history

## Configuration
- `/config` - Show current configuration
- `/model <name>` - Switch LLM model

## Session Management  
- `/session save <name>` - Save current session
- `/session load <name>` - Load a session
- `/session list` - List saved sessions

## Tips
- Type naturally - AICLI understands conversational prompts
- Ask about code, request refactoring, or get explanations
- AICLI can read your project files automatically
- Use Ctrl+C to interrupt, then /exit to quit safely
        """
        
        panel = Panel(
            Markdown(help_content.strip()),
            title="[bright_cyan bold]AICLI Help[/bright_cyan bold]",
            border_style="bright_cyan",
            padding=(1, 2),
        )
        self.console.print(panel)
    
    def _clear_screen(self):
        """Clear the terminal screen."""
        self.console.clear()
        # Redisplay banner after clearing
        from .main import display_banner, display_welcome_message
        display_banner()
        display_welcome_message()
    
    def _show_history(self):
        """Show command history."""
        if not self.command_history:
            self.console.print("📝 No command history yet", style="dim")
            return
            
        history_text = "\\n".join([
            f"{i+1:2d}. {cmd}" 
            for i, cmd in enumerate(self.command_history[-10:])  # Last 10 commands
        ])
        
        panel = Panel(
            history_text,
            title="[bright_cyan bold]Recent Commands[/bright_cyan bold]",
            border_style="bright_cyan",
            padding=(1, 2),
        )
        self.console.print(panel)
    
    def _show_config(self):
        """Show current configuration."""
        self.console.print(self.config.to_rich_table())
    
    def _change_model(self, model_name: str):
        """Change the LLM model."""
        try:
            self.config.llm.model = model_name.strip()
            self.agent = AIAgent(self.config)  # Reinitialize agent
            self.console.print(f"🔄 Switched to model: [bright_cyan]{model_name}[/bright_cyan]")
        except Exception as e:
            self.console.print(f"❌ Error switching model: {e}", style="error")
    
    def _handle_session_command(self, args: str):
        """Handle session-related commands."""
        parts = args.strip().split()
        if not parts:
            self.console.print("❌ Session command requires arguments", style="error")
            return
            
        action = parts[0].lower()
        
        if action == "save" and len(parts) > 1:
            session_name = parts[1]
            self.console.print(f"💾 Saving session: [bright_cyan]{session_name}[/bright_cyan]")
            # TODO: Implement session saving
            
        elif action == "load" and len(parts) > 1:
            session_name = parts[1]
            self.console.print(f"📂 Loading session: [bright_cyan]{session_name}[/bright_cyan]")
            # TODO: Implement session loading
            
        elif action == "list":
            self.console.print("📋 Available sessions:")
            # TODO: Implement session listing
            
        else:
            self.console.print("❌ Invalid session command", style="error")
            self.console.print("💡 Usage: /session [save|load|list] [name]")