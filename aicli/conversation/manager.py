"""
State management with dispatch/reducer pattern and middleware pipeline.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Protocol, Type, TypeVar, Union
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

from .state import ConversationState, Message, ConversationStatus, MessageRole, TokenUsage

logger = logging.getLogger(__name__)

T = TypeVar('T')


class Action(Protocol):
    """Action protocol for type safety."""
    type: str
    payload: Optional[Dict[str, Any]] = None


@dataclass
class StateAction:
    """Standard action implementation."""
    type: str
    payload: Optional[Dict[str, Any]] = None


class Middleware(ABC):
    """Abstract middleware class."""
    
    @abstractmethod
    async def __call__(
        self,
        action: Action,
        state: ConversationState,
        next_middleware: Callable[[Action], ConversationState]
    ) -> ConversationState:
        """Process action with middleware logic."""
        pass


class Reducer(ABC):
    """Abstract reducer class."""
    
    @abstractmethod
    def __call__(self, state: ConversationState, action: Action) -> ConversationState:
        """Reduce state based on action."""
        pass


class ConversationReducer(Reducer):
    """Main conversation reducer."""
    
    def __call__(self, state: ConversationState, action: Action) -> ConversationState:
        """Reduce conversation state based on action type."""
        action_type = action.type
        payload = action.payload or {}
        
        if action_type == "ADD_MESSAGE":
            message = payload.get("message")
            token_count = payload.get("token_count", 0)
            if message:
                return state.add_message(message, token_count)
        
        elif action_type == "UPDATE_STATUS":
            status = payload.get("status")
            if status:
                return state.update_status(status)
        
        elif action_type == "COMPACT_CONVERSATION":
            new_messages = payload.get("messages", [])
            new_token_count = payload.get("token_count", 0)
            return state.compact(new_messages, new_token_count)
        
        elif action_type == "UPDATE_METADATA":
            key = payload.get("key")
            value = payload.get("value")
            if key is not None:
                return state.update_metadata(key, value)
        
        elif action_type == "UPDATE_CONTEXT_WINDOW":
            max_tokens = payload.get("max_tokens")
            if max_tokens:
                from dataclasses import replace
                new_context_window = replace(
                    state.context_window,
                    max_tokens=max_tokens
                )
                return replace(state, context_window=new_context_window)
        
        return state


class LoggingMiddleware(Middleware):
    """Middleware for logging actions and state changes."""
    
    async def __call__(
        self,
        action: Action,
        state: ConversationState,
        next_middleware: Callable[[Action], ConversationState]
    ) -> ConversationState:
        """Log action and state changes."""
        logger.debug(f"Action dispatched: {action.type}")
        logger.debug(f"Current state: messages={len(state.messages)}, tokens={state.context_window.current_tokens}")
        
        new_state = await next_middleware(action)
        
        logger.debug(f"New state: messages={len(new_state.messages)}, tokens={new_state.context_window.current_tokens}")
        return new_state


class ValidationMiddleware(Middleware):
    """Middleware for validating actions and state transitions."""
    
    async def __call__(
        self,
        action: Action,
        state: ConversationState,
        next_middleware: Callable[[Action], ConversationState]
    ) -> ConversationState:
        """Validate action before processing."""
        if not self._validate_action(action, state):
            logger.warning(f"Invalid action: {action.type}")
            return state
        
        new_state = await next_middleware(action)
        
        if not self._validate_state(new_state):
            logger.error("Invalid state transition detected")
            return state
        
        return new_state
    
    def _validate_action(self, action: Action, state: ConversationState) -> bool:
        """Validate action against current state."""
        if action.type == "ADD_MESSAGE":
            payload = action.payload or {}
            message = payload.get("message")
            return isinstance(message, Message)
        
        elif action.type == "UPDATE_STATUS":
            payload = action.payload or {}
            status = payload.get("status")
            return isinstance(status, ConversationStatus)
        
        return True
    
    def _validate_state(self, state: ConversationState) -> bool:
        """Validate state consistency."""
        if state.context_window.current_tokens < 0:
            return False
        if len(state.messages) < 0:
            return False
        return True


class StateManager:
    """Central state manager with dispatch/reducer pattern."""
    
    def __init__(
        self,
        initial_state: ConversationState,
        reducer: Reducer,
        middleware: Optional[List[Middleware]] = None
    ):
        self._state = initial_state
        self._reducer = reducer
        self._middleware = middleware or []
        self._subscribers: List[Callable[[ConversationState], None]] = []
        self._executor = ThreadPoolExecutor(max_workers=2)
    
    @property
    def state(self) -> ConversationState:
        """Get current state."""
        return self._state
    
    def subscribe(self, callback: Callable[[ConversationState], None]) -> Callable[[], None]:
        """Subscribe to state changes. Returns unsubscribe function."""
        self._subscribers.append(callback)
        
        def unsubscribe():
            if callback in self._subscribers:
                self._subscribers.remove(callback)
        
        return unsubscribe
    
    async def dispatch(self, action: Action) -> ConversationState:
        """Dispatch action through middleware pipeline."""
        try:
            new_state = await self._apply_middleware(action, self._state)
            
            if new_state != self._state:
                old_state = self._state
                self._state = new_state
                await self._notify_subscribers(old_state, new_state)
            
            return self._state
        
        except Exception as e:
            logger.error(f"Error dispatching action {action.type}: {e}")
            return self._state
    
    async def _apply_middleware(self, action: Action, state: ConversationState) -> ConversationState:
        """Apply middleware pipeline."""
        if not self._middleware:
            return self._reducer(state, action)
        
        middleware_chain = self._build_middleware_chain()
        return await middleware_chain(action)
    
    def _build_middleware_chain(self) -> Callable[[Action], ConversationState]:
        """Build middleware chain with reducer at the end."""
        def final_reducer(action: Action) -> ConversationState:
            return self._reducer(self._state, action)
        
        chain = final_reducer
        
        for middleware in reversed(self._middleware):
            previous_chain = chain
            
            async def create_middleware_wrapper(mw, prev_chain):
                async def wrapper(action: Action) -> ConversationState:
                    async def next_fn(action: Action) -> ConversationState:
                        if asyncio.iscoroutinefunction(prev_chain):
                            return await prev_chain(action)
                        else:
                            return prev_chain(action)
                    return await mw(action, self._state, next_fn)
                return wrapper
            
            chain = await create_middleware_wrapper(middleware, previous_chain)
        
        return chain
    
    async def _notify_subscribers(
        self,
        old_state: ConversationState,
        new_state: ConversationState
    ) -> None:
        """Notify all subscribers of state change."""
        for subscriber in self._subscribers:
            try:
                if asyncio.iscoroutinefunction(subscriber):
                    await subscriber(new_state)
                else:
                    await asyncio.get_event_loop().run_in_executor(
                        self._executor,
                        subscriber,
                        new_state
                    )
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")
    
    def reset(self, new_state: ConversationState) -> None:
        """Reset state to a new state."""
        self._state = new_state
    
    def close(self) -> None:
        """Clean up resources."""
        self._executor.shutdown(wait=True)


class StateManagerFactory:
    """Factory for creating configured state managers."""
    
    @staticmethod
    def create_default(initial_state: ConversationState) -> StateManager:
        """Create state manager with default configuration."""
        middleware = [
            ValidationMiddleware(),
            LoggingMiddleware()
        ]
        
        return StateManager(
            initial_state=initial_state,
            reducer=ConversationReducer(),
            middleware=middleware
        )
    
    @staticmethod
    def create_minimal(initial_state: ConversationState) -> StateManager:
        """Create minimal state manager without middleware."""
        return StateManager(
            initial_state=initial_state,
            reducer=ConversationReducer()
        )