"""LLM factory for creating different language model instances."""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import Ollama
from langchain_core.language_models import BaseLanguageModel

from ..utils.config import LLMConfig


class LLMFactory:
    """Factory for creating LLM instances."""
    
    @staticmethod
    def create_llm(config: LLMConfig) -> BaseLanguageModel:
        """Create an LLM instance based on configuration."""
        provider = config.provider.lower()
        
        if provider == "openai":
            return LLMFactory._create_openai(config)
        elif provider == "anthropic":
            return LLMFactory._create_anthropic(config)
        elif provider == "ollama":
            return LLMFactory._create_ollama(config)
        elif provider == "fireworks":
            return LLMFactory._create_fireworks(config)
        elif provider == "together":
            return LLMFactory._create_together(config)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    @staticmethod
    def _create_openai(config: LLMConfig) -> ChatOpenAI:
        """Create OpenAI LLM instance."""
        kwargs = {
            "model": config.model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "timeout": config.timeout,
        }
        
        if config.api_key:
            kwargs["api_key"] = config.api_key
        if config.base_url:
            kwargs["base_url"] = config.base_url
            
        return ChatOpenAI(**kwargs)
    
    @staticmethod
    def _create_anthropic(config: LLMConfig) -> ChatAnthropic:
        """Create Anthropic LLM instance."""
        kwargs = {
            "model": config.model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "timeout": config.timeout,
        }
        
        if config.api_key:
            kwargs["api_key"] = config.api_key
        if config.base_url:
            kwargs["base_url"] = config.base_url
            
        return ChatAnthropic(**kwargs)
    
    @staticmethod
    def _create_ollama(config: LLMConfig) -> Ollama:
        """Create Ollama LLM instance."""
        kwargs = {
            "model": config.model,
            "temperature": config.temperature,
        }
        
        if config.base_url:
            kwargs["base_url"] = config.base_url
        else:
            kwargs["base_url"] = "http://localhost:11434"
            
        return Ollama(**kwargs)
    
    @staticmethod
    def _create_fireworks(config: LLMConfig) -> ChatOpenAI:
        """Create Fireworks LLM instance using OpenAI-compatible API."""
        kwargs = {
            "model": config.model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "base_url": config.base_url or "https://api.fireworks.ai/inference/v1",
            "timeout": config.timeout,
        }
        
        if config.api_key:
            kwargs["api_key"] = config.api_key
            
        return ChatOpenAI(**kwargs)
    
    @staticmethod
    def _create_together(config: LLMConfig) -> ChatOpenAI:
        """Create Together AI LLM instance using OpenAI-compatible API."""
        kwargs = {
            "model": config.model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "base_url": config.base_url or "https://api.together.xyz/v1",
            "timeout": config.timeout,
        }
        
        if config.api_key:
            kwargs["api_key"] = config.api_key
            
        return ChatOpenAI(**kwargs)
    
    @staticmethod
    def get_available_providers() -> Dict[str, Dict[str, Any]]:
        """Get information about available LLM providers."""
        return {
            "openai": {
                "name": "OpenAI",
                "models": ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"],
                "requires_api_key": True,
                "default_model": "gpt-4",
            },
            "anthropic": {
                "name": "Anthropic",
                "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
                "requires_api_key": True,
                "default_model": "claude-3-sonnet-20240229",
            },
            "ollama": {
                "name": "Ollama (Local)",
                "models": ["llama2", "codellama", "mistral", "neural-chat"],
                "requires_api_key": False,
                "default_model": "llama2",
            },
            "fireworks": {
                "name": "Fireworks AI",
                "models": ["accounts/fireworks/models/llama-v2-70b-chat"],
                "requires_api_key": True,
                "default_model": "accounts/fireworks/models/llama-v2-70b-chat",
            },
            "together": {
                "name": "Together AI",
                "models": ["meta-llama/Llama-2-70b-chat-hf", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
                "requires_api_key": True,
                "default_model": "meta-llama/Llama-2-70b-chat-hf",
            },
        }