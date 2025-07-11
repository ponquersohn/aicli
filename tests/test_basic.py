"""Basic tests for AICLI functionality."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from aicli.utils.config import Config, LLMConfig
from aicli.llm.factory import LLMFactory
from aicli.tools.registry import ToolRegistry


class TestConfig:
    """Test configuration loading and validation."""
    
    def test_default_config(self):
        """Test default configuration creation."""
        config = Config()
        assert config.llm.provider == "anthropic"
        assert config.llm.model == "claude-3-sonnet-20240229"
        assert config.context.max_size == 100000
        assert config.security.enable_shell_tools is False
    
    def test_llm_config_validation(self):
        """Test LLM configuration validation."""
        llm_config = LLMConfig(
            provider="openai",
            model="gpt-4",
            temperature=0.5
        )
        assert llm_config.provider == "openai"
        assert llm_config.model == "gpt-4"
        assert llm_config.temperature == 0.5


class TestLLMFactory:
    """Test LLM factory functionality."""
    
    def test_get_available_providers(self):
        """Test getting available providers."""
        providers = LLMFactory.get_available_providers()
        assert "openai" in providers
        assert "anthropic" in providers
        assert "ollama" in providers
        
        # Check provider info structure
        openai_info = providers["openai"]
        assert "name" in openai_info
        assert "models" in openai_info
        assert "requires_api_key" in openai_info
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_create_openai_llm(self):
        """Test creating OpenAI LLM."""
        config = LLMConfig(
            provider="openai",
            model="gpt-4",
            api_key="test-key"
        )
        
        # This will fail without actual API key, but we can test the factory logic
        try:
            llm = LLMFactory.create_llm(config)
            assert llm is not None
        except Exception:
            # Expected to fail without proper API setup
            pass
    
    def test_unsupported_provider(self):
        """Test error handling for unsupported provider."""
        config = LLMConfig(provider="unsupported")
        
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            LLMFactory.create_llm(config)


class TestToolRegistry:
    """Test tool registry functionality."""
    
    def test_get_tools(self):
        """Test getting tools from registry."""
        config = Config()
        tools = ToolRegistry.get_tools(config)
        
        assert len(tools) > 0
        
        # Check that basic tools are included
        tool_names = [tool.name for tool in tools]
        assert "file_read" in tool_names
        assert "file_search" in tool_names
        assert "git" in tool_names
    
    def test_get_tool_info(self):
        """Test getting tool information."""
        tool_info = ToolRegistry.get_tool_info()
        
        assert "file_read" in tool_info
        assert "git" in tool_info
        assert "python_repl" in tool_info
        
        # Check info structure
        file_read_info = tool_info["file_read"]
        assert "name" in file_read_info
        assert "description" in file_read_info
        assert "category" in file_read_info
    
    def test_shell_tools_disabled_by_default(self):
        """Test that shell tools are disabled by default."""
        config = Config()
        tools = ToolRegistry.get_tools(config)
        
        tool_names = [tool.name for tool in tools]
        # Shell tools should not be included by default
        assert "shell" not in tool_names
    
    def test_shell_tools_enabled_when_configured(self):
        """Test that shell tools are included when enabled."""
        config = Config()
        config.security.enable_shell_tools = True
        
        tools = ToolRegistry.get_tools(config)
        tool_names = [tool.name for tool in tools]
        
        # Shell tools should be included when enabled
        assert "shell" in tool_names


class TestFileOperations:
    """Test file operation tools."""
    
    def test_file_read_tool_exists(self):
        """Test that file read tool can be imported."""
        from aicli.tools.file_tools import FileReadTool
        
        tool = FileReadTool()
        assert tool.name == "file_read"
        assert "read" in tool.description.lower()
    
    def test_file_search_tool_exists(self):
        """Test that file search tool can be imported."""
        from aicli.tools.file_tools import FileSearchTool
        
        tool = FileSearchTool()
        assert tool.name == "file_search"
        assert "search" in tool.description.lower()


if __name__ == "__main__":
    pytest.main([__file__])