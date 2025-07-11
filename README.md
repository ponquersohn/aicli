# 🤖 AICLI - Beautiful Conversational Code Assistant

A powerful, open-source CLI tool inspired by Claude Code, built with LangChain for conversational code assistance. AICLI provides an elegant terminal interface for AI-powered development workflows.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## ✨ Features

### 🎨 Beautiful Interface
- **Rich Terminal UI** - Elegant styling with syntax highlighting and markdown rendering
- **Interactive REPL** - Smooth conversational interface with command history
- **Live Progress** - Beautiful spinners and progress indicators
- **Customizable Themes** - Claude Code-inspired color schemes

### 🧠 AI-Powered Development
- **Multi-LLM Support** - OpenAI, Anthropic, Fireworks, Together AI, and Ollama
- **Context Awareness** - Automatically understands your project structure
- **Conversational Interface** - Natural language queries for code assistance
- **Session Memory** - Persistent conversations across sessions

### 🔧 Developer Tools
- **File Operations** - Read, search, and modify files with AI assistance
- **Git Integration** - Status, diff, blame, and history analysis
- **Python REPL** - Safe code execution with sandboxing
- **Test Runner** - Automated testing with result analysis
- **Shell Commands** - Whitelisted shell operations for safety

### 🛡️ Security & Safety
- **Sandboxed Execution** - Safe Python code execution
- **Command Whitelisting** - Only approved shell commands allowed
- **File Backups** - Automatic backups before modifications
- **Confirmation Prompts** - Preview changes before applying

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/aicli.git
cd aicli

# Install dependencies
pip install -e .

# Set up your API keys
cp .env.example .env
# Edit .env and add your API keys
```

### Configuration

Create a `.env` file with your API keys:

```bash
# Anthropic (recommended)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# OpenAI (alternative)
OPENAI_API_KEY=sk-your-openai-key-here

# Set default provider
DEFAULT_LLM_PROVIDER=anthropic
```

### Basic Usage

```bash
# Interactive mode (default)
aicli

# Single command
aicli "Refactor this function for better readability"

# With specific model
aicli --model claude-3-sonnet "Fix the bug in auth.py"

# Include specific files
aicli --include src/main.py "Add error handling"

# Dry run mode (preview changes)
aicli "Remove unused imports" --dry-run
```

## 📖 Usage Examples

### Interactive Session
```bash
$ aicli
╔═══════════════════════════════════════╗
║                                       ║
║            🤖 AICLI v0.1.0           ║
║                                       ║
║    Conversational Code Assistant      ║
║         Powered by LangChain          ║
║                                       ║
╚═══════════════════════════════════════╝

💡 Welcome to AICLI!
Type your questions in natural language
Use '/help' for commands or '/exit' to quit

💬 You › What files are in this project?
🤖 AICLI › 

I can see this is a Python project with the following structure:

- **aicli/** - Main package with CLI, agent, and tools
- **tests/** - Unit tests
- **examples/** - Usage examples
- **pyproject.toml** - Project configuration
- **.env.example** - Environment configuration template

Would you like me to analyze any specific files or help with development tasks?
```

### Code Analysis
```bash
💬 You › Analyze the main CLI file and suggest improvements

🤖 AICLI › I've analyzed `aicli/cli/main.py`. Here are my suggestions:

## Strengths
✅ Excellent use of Rich for beautiful terminal output
✅ Comprehensive CLI argument handling with Typer
✅ Good error handling and user feedback

## Improvement Suggestions

1. **Add input validation**
   ```python
   def validate_file_paths(paths: List[str]) -> List[Path]:
       return [Path(p) for p in paths if Path(p).exists()]
   ```

2. **Implement graceful shutdown**
   ```python
   signal.signal(signal.SIGINT, handle_shutdown)
   ```

Would you like me to implement these improvements?
```

### File Operations
```bash
💬 You › Show me the Git status and recent changes

🤖 AICLI › ## Git Status

**Modified files:**
- `aicli/cli/main.py` (12 lines changed)
- `README.md` (5 lines added)

**Recent commits:**
- `feat: Add beautiful CLI interface` (2 hours ago)
- `docs: Update README with examples` (3 hours ago)

Would you like me to show the specific changes or help with committing?
```

## 🔧 Configuration

AICLI supports multiple configuration methods:

### Environment Variables
```bash
export ANTHROPIC_API_KEY="your-key"
export DEFAULT_LLM_PROVIDER="anthropic"
export LOG_LEVEL="INFO"
```

### YAML Configuration
Create `.claudecli.yaml`:
```yaml
llm:
  provider: anthropic
  model: claude-3-sonnet-20240229
  temperature: 0.7

security:
  enable_shell_tools: false
  confirm_destructive: true

ui:
  theme: aicli
  syntax_highlighting: true
```

### CLI Options
```bash
aicli --provider anthropic --model claude-3-haiku --debug
```

## 🛠️ Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest

# Format code
black aicli/
ruff check aicli/

# Type checking
mypy aicli/
```

### Project Structure

```bash
aicli/
├── aicli/                     # 📦 Main package
│   ├── __init__.py
│   ├── cli.py                 # Typer/Rich CLI entrypoint
│   ├── agent.py               # LangChain agent logic
│   ├── config.py              # Config loading (YAML/env/CLI)
│   ├── context/
│   │   ├── __init__.py
│   │   ├── file_loader.py     # Loads files for context
│   │   ├── summarizer.py      # Embedding/summarization support
│   │   └── memory.py          # Memory management for sessions
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── python_tool.py     # Executes Python code
│   │   ├── git_tool.py        # Git integration
│   │   ├── shell_tool.py      # Optional shell tool
│   │   └── test_runner.py     # Test execution & feedback
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── model_factory.py   # Loads models via LangChain
│   │   └── prompt_templates.py # Prompt definitions for code edit, test gen, etc.
│   ├── editor/
│   │   ├── __init__.py
│   │   ├── code_editor.py     # Applies code edits to files
│   │   └── diff_renderer.py   # Shows diff before apply
│   └── utils/
│       ├── __init__.py
│       ├── logger.py          # Unified logging w/ levels
│       ├── paths.py           # Path helpers
│       └── shell.py           # Subprocess helpers
│
├── sessions/                  # 🧠 Stored memory/sessions (optional)
│   └── session1.json
│
├── examples/                  # 📎 Example CLI interactions and test projects
│   └── sample_project/
│
├── tests/                     # ✅ Unit + integration tests
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_agent.py
│   ├── test_config.py
│   └── ...
│
├── .env                       # 🔑 API keys (ignored)
├── .gitignore
├── .pre-commit-config.yaml    # 🧹 Optional lint/format hooks
├── pyproject.toml             # 📦 Project metadata, deps
├── requirements.txt
├── README.md                  # 📖 Overview and usage
└── cli.py                     # 🔧 Entrypoint (wraps `aicli.cli`)
```

---

## 🧭 Key Concepts

| Folder         | Purpose                                            |
| -------------- | -------------------------------------------------- |
| `aicli/cli.py` | CLI entrypoint using Typer or Click                |
| `agent.py`     | LangChain agent logic (actions, tools, memory)     |
| `context/`     | File scanning, embedding, and memory handling      |
| `llm/`         | Model backend handling and prompt management       |
| `tools/`       | LangChain tools like Python REPL, Git, Test Runner |
| `editor/`      | Code edit, diff preview, and application           |
| `utils/`       | Logging, path handling, subprocess helpers         |
| `tests/`       | Standard unit tests for each module                |
| `sessions/`    | Optional persisted conversation memory             |
| `examples/`    | Sample project to simulate usage/testing           |

---

Let me know if you'd like a GitHub-ready scaffold (with some boilerplate files already filled out).

