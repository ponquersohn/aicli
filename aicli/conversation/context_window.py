"""
Context window management with intelligent token counting and auto-compaction.
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from .state import ConversationState, Message, MessageRole, TokenUsage

logger = logging.getLogger(__name__)


class TokenCounter(ABC):
    """Abstract token counter interface."""
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        pass
    
    @abstractmethod
    def count_message_tokens(self, message: Message) -> int:
        """Count tokens in a message."""
        pass


class SimpleTokenCounter(TokenCounter):
    """Simple token counter using word approximation."""
    
    def count_tokens(self, text: str) -> int:
        """Approximate token count using words * 1.3 ratio."""
        words = len(text.split())
        return int(words * 1.3)
    
    def count_message_tokens(self, message: Message) -> int:
        """Count tokens in message including metadata."""
        base_tokens = self.count_tokens(message.content)
        
        # Add tokens for role and metadata
        role_tokens = 2
        metadata_tokens = sum(
            self.count_tokens(str(v)) for v in message.metadata.values()
        ) if message.metadata else 0
        
        # Add tokens for tool calls if present
        tool_tokens = 0
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_tokens += self.count_tokens(str(tool_call))
        
        return base_tokens + role_tokens + metadata_tokens + tool_tokens


@dataclass
class CompactionStrategy:
    """Configuration for compaction strategy."""
    name: str
    priority: int
    preserve_recent_messages: int = 5
    preserve_system_messages: bool = True
    preserve_tool_results: bool = True
    max_compaction_ratio: float = 0.7


class CompactionResult:
    """Result of compaction operation."""
    
    def __init__(
        self,
        original_messages: List[Message],
        compacted_messages: List[Message],
        tokens_saved: int,
        strategy_used: str
    ):
        self.original_messages = original_messages
        self.compacted_messages = compacted_messages
        self.tokens_saved = tokens_saved
        self.strategy_used = strategy_used
        self.compaction_ratio = tokens_saved / sum(
            SimpleTokenCounter().count_message_tokens(msg) for msg in original_messages
        ) if original_messages else 0.0


class ConversationCompactor:
    """Handles conversation compaction using various strategies."""
    
    def __init__(self, token_counter: TokenCounter):
        self.token_counter = token_counter
        self.strategies = {
            'chronological': self._chronological_compaction,
            'semantic': self._semantic_compaction,
            'tool_context': self._tool_context_compaction
        }
    
    async def compact(
        self,
        messages: List[Message],
        target_tokens: int,
        strategy: CompactionStrategy
    ) -> CompactionResult:
        """Compact messages using specified strategy."""
        if strategy.name not in self.strategies:
            raise ValueError(f"Unknown compaction strategy: {strategy.name}")
        
        compaction_func = self.strategies[strategy.name]
        compacted_messages = await compaction_func(messages, target_tokens, strategy)
        
        original_tokens = sum(
            self.token_counter.count_message_tokens(msg) for msg in messages
        )
        compacted_tokens = sum(
            self.token_counter.count_message_tokens(msg) for msg in compacted_messages
        )
        
        return CompactionResult(
            original_messages=messages,
            compacted_messages=compacted_messages,
            tokens_saved=original_tokens - compacted_tokens,
            strategy_used=strategy.name
        )
    
    async def _chronological_compaction(
        self,
        messages: List[Message],
        target_tokens: int,
        strategy: CompactionStrategy
    ) -> List[Message]:
        """Remove oldest messages while preserving important ones."""
        if len(messages) <= strategy.preserve_recent_messages:
            return messages
        
        # Always preserve system messages if configured
        system_messages = [
            msg for msg in messages 
            if msg.role == MessageRole.SYSTEM and strategy.preserve_system_messages
        ]
        
        # Get recent messages to preserve
        recent_messages = messages[-strategy.preserve_recent_messages:]
        
        # Calculate remaining budget
        system_tokens = sum(
            self.token_counter.count_message_tokens(msg) for msg in system_messages
        )
        recent_tokens = sum(
            self.token_counter.count_message_tokens(msg) for msg in recent_messages
        )
        
        remaining_budget = target_tokens - system_tokens - recent_tokens
        
        if remaining_budget <= 0:
            return system_messages + recent_messages
        
        # Fill remaining budget with middle messages
        middle_messages = messages[len(system_messages):-strategy.preserve_recent_messages]
        selected_middle = []
        current_tokens = 0
        
        for msg in reversed(middle_messages):
            msg_tokens = self.token_counter.count_message_tokens(msg)
            if current_tokens + msg_tokens <= remaining_budget:
                selected_middle.insert(0, msg)
                current_tokens += msg_tokens
            else:
                break
        
        return system_messages + selected_middle + recent_messages
    
    async def _semantic_compaction(
        self,
        messages: List[Message],
        target_tokens: int,
        strategy: CompactionStrategy
    ) -> List[Message]:
        """Compact based on semantic importance (simplified version)."""
        # For now, fall back to chronological compaction
        # TODO: Implement actual semantic analysis
        return await self._chronological_compaction(messages, target_tokens, strategy)
    
    async def _tool_context_compaction(
        self,
        messages: List[Message],
        target_tokens: int,
        strategy: CompactionStrategy
    ) -> List[Message]:
        """Preserve tool-related messages and their context."""
        important_messages = []
        regular_messages = []
        
        for msg in messages:
            if (msg.role == MessageRole.TOOL or 
                msg.tool_calls or 
                (msg.role == MessageRole.SYSTEM and strategy.preserve_system_messages)):
                important_messages.append(msg)
            else:
                regular_messages.append(msg)
        
        # Calculate tokens for important messages
        important_tokens = sum(
            self.token_counter.count_message_tokens(msg) for msg in important_messages
        )
        
        if important_tokens >= target_tokens:
            # If important messages exceed target, use chronological on them
            return await self._chronological_compaction(
                important_messages, target_tokens, strategy
            )
        
        # Fill remaining space with regular messages
        remaining_budget = target_tokens - important_tokens
        selected_regular = []
        current_tokens = 0
        
        # Prefer recent regular messages
        for msg in reversed(regular_messages):
            msg_tokens = self.token_counter.count_message_tokens(msg)
            if current_tokens + msg_tokens <= remaining_budget:
                selected_regular.insert(0, msg)
                current_tokens += msg_tokens
            else:
                break
        
        # Merge and maintain chronological order
        all_selected = important_messages + selected_regular
        return sorted(all_selected, key=lambda msg: msg.timestamp)


class ContextWindowManager:
    """Manages context window with intelligent token counting and auto-compaction."""
    
    def __init__(
        self,
        token_counter: Optional[TokenCounter] = None,
        default_strategy: Optional[CompactionStrategy] = None
    ):
        self.token_counter = token_counter or SimpleTokenCounter()
        self.compactor = ConversationCompactor(self.token_counter)
        self.default_strategy = default_strategy or CompactionStrategy(
            name="chronological",
            priority=1,
            preserve_recent_messages=5,
            preserve_system_messages=True,
            preserve_tool_results=True,
            max_compaction_ratio=0.7
        )
        self._compaction_callbacks: List[Callable[[CompactionResult], None]] = []
    
    def add_compaction_callback(self, callback: Callable[[CompactionResult], None]) -> None:
        """Add callback to be called when compaction occurs."""
        self._compaction_callbacks.append(callback)
    
    def calculate_message_tokens(self, message: Message) -> int:
        """Calculate tokens for a message."""
        return self.token_counter.count_message_tokens(message)
    
    def calculate_conversation_tokens(self, messages: List[Message]) -> int:
        """Calculate total tokens for conversation."""
        return sum(self.calculate_message_tokens(msg) for msg in messages)
    
    async def check_and_compact(
        self,
        state: ConversationState,
        strategy: Optional[CompactionStrategy] = None
    ) -> Optional[Tuple[List[Message], int]]:
        """Check if compaction is needed and perform it if necessary."""
        if not state.context_window.needs_compaction:
            return None
        
        logger.info(
            f"Context window compaction triggered: {state.context_window.utilization:.2%} utilization"
        )
        
        return await self.compact_conversation(state, strategy)
    
    async def compact_conversation(
        self,
        state: ConversationState,
        strategy: Optional[CompactionStrategy] = None
    ) -> Tuple[List[Message], int]:
        """Force compaction of conversation."""
        strategy = strategy or self.default_strategy
        
        # Calculate target token count after compaction
        max_tokens = state.context_window.max_tokens
        target_tokens = int(max_tokens * (1 - strategy.max_compaction_ratio))
        
        logger.debug(f"Compacting conversation: target={target_tokens}, strategy={strategy.name}")
        
        compaction_result = await self.compactor.compact(
            state.messages,
            target_tokens,
            strategy
        )
        
        # Notify callbacks
        for callback in self._compaction_callbacks:
            try:
                callback(compaction_result)
            except Exception as e:
                logger.error(f"Error in compaction callback: {e}")
        
        logger.info(
            f"Compaction completed: {compaction_result.tokens_saved} tokens saved "
            f"({compaction_result.compaction_ratio:.2%} reduction)"
        )
        
        new_token_count = self.calculate_conversation_tokens(compaction_result.compacted_messages)
        return compaction_result.compacted_messages, new_token_count
    
    def estimate_tokens_for_text(self, text: str) -> int:
        """Estimate tokens for arbitrary text."""
        return self.token_counter.count_tokens(text)
    
    def get_utilization_info(self, state: ConversationState) -> Dict[str, Any]:
        """Get detailed utilization information."""
        context_window = state.context_window
        
        return {
            'current_tokens': context_window.current_tokens,
            'max_tokens': context_window.max_tokens,
            'utilization': context_window.utilization,
            'utilization_percent': f"{context_window.utilization:.2%}",
            'needs_compaction': context_window.needs_compaction,
            'threshold': context_window.compaction_threshold,
            'available_tokens': context_window.max_tokens - context_window.current_tokens,
            'message_count': len(state.messages)
        }