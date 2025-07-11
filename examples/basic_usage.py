#!/usr/bin/env python3
"""
Basic usage example for AICLI.

This script demonstrates how to use AICLI programmatically.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import aicli
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aicli.utils.config import Config
from aicli.agent.core import AIAgent


def main():
    """Demonstrate basic AICLI usage."""
    print("🤖 AICLI Basic Usage Example")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Create configuration
    config = Config()
    
    # Override some settings for the example
    config.llm.provider = "anthropic"  # Can change to "openai" if you have OpenAI API key
    config.llm.model = "claude-3-haiku-20240307"  # Using a faster/cheaper model for demo
    config.security.enable_shell_tools = False  # Keep it safe
    
    print(f"✓ Configuration loaded")
    print(f"  Provider: {config.llm.provider}")
    print(f"  Model: {config.llm.model}")
    print()
    
    # Check if API key is available
    api_key_available = False
    if config.llm.provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
        api_key_available = True
    elif config.llm.provider == "openai" and os.getenv("OPENAI_API_KEY"):
        api_key_available = True
    
    if not api_key_available:
        print("⚠️  No API key found for the configured provider.")
        print("   Please set ANTHROPIC_API_KEY or OPENAI_API_KEY in your environment.")
        print("   You can copy .env.example to .env and add your API keys.")
        print()
        print("🔧 For now, showing configuration and available tools...")
        
        # Show available tools
        from aicli.tools.registry import ToolRegistry
        tools = ToolRegistry.get_tools(config)
        print(f"📦 Available tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description[:60]}...")
        return
    
    try:
        # Create AI agent
        print("🚀 Creating AI agent...")
        agent = AIAgent(config)
        print("✓ AI agent created successfully")
        print()
        
        # Example queries to demonstrate different capabilities
        examples = [
            "What files are in the current directory?",
            "Show me the structure of this project",
            "What's in the README.md file?",
        ]
        
        for i, query in enumerate(examples, 1):
            print(f"Example {i}: {query}")
            print("-" * 50)
            
            try:
                response = agent.execute(query)
                print(response)
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print()
            
            # Ask user if they want to continue
            if i < len(examples):
                try:
                    input("Press Enter to continue to next example (or Ctrl+C to stop)...")
                except KeyboardInterrupt:
                    print("\n👋 Stopping examples.")
                    break
        
        print("✨ Examples completed! Try running 'aicli' for interactive mode.")
        
    except Exception as e:
        print(f"❌ Error creating or using AI agent: {e}")
        print("   Make sure your API key is correctly configured.")


if __name__ == "__main__":
    main()