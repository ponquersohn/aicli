"""
Immutable conversation state management following React patterns.
"""
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import uuid


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ConversationStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass(frozen=True)
class Message:
    """Immutable message structure."""
    id: str
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]
    tool_calls: Optional[List[Dict[str, Any]]] = None
    
    @classmethod
    def create(
        cls,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None
    ) -> "Message":
        """Create a new message with auto-generated ID and timestamp."""
        return cls(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {},
            tool_calls=tool_calls
        )


@dataclass(frozen=True)
class TokenUsage:
    """Token usage tracking."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    def add(self, other: "TokenUsage") -> "TokenUsage":
        """Add token usage from another instance."""
        return TokenUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens
        )


@dataclass(frozen=True)
class ContextWindow:
    """Context window state."""
    max_tokens: int
    current_tokens: int
    compaction_threshold: float = 0.85
    
    @property
    def utilization(self) -> float:
        """Get current utilization percentage."""
        return self.current_tokens / self.max_tokens if self.max_tokens > 0 else 0.0
    
    @property
    def needs_compaction(self) -> bool:
        """Check if compaction is needed."""
        return self.utilization >= self.compaction_threshold


@dataclass(frozen=True)
class ConversationState:
    """Immutable conversation state following React patterns."""
    id: str
    messages: List[Message]
    status: ConversationStatus
    context_window: ContextWindow
    token_usage: TokenUsage
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def create(
        cls,
        max_tokens: int = 4000,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "ConversationState":
        """Create a new conversation state."""
        now = datetime.now()
        return cls(
            id=str(uuid.uuid4()),
            messages=[],
            status=ConversationStatus.ACTIVE,
            context_window=ContextWindow(max_tokens=max_tokens, current_tokens=0),
            token_usage=TokenUsage(),
            metadata=metadata or {},
            created_at=now,
            updated_at=now
        )
    
    def add_message(self, message: Message, token_count: int = 0) -> "ConversationState":
        """Add a message and update token count."""
        new_messages = self.messages + [message]
        new_token_usage = self.token_usage.add(TokenUsage(total_tokens=token_count))
        new_context_window = replace(
            self.context_window,
            current_tokens=self.context_window.current_tokens + token_count
        )
        
        return replace(
            self,
            messages=new_messages,
            token_usage=new_token_usage,
            context_window=new_context_window,
            updated_at=datetime.now()
        )
    
    def update_status(self, status: ConversationStatus) -> "ConversationState":
        """Update conversation status."""
        return replace(
            self,
            status=status,
            updated_at=datetime.now()
        )
    
    def compact(self, new_messages: List[Message], new_token_count: int) -> "ConversationState":
        """Apply compaction with new message list and token count."""
        return replace(
            self,
            messages=new_messages,
            context_window=replace(
                self.context_window,
                current_tokens=new_token_count
            ),
            updated_at=datetime.now()
        )
    
    def update_metadata(self, key: str, value: Any) -> "ConversationState":
        """Update metadata with a new key-value pair."""
        new_metadata = {**self.metadata, key: value}
        return replace(
            self,
            metadata=new_metadata,
            updated_at=datetime.now()
        )