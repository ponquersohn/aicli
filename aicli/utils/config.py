"""Configuration management for AICLI."""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
import yaml
from rich.table import Table
from rich.console import Console


class LLMConfig(BaseModel):
    """LLM configuration."""
    provider: str = Field(default="anthropic", description="LLM provider")
    model: str = Field(default="claude-3-sonnet-20240229", description="Model name")
    api_key: Optional[str] = Field(default=None, description="API key")
    base_url: Optional[str] = Field(default=None, description="API base URL")
    temperature: float = Field(default=0.7, description="Model temperature")
    max_tokens: int = Field(default=4000, description="Maximum tokens")
    timeout: int = Field(default=30, description="Request timeout in seconds")


class ContextConfig(BaseModel):
    """Context management configuration."""
    max_size: int = Field(default=100000, description="Maximum context size in tokens")
    auto_load: bool = Field(default=True, description="Automatically load relevant files")
    include_files: List[str] = Field(default_factory=list, description="Files to always include")
    exclude_files: List[str] = Field(default_factory=list, description="Files to exclude")
    exclude_patterns: List[str] = Field(
        default_factory=lambda: ["*.pyc", "*.log", ".git/*", "__pycache__/*"],
        description="File patterns to exclude"
    )
    cache_size: str = Field(default="50MB", description="Context cache size")


class SessionConfig(BaseModel):
    """Session management configuration."""
    directory: str = Field(default="./sessions", description="Session storage directory")
    auto_save: bool = Field(default=True, description="Automatically save sessions")
    max_size: str = Field(default="10MB", description="Maximum session size")
    resume_session: Optional[str] = Field(default=None, description="Session to resume")


class EditorConfig(BaseModel):
    """Editor configuration."""
    backup_files: bool = Field(default=True, description="Backup files before editing")
    backup_dir: str = Field(default="./backups", description="Backup directory")
    dry_run: bool = Field(default=False, description="Preview changes without applying")
    auto_apply: bool = Field(default=False, description="Apply changes without confirmation")
    max_file_size: str = Field(default="1MB", description="Maximum file size to edit")


class SecurityConfig(BaseModel):
    """Security configuration."""
    enable_shell_tools: bool = Field(default=False, description="Enable shell command tools")
    shell_whitelist: List[str] = Field(
        default_factory=lambda: ["git", "npm", "pip", "pytest"],
        description="Whitelisted shell commands"
    )
    confirm_destructive: bool = Field(default=True, description="Confirm destructive operations")


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO", description="Log level")
    file: Optional[str] = Field(default="aicli.log", description="Log file path")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )


class UIConfig(BaseModel):
    """UI configuration."""
    theme: str = Field(default="aicli", description="Rich theme name")
    syntax_highlighting: bool = Field(default=True, description="Enable syntax highlighting")
    markdown_rendering: bool = Field(default=True, description="Enable markdown rendering")
    terminal_width: str = Field(default="auto", description="Terminal width")
    animations: bool = Field(default=True, description="Enable animations")


class Config(BaseSettings):
    """Main configuration class."""
    
    llm: LLMConfig = Field(default_factory=LLMConfig)
    context: ContextConfig = Field(default_factory=ContextConfig)
    session: SessionConfig = Field(default_factory=SessionConfig)
    editor: EditorConfig = Field(default_factory=EditorConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        case_sensitive = False
    
    @classmethod
    def load(
        cls,
        config_file: Optional[Path] = None,
        debug: bool = False,
        verbose: bool = False
    ) -> "Config":
        """Load configuration from file and environment."""
        # Start with default config
        config_data = {}
        
        # Load from YAML file if specified or exists
        yaml_file = config_file or cls._find_config_file()
        if yaml_file and yaml_file.exists():
            with open(yaml_file, 'r') as f:
                config_data = yaml.safe_load(f) or {}
        
        # Create config instance (this will also load from environment)
        config = cls(**config_data)
        
        # Override with debug/verbose flags
        if debug:
            config.logging.level = "DEBUG"
        if verbose:
            config.logging.level = "DEBUG"
            
        # Load API keys from environment if not set
        config._load_api_keys()
        
        return config
    
    @staticmethod
    def _find_config_file() -> Optional[Path]:
        """Find configuration file in standard locations."""
        possible_locations = [
            Path(".claudecli.yaml"),
            Path(".claudecli.yml"),
            Path("aicli.yaml"),
            Path("aicli.yml"),
            Path.home() / ".config" / "aicli" / "config.yaml",
            Path.home() / ".aicli.yaml",
        ]
        
        for location in possible_locations:
            if location.exists():
                return location
        return None
    
    def _load_api_keys(self):
        """Load API keys from environment variables."""
        provider_keys = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY", 
            "fireworks": "FIREWORKS_API_KEY",
            "together": "TOGETHER_API_KEY",
        }
        
        if not self.llm.api_key and self.llm.provider in provider_keys:
            env_key = provider_keys[self.llm.provider]
            self.llm.api_key = os.getenv(env_key)
        
        # Load model from environment if not set
        provider_models = {
            "openai": os.getenv("OPENAI_MODEL"),
            "anthropic": os.getenv("ANTHROPIC_MODEL"),
            "fireworks": os.getenv("FIREWORKS_MODEL"),
            "together": os.getenv("TOGETHER_MODEL"),
            "ollama": os.getenv("OLLAMA_MODEL"),
        }
        
        if self.llm.provider in provider_models and provider_models[self.llm.provider]:
            self.llm.model = provider_models[self.llm.provider]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return self.dict()
    
    def to_yaml(self) -> str:
        """Convert config to YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False, indent=2)
    
    def save(self, file_path: Path):
        """Save configuration to YAML file."""
        with open(file_path, 'w') as f:
            f.write(self.to_yaml())
    
    def to_rich_table(self) -> Table:
        """Convert config to Rich table for display."""
        table = Table(title="🔧 AICLI Configuration", show_header=True, header_style="bright_cyan bold")
        table.add_column("Section", style="bright_cyan")
        table.add_column("Setting", style="bright_white")
        table.add_column("Value", style="dim")
        
        sections = {
            "LLM": self.llm.dict(),
            "Context": self.context.dict(),
            "Session": self.session.dict(),
            "Editor": self.editor.dict(),
            "Security": self.security.dict(),
            "Logging": self.logging.dict(),
            "UI": self.ui.dict(),
        }
        
        for section_name, section_data in sections.items():
            for key, value in section_data.items():
                # Hide sensitive values
                if "key" in key.lower() or "password" in key.lower():
                    display_value = "***" if value else "not set"
                else:
                    display_value = str(value)
                
                table.add_row(section_name, key, display_value)
                section_name = ""  # Only show section name for first row
        
        return table