# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **AICLI** - an open-source CLI tool similar to Claude Code, built with LangChain for conversational code assistance. The project is currently in the planning/specification phase with detailed documentation but no implementation yet. You will be implementing this tool from scratch based on the specifications.

## Project Architecture

The planned architecture follows a modular design:

- **`aicli/cli.py`** - CLI entrypoint using Typer/Rich for terminal interaction
- **`aicli/agent.py`** - Core LangChain agent logic handling actions, tools, and memory
- **`aicli/context/`** - File scanning, embedding, and memory handling for project context
- **`aicli/llm/`** - Model backend handling with support for multiple LLM providers (Claude, GPT-4, Mistral, Ollama)
- **`aicli/tools/`** - LangChain tools including Python REPL, Git integration, shell commands, test runner
- **`aicli/editor/`** - Code editing, diff preview, and file modification capabilities
- **`aicli/utils/`** - Logging, path handling, and subprocess utilities
- **`tests/`** - Unit and integration tests
- **`sessions/`** - Persistent conversation memory storage
- **`examples/`** - Sample projects for testing and demonstration

## MVP Features to Implement

### Phase 1: Core CLI & LLM Integration
- **Multi-LLM Support**: Pluggable backends via LangChain (ChatOpenAI, ChatAnthropic, ChatFireworks, ChatOllama, ChatTogether)
- **REPL Interface**: Interactive terminal with Rich/Typer, multi-line input support, colored syntax highlighting
- **Configuration**: Support for `.claudecli.yaml` config files and environment variables for API keys
- **Basic Chat**: Conversational AI assistant functionality

### Phase 2: Project Context & File Operations  
- **Project Context Awareness**: Automatic file scanning with smart context loading strategies
- **File Context Loading**: Load relevant files based on user prompts, recency, and file size
- **Natural Language Code Editing**: File modifications with diff preview and --dry-run/--apply modes
- **Multi-File Operations**: Cross-file refactoring, function renaming, file splitting

### Phase 3: Essential LangChain Tools
- **PythonREPLTool**: Execute Python code snippets safely
- **GitTool**: Git operations (status, diff, blame, history, branch management)
- **FileSearchTool**: Semantic file search and content discovery
- **TerminalTool**: Safe shell command execution (disabled by default)
- **TestRunnerTool**: Pytest/unittest integration with auto-run and feedback

### Phase 4: Memory & Session Management
- **Conversation Memory**: LangChain ConversationBufferMemory for session history
- **Session Persistence**: Save/load conversations with `--resume session_name`
- **File-level Memory**: Remember recent changes and summaries per file
- **Context Caching**: Efficient context management with change detection

### Phase 5: Advanced Features
- **LLM Feedback Loop**: Auto-run linting/testing after changes, feed results back to LLM
- **Batch Operations**: Multiple file edits with preview and confirmation
- **Vector Search**: Semantic file selection using embeddings (FAISS/Chroma)
- **Plugin System**: Custom tool registration and 3rd-party extensions

## Current Status

This repository contains only documentation and specifications:
- `README.md` - Project structure and architectural overview
- `FEATURES.md` - Detailed feature specifications and MVP development phases

No actual code implementation exists yet. You will need to create the entire codebase from scratch. The project is designed to be developed in phases:
1. Basic CLI and LLM integration
2. File context and editing capabilities  
3. LangChain tools integration
4. Memory and session management
5. Advanced features like vector search and plugins

## Development Commands

Since this is a new Python project, you will need to:
- Create `pyproject.toml` for project configuration and dependencies
- Set up development dependencies (pytest, black, ruff, pre-commit)
- Use `pip install -e .` for local development installation
- Run tests with `pytest`
- Format code with `black`
- Lint with `ruff`
- Run type checking with `mypy`
- Test feedback integration: `claude-cli "Fix errors" --feedback lint`

## Required Dependencies

### Core Dependencies
- `langchain` - LLM abstraction and agent framework
- `langchain-openai` - OpenAI integration
- `langchain-anthropic` - Anthropic Claude integration
- `langchain-community` - Additional LLM providers and tools
- `typer[all]` - CLI framework with Rich support
- `rich` - Terminal formatting and syntax highlighting
- `pyyaml` - Configuration file support
- `python-dotenv` - Environment variable management

### Development Dependencies
- `pytest` - Testing framework
- `pytest-asyncio` - Async testing support
- `black` - Code formatting
- `ruff` - Fast Python linter
- `mypy` - Type checking
- `pre-commit` - Git hooks for code quality

## Security & Safety Requirements

Critical security features that must be implemented:
- **No unguarded shell execution** - TerminalTool disabled by default
- **File edit confirmation** - Always preview diffs before applying changes
- **Prompt safety checks** - Detect and prevent destructive commands
- **API key protection** - Never log or expose sensitive credentials
- **Sandboxed execution** - Isolate Python code execution when possible
- **Tool enable/disable** - Granular control over which tools are active

## Implementation Guidelines

When implementing:
- Use LangChain for LLM abstractions and tool integration
- Implement Rich/Typer for CLI interface with colored output and markdown rendering
- Support configuration via `.claudecli.yaml` and environment variables
- Follow secure coding practices, especially for shell/Python execution tools
- Design with modularity in mind for easy extension and plugin support
- Create comprehensive tests for all core functionality
- Implement proper error handling and user feedback
- Support both interactive REPL mode and single-command execution
- Include history navigation and multi-line input support
- Provide clear diff visualization before applying file changes

## CLI Interface Requirements

The tool should support:
```bash
# Interactive REPL mode (default)
claude-cli

# Single command execution
claude-cli "Refactor this function for better readability" --apply

# Model selection
claude-cli --model claude-3-sonnet

# Configuration
claude-cli --config /path/to/config.yaml

# Include specific files
claude-cli --include src/core.py tests/test_api.py

# Dry run mode
claude-cli "Remove unused imports" --dry-run

# Resume previous session
claude-cli --resume session1

# Debug mode
claude-cli --debug

# Run with feedback loop
claude-cli "Fix the test errors" --feedback test
```