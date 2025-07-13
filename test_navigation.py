#!/usr/bin/env python3
"""Simple test script to verify input navigation functionality."""

import readline

def test_navigation():
    """Test command line navigation features."""
    print("🧪 Testing AICLI Navigation Features")
    print("=" * 50)
    
    # Configure readline
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind("set show-all-if-ambiguous on")
    readline.parse_and_bind("set completion-ignore-case on")
    readline.set_history_length(1000)
    
    # Add some test history
    test_commands = [
        "help me refactor this function",
        "show me the git status", 
        "explain this code to me",
        "find all Python files",
        "what does this error mean?"
    ]
    
    for cmd in test_commands:
        readline.add_history(cmd)
    
    print("\n✅ Navigation Features Available:")
    print("   • ↑/↓ arrows: Navigate command history")
    print("   • ←/→ arrows: Move cursor within line")
    print("   • Ctrl+←/→: Jump by words")
    print("   • Home/End: Jump to start/end of line")
    print("   • Tab: Command completion (if implemented)")
    
    print(f"\n📝 Current history ({readline.get_current_history_length()} items):")
    for i in range(readline.get_current_history_length()):
        item = readline.get_history_item(i + 1)
        print(f"   {i+1:2d}. {item}")
    
    print("\n🚀 Test Input (try using arrow keys for navigation):")
    print("   Type 'quit' to exit")
    
    while True:
        try:
            user_input = input("💬 Test › ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            print(f"   You entered: {user_input}")
            if user_input.strip():
                readline.add_history(user_input)
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    test_navigation()