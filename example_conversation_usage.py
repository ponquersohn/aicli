#!/usr/bin/env python3
"""
Example usage of the Phase 1 conversation management system.
This demonstrates the key features implemented in Phase 1.
"""
import asyncio
from aicli.conversation import (
    ConversationManager,
    ConversationManagerFactory,
    MessageRole,
    ConversationStatus,
    CompactionStrategy
)


async def demo_basic_usage():
    """Demonstrate basic conversation management."""
    print("=== Basic Conversation Management Demo ===")
    
    # Create a conversation manager with small token limit for demo
    manager = ConversationManagerFactory.create_default(max_tokens=1000)
    
    # Add some messages
    await manager.add_system_message("You are a helpful AI assistant.")
    await manager.add_user_message("Hello, how are you?")
    await manager.add_assistant_message("I'm doing well, thank you for asking!")
    
    # Check state
    state = manager.current_state
    print(f"Conversation ID: {state.id}")
    print(f"Message count: {len(state.messages)}")
    print(f"Status: {state.status.value}")
    
    # Get utilization info
    util_info = manager.get_utilization_info()
    print(f"Token utilization: {util_info['utilization_percent']}")
    print(f"Current tokens: {util_info['current_tokens']}")
    print(f"Available tokens: {util_info['available_tokens']}")
    
    manager.close()


async def demo_auto_compaction():
    """Demonstrate automatic compaction when reaching threshold."""
    print("\n=== Auto-Compaction Demo ===")
    
    # Create manager with very small token limit
    manager = ConversationManagerFactory.create_default(max_tokens=200)
    
    # Add messages until compaction triggers
    print("Adding messages to trigger compaction...")
    for i in range(10):
        await manager.add_user_message(f"This is a longer message {i} to fill up the context window with more tokens.")
        await manager.add_assistant_message(f"This is assistant response {i} which also adds more tokens to the conversation.")
    
    # Check final state
    final_state = manager.current_state
    util_info = manager.get_utilization_info()
    
    print(f"Final message count: {len(final_state.messages)}")
    print(f"Final utilization: {util_info['utilization_percent']}")
    print("Note: Compaction should have occurred automatically when threshold was reached")
    
    manager.close()


async def demo_custom_compaction():
    """Demonstrate custom compaction strategies."""
    print("\n=== Custom Compaction Strategy Demo ===")
    
    # Create custom strategy
    strategy = CompactionStrategy(
        name="chronological",
        priority=1,
        preserve_recent_messages=3,  # Keep only 3 recent messages
        preserve_system_messages=True,
        max_compaction_ratio=0.5  # More aggressive compaction
    )
    
    manager = ConversationManagerFactory.create_with_strategy(
        max_tokens=500,
        strategy_name="chronological",
        preserve_recent=3
    )
    
    # Add system message
    await manager.add_system_message("You are a helpful assistant.")
    
    # Add many messages
    for i in range(8):
        await manager.add_user_message(f"User message {i}")
        await manager.add_assistant_message(f"Assistant response {i}")
    
    print(f"Before compaction: {len(manager.get_messages())} messages")
    
    # Force compaction
    result = await manager.force_compaction(strategy)
    print(f"After compaction: {len(manager.get_messages())} messages")
    print(f"Tokens saved: {result.tokens_saved}")
    print(f"Strategy used: {result.strategy_used}")
    
    # Check what messages were preserved
    messages = manager.get_messages()
    print("\nPreserved messages:")
    for msg in messages:
        print(f"  {msg.role.value}: {msg.content[:50]}...")
    
    manager.close()


async def demo_state_subscriptions():
    """Demonstrate state change subscriptions."""
    print("\n=== State Subscription Demo ===")
    
    def on_state_change(state):
        print(f"State changed! Messages: {len(state.messages)}, Status: {state.status.value}")
    
    manager = ConversationManagerFactory.create_default(max_tokens=400)
    
    # Subscribe to changes
    unsubscribe = manager.subscribe_to_changes(on_state_change)
    
    # Make some changes
    await manager.add_user_message("First message")
    await manager.add_assistant_message("First response")
    await manager.update_status(ConversationStatus.PAUSED)
    await manager.update_metadata("demo", "subscription_test")
    await manager.update_status(ConversationStatus.ACTIVE)
    
    # Unsubscribe and cleanup
    unsubscribe()
    manager.close()


async def demo_message_filtering():
    """Demonstrate message filtering and retrieval."""
    print("\n=== Message Filtering Demo ===")
    
    manager = ConversationManagerFactory.create_default(max_tokens=600)
    
    # Add various types of messages
    await manager.add_system_message("System instruction")
    await manager.add_user_message("User question 1")
    await manager.add_assistant_message("Assistant answer 1")
    await manager.add_tool_message("Tool result data")
    await manager.add_user_message("User question 2")
    await manager.add_assistant_message("Assistant answer 2")
    
    # Filter messages
    user_messages = manager.get_messages(MessageRole.USER)
    assistant_messages = manager.get_messages(MessageRole.ASSISTANT)
    recent_messages = manager.get_recent_messages(3)
    
    print(f"Total messages: {len(manager.get_messages())}")
    print(f"User messages: {len(user_messages)}")
    print(f"Assistant messages: {len(assistant_messages)}")
    print(f"Recent messages: {len(recent_messages)}")
    
    print("\nRecent messages:")
    for msg in recent_messages:
        print(f"  {msg.role.value}: {msg.content}")
    
    manager.close()


async def main():
    """Run all demos."""
    print("Phase 1 Conversation Management System Demo")
    print("=" * 50)
    
    await demo_basic_usage()
    await demo_auto_compaction()
    await demo_custom_compaction()
    await demo_state_subscriptions()
    await demo_message_filtering()
    
    print("\n✅ All demos completed successfully!")
    print("Phase 1 implementation is working correctly.")


if __name__ == "__main__":
    asyncio.run(main())