"""
Simple tests for the parser and transformer.
"""
import json
import os
import sys
from parser import MessageParser
from transformer import MessageTransformer


def test_parser():
    """Test the MessageParser class."""
    print("Testing MessageParser...")
    
    # Create test user mapping
    user_mapping = {
        "user": "User Name",
        "friend": "Other Person"
    }
    
    # Initialize parser
    parser = MessageParser(user_mapping)
    
    # Load example messages
    parser.load_messages('data/messages.json.example')
    
    # Parse conversations
    conversations = parser.parse_conversations(time_threshold_seconds=30)
    
    print(f"  ✓ Loaded messages successfully")
    print(f"  ✓ Found {len(conversations)} conversation(s)")
    
    # Check conversation grouping
    # Based on the example, messages 1-3 are within 30 seconds (conversation 1)
    # Message 4 is 70 seconds after message 3 (conversation 2)
    assert len(conversations) == 2, f"Expected 2 conversations, got {len(conversations)}"
    print(f"  ✓ Conversation grouping works correctly (30 second threshold)")
    
    # Check user replacement
    assert conversations[0][0]['sender'] == 'user', "User replacement failed"
    assert conversations[0][1]['sender'] == 'friend', "User replacement failed"
    print(f"  ✓ User replacement works correctly")
    
    # Get statistics
    stats = parser.get_statistics()
    print(f"  ✓ Statistics: {stats['total_messages']} messages, {stats['total_conversations']} conversations")
    
    print("✅ MessageParser tests passed!\n")
    return True


def test_transformer():
    """Test the MessageTransformer class."""
    print("Testing MessageTransformer...")
    
    # Create test users.json
    test_users = {
        "user": "User Name",
        "friend": "Other Person"
    }
    
    with open('test_users.json', 'w') as f:
        json.dump(test_users, f)
    
    # Initialize transformer
    transformer = MessageTransformer('test_users.json')
    
    # Load and parse
    transformer.load_and_parse('data/messages.json.example', time_threshold_seconds=30)
    print(f"  ✓ Loaded and parsed messages")
    
    # Test ChatML format
    chatml_data = transformer.to_chatml_format()
    assert len(chatml_data) == 2, "Should have 2 conversations"
    assert 'messages' in chatml_data[0], "ChatML format should have 'messages' key"
    print(f"  ✓ ChatML format generation works")
    
    # Test text format
    text_data = transformer.to_text_format()
    assert len(text_data) == 2, "Should have 2 conversations in text format"
    print(f"  ✓ Text format generation works")
    
    # Test JSONL format
    jsonl_data = transformer.to_jsonl_format()
    assert len(jsonl_data) == 2, "Should have 2 conversations in JSONL format"
    # Verify each line is valid JSON
    for line in jsonl_data:
        json.loads(line)  # Should not raise exception
    print(f"  ✓ JSONL format generation works")
    
    # Test file output
    transformer.save_to_file('test_output.json', format='chatml')
    assert os.path.exists('test_output.json'), "Output file should be created"
    print(f"  ✓ File output works")
    
    # Cleanup test files
    os.remove('test_users.json')
    os.remove('test_output.json')
    
    print("✅ MessageTransformer tests passed!\n")
    return True


def test_conversation_grouping():
    """Test conversation grouping with different time thresholds."""
    print("Testing conversation grouping with different thresholds...")
    
    user_mapping = {"user": "User Name", "friend": "Other Person"}
    
    # Test with 60 second threshold - all messages should be in one conversation
    parser = MessageParser(user_mapping)
    parser.load_messages('data/messages.json.example')
    conversations_60s = parser.parse_conversations(time_threshold_seconds=60)
    
    # Messages are at: 0s, 15s, 20s, 90s
    # With 60s threshold: 0-15-20 grouped, then 90s is separate (70s gap from 20s)
    assert len(conversations_60s) == 2, f"Expected 2 conversations with 60s threshold, got {len(conversations_60s)}"
    print(f"  ✓ 60 second threshold: {len(conversations_60s)} conversations")
    
    # Test with 100 second threshold - all messages should be in one conversation
    parser2 = MessageParser(user_mapping)
    parser2.load_messages('data/messages.json.example')
    conversations_100s = parser2.parse_conversations(time_threshold_seconds=100)
    
    assert len(conversations_100s) == 1, f"Expected 1 conversation with 100s threshold, got {len(conversations_100s)}"
    assert len(conversations_100s[0]) == 4, f"Expected 4 messages in conversation"
    print(f"  ✓ 100 second threshold: {len(conversations_100s)} conversation(s) with {len(conversations_100s[0])} messages")
    
    # Test with 10 second threshold - more fragmented conversations
    parser3 = MessageParser(user_mapping)
    parser3.load_messages('data/messages.json.example')
    conversations_10s = parser3.parse_conversations(time_threshold_seconds=10)
    
    # With 10s: 0s alone, 15-20 grouped (5s apart), 90s alone
    assert len(conversations_10s) == 3, f"Expected 3 conversations with 10s threshold, got {len(conversations_10s)}"
    print(f"  ✓ 10 second threshold: {len(conversations_10s)} conversations")
    
    print("✅ Conversation grouping tests passed!\n")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Running tests for Instagram Chat to LLM Dataset")
    print("=" * 60 + "\n")
    
    try:
        test_parser()
        test_transformer()
        test_conversation_grouping()
        
        print("=" * 60)
        print("✅ All tests passed successfully!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
