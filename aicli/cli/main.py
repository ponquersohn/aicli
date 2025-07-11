"""Main CLI entrypoint for AICLI."""

import os
import sys
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich import print as rprint
from dotenv import load_dotenv

from ..utils.config import Config
from ..utils.logger import setup_logger
from .interface import InteractiveInterface
from .theme import AICliTheme

# Load environment variables
load_dotenv()

# Initialize console with custom theme
console = Console(theme=AICliTheme.get_theme())

# Create Typer app
app = typer.Typer(
    name="aicli",
    help="🤖 A beautiful CLI tool for conversational code assistance",
    rich_markup_mode="rich",
    no_args_is_help=False,
)


def display_banner():
    """Display the beautiful AICLI startup banner."""
    banner_text = Text()
    banner_text.append("  ╔═══════════════════════════════════════╗\n", style="cyan bold")
    banner_text.append("  ║                                       ║\n", style="cyan bold")
    banner_text.append("  ║            🤖 AICLI v0.1.0           ║\n", style="bright_white bold")
    banner_text.append("  ║                                       ║\n", style="cyan bold")
    banner_text.append("  ║    Conversational Code Assistant      ║\n", style="bright_blue")
    banner_text.append("  ║         Powered by LangChain          ║\n", style="bright_blue")
    banner_text.append("  ║                                       ║\n", style="cyan bold")
    banner_text.append("  ╚═══════════════════════════════════════╝", style="cyan bold")
    
    panel = Panel(
        Align.center(banner_text),
        border_style="bright_cyan",
        padding=(0, 2),
    )
    console.print(panel)
    console.print()


def display_welcome_message():
    """Display welcome message with helpful tips."""
    welcome_parts = [
        Text("💡 Welcome to AICLI!", style="bright_yellow bold"),
        Text("Type your questions in natural language", style="bright_white"),
        Text("Use '/help' for commands or '/exit' to quit", style="dim"),
    ]
    
    for part in welcome_parts:
        console.print(Align.center(part))
    console.print()


@app.command()
def main(
    query: Optional[str] = typer.Argument(
        None,
        help="Query to execute in non-interactive mode"
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="LLM model to use (e.g., gpt-4, claude-3-sonnet)"
    ),
    provider: Optional[str] = typer.Option(
        None,
        "--provider",
        "-p",
        help="LLM provider (openai, anthropic, fireworks, together, ollama)"
    ),
    config_file: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file"
    ),
    include: Optional[List[str]] = typer.Option(
        None,
        "--include",
        "-i",
        help="Include specific files in context"
    ),
    exclude: Optional[List[str]] = typer.Option(
        None,
        "--exclude",
        "-e",
        help="Exclude files from context"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview changes without applying them"
    ),
    apply: bool = typer.Option(
        False,
        "--apply",
        help="Apply changes without confirmation"
    ),
    resume: Optional[str] = typer.Option(
        None,
        "--resume",
        "-r",
        help="Resume a previous session"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug mode"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output"
    ),
):
    """
    🤖 AICLI - Conversational Code Assistant
    
    Start an interactive session or execute a single query.
    
    Examples:
    
        # Interactive mode
        $ aicli
        
        # Single query
        $ aicli "Refactor this function for better readability"
        
        # With specific model
        $ aicli --model claude-3-sonnet "Fix the bug in auth.py"
        
        # Include specific files
        $ aicli --include src/main.py tests/test_main.py "Add error handling"
        
        # Dry run mode
        $ aicli "Remove unused imports" --dry-run
    """
    try:
        # Load configuration
        config = Config.load(config_file, debug=debug, verbose=verbose)
        
        # Override config with CLI arguments
        if model:
            config.llm.model = model
        if provider:
            config.llm.provider = provider
        if include:
            config.context.include_files.extend(include)
        if exclude:
            config.context.exclude_files.extend(exclude)
        if dry_run:
            config.editor.dry_run = True
        if apply:
            config.editor.auto_apply = True
        if resume:
            config.session.resume_session = resume
            
        # Setup logging
        logger = setup_logger(config.logging.level, config.logging.file)
        
        if query:
            # Non-interactive mode - execute single query
            from ..agent.core import AIAgent
            
            agent = AIAgent(config)
            response = agent.execute(query)
            console.print(response)
        else:
            # Interactive mode
            display_banner()
            display_welcome_message()
            
            interface = InteractiveInterface(config)
            interface.run()
            
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!", style="bright_yellow")
        sys.exit(0)
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bright_red")
        if debug:
            console.print_exception()
        sys.exit(1)


@app.command()
def version():
    """Display version information."""
    version_info = {
        "AICLI": "0.1.0",
        "Python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "Platform": sys.platform,
    }
    
    for key, value in version_info.items():
        console.print(f"[bright_cyan]{key}:[/bright_cyan] [bright_white]{value}[/bright_white]")


@app.command()
def config():
    """Display current configuration."""
    try:
        config = Config.load()
        console.print(config.to_rich_table())
    except Exception as e:
        console.print(f"❌ Error loading config: {e}", style="bright_red")


if __name__ == "__main__":
    app()