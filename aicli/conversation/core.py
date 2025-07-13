"""
Core conversation management integration.
"""
import asyncio
import logging
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime

from .state import ConversationState, Message, MessageRole, ConversationStatus
from .manager import StateManager, StateManagerFactory, StateAction
from .context_window import ContextWindowManager, CompactionStrategy, CompactionResult

logger = logging.getLogger(__name__)


class ConversationManager:
    """High-level conversation management orchestrator."""
    
    def __init__(
        self,
        max_tokens: int = 4000,
        compaction_strategy: Optional[CompactionStrategy] = None,
        state_manager: Optional[StateManager] = None,
        context_window_manager: Optional[ContextWindowManager] = None
    ):
        # Initialize state
        initial_state = ConversationState.create(
            max_tokens=max_tokens,
            metadata={'created_by': 'ConversationManager'}
        )
        
        # Initialize managers
        self.state_manager = state_manager or StateManagerFactory.create_default(initial_state)
        self.context_window_manager = context_window_manager or ContextWindowManager(
            default_strategy=compaction_strategy
        )
        
        # Set up compaction callback
        self.context_window_manager.add_compaction_callback(self._on_compaction)
        
        # Subscribe to state changes for automatic compaction
        self._unsubscribe = self.state_manager.subscribe(self._on_state_change)
    
    @property
    def current_state(self) -> ConversationState:
        """Get current conversation state."""
        return self.state_manager.state
    
    async def add_message(
        self,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None
    ) -> Message:
        """Add a message to the conversation."""
        message = Message.create(
            role=role,
            content=content,
            metadata=metadata,
            tool_calls=tool_calls
        )
        
        token_count = self.context_window_manager.calculate_message_tokens(message)
        
        action = StateAction(
            type="ADD_MESSAGE",
            payload={
                "message": message,
                "token_count": token_count
            }
        )
        
        await self.state_manager.dispatch(action)
        return message
    
    async def add_user_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Add a user message."""
        return await self.add_message(MessageRole.USER, content, metadata)
    
    async def add_assistant_message(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None
    ) -> Message:
        """Add an assistant message."""
        return await self.add_message(MessageRole.ASSISTANT, content, metadata, tool_calls)
    
    async def add_system_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Add a system message."""
        return await self.add_message(MessageRole.SYSTEM, content, metadata)
    
    async def add_tool_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Add a tool message."""
        return await self.add_message(MessageRole.TOOL, content, metadata)
    
    async def update_status(self, status: ConversationStatus) -> None:
        """Update conversation status."""
        action = StateAction(
            type="UPDATE_STATUS",
            payload={"status": status}
        )
        await self.state_manager.dispatch(action)
    
    async def update_metadata(self, key: str, value: Any) -> None:
        """Update conversation metadata."""
        action = StateAction(
            type="UPDATE_METADATA",
            payload={"key": key, "value": value}
        )
        await self.state_manager.dispatch(action)
    
    async def force_compaction(self, strategy: Optional[CompactionStrategy] = None) -> CompactionResult:
        """Force conversation compaction."""
        messages, token_count = await self.context_window_manager.compact_conversation(
            self.current_state,
            strategy
        )
        
        action = StateAction(
            type="COMPACT_CONVERSATION",
            payload={
                "messages": messages,
                "token_count": token_count
            }
        )
        
        await self.state_manager.dispatch(action)
        
        # Return the compaction result
        return CompactionResult(
            original_messages=self.current_state.messages,
            compacted_messages=messages,
            tokens_saved=self.current_state.context_window.current_tokens - token_count,
            strategy_used=strategy.name if strategy else "default"
        )
    
    def get_messages(self, role: Optional[MessageRole] = None) -> List[Message]:
        """Get messages, optionally filtered by role."""
        messages = self.current_state.messages
        if role:
            return [msg for msg in messages if msg.role == role]
        return messages
    
    def get_recent_messages(self, count: int) -> List[Message]:
        """Get the most recent messages."""
        return self.current_state.messages[-count:] if count > 0 else []
    
    def get_utilization_info(self) -> Dict[str, Any]:
        """Get context window utilization information."""
        return self.context_window_manager.get_utilization_info(self.current_state)
    
    def estimate_tokens_for_text(self, text: str) -> int:
        """Estimate tokens for text."""
        return self.context_window_manager.estimate_tokens_for_text(text)
    
    def subscribe_to_changes(self, callback: Callable[[ConversationState], None]) -> Callable[[], None]:
        """Subscribe to conversation state changes."""
        return self.state_manager.subscribe(callback)
    
    async def _on_state_change(self, state: ConversationState) -> None:
        """Handle state changes and trigger auto-compaction if needed."""
        try:
            compaction_result = await self.context_window_manager.check_and_compact(state)
            
            if compaction_result:
                messages, token_count = compaction_result
                action = StateAction(
                    type="COMPACT_CONVERSATION",
                    payload={
                        "messages": messages,
                        "token_count": token_count
                    }
                )
                await self.state_manager.dispatch(action)
        
        except Exception as e:
            logger.error(f"Error in auto-compaction: {e}")
    
    def _on_compaction(self, result: CompactionResult) -> None:
        """Handle compaction events."""
        logger.info(
            f"Conversation compacted: {len(result.original_messages)} -> "
            f"{len(result.compacted_messages)} messages, "
            f"{result.tokens_saved} tokens saved"
        )
    
    def close(self) -> None:
        """Clean up resources."""
        if self._unsubscribe:
            self._unsubscribe()
        self.state_manager.close()


class ConversationManagerFactory:
    """Factory for creating configured conversation managers."""
    
    @staticmethod
    def create_default(max_tokens: int = 4000) -> ConversationManager:
        """Create conversation manager with default configuration."""
        return ConversationManager(max_tokens=max_tokens)
    
    @staticmethod
    def create_with_strategy(
        max_tokens: int = 4000,
        strategy_name: str = "chronological",
        preserve_recent: int = 5
    ) -> ConversationManager:
        """Create conversation manager with custom compaction strategy."""
        strategy = CompactionStrategy(
            name=strategy_name,
            priority=1,
            preserve_recent_messages=preserve_recent,
            preserve_system_messages=True,
            preserve_tool_results=True,
            max_compaction_ratio=0.7
        )
        
        return ConversationManager(
            max_tokens=max_tokens,
            compaction_strategy=strategy
        )
    
    @staticmethod
    def create_minimal(max_tokens: int = 2000) -> ConversationManager:
        """Create minimal conversation manager for testing."""
        initial_state = ConversationState.create(max_tokens=max_tokens)
        state_manager = StateManagerFactory.create_minimal(initial_state)
        
        return ConversationManager(
            max_tokens=max_tokens,
            state_manager=state_manager
        )