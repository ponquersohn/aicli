"""
Conversation management module with sophisticated state management,
context window handling, and intelligent compaction.

Phase 1 Implementation (COMPLETED):
- Immutable state management following React patterns
- State manager with dispatch/reducer pattern and middleware
- Context window management with intelligent compaction

Future phases will include:
- Real-time streaming with concurrent tool execution
- Error recovery and graceful degradation
- Multi-level caching and session persistence
"""

from .state import (
    ConversationState,
    Message,
    MessageRole,
    ConversationStatus,
    TokenUsage,
    ContextWindow
)

from .manager import (
    StateManager,
    StateManagerFactory,
    StateAction,
    ConversationReducer,
    LoggingMiddleware,
    ValidationMiddleware
)

from .context_window import (
    ContextWindowManager,
    CompactionStrategy,
    CompactionResult,
    TokenCounter,
    SimpleTokenCounter,
    ConversationCompactor
)

from .core import (
    ConversationManager,
    ConversationManagerFactory
)

__all__ = [
    # State management
    'ConversationState',
    'Message',
    'MessageRole',
    'ConversationStatus',
    'TokenUsage',
    'ContextWindow',
    
    # State manager
    'StateManager',
    'StateManagerFactory',
    'StateAction',
    'ConversationReducer',
    'LoggingMiddleware',
    'ValidationMiddleware',
    
    # Context window management
    'ContextWindowManager',
    'CompactionStrategy',
    'CompactionResult',
    'TokenCounter',
    'SimpleTokenCounter',
    'ConversationCompactor',
    
    # High-level interface
    'ConversationManager',
    'ConversationManagerFactory'
]