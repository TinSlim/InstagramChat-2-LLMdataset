#!/usr/bin/env python3
"""
Example usage script for Instagram Chat to LLM Dataset converter.

This script demonstrates how to use the parser and transformer to convert
Instagram messages into LLM training data.
"""
import sys
from src.transformer import MessageTransformer


def main():
    """
    Main function demonstrating usage.
    """
    print("=" * 70)
    print("Instagram Chat to LLM Dataset Converter")
    print("=" * 70)
    print()
    
    # Configuration
    users_file = 'users.json'
    messages_folder = 'data/other_person/'  # Folder containing multiple JSON files
    time_threshold = 30  # seconds
    
    #

    print("Configuration:")
    print(f"  Users mapping file: {users_file}")
    print(f"  Messages folder: {messages_folder}")
    print(f"  Time threshold for conversations: {time_threshold} seconds")
    print()
    
    # Initialize transformer
    print("Initializing transformer...")
    try:
        transformer = MessageTransformer(users_file)
    except Exception as e:
        print(f"Error loading user mapping: {e}")
        print("\nPlease ensure 'users.json' exists and is properly formatted.")
        print("Example users.json:")
        print("""{
  "user": "your_instagram_username",
  "other": "other_person_instagram_username",
}""")
        return 1
    
    # Load and parse messages
    print(f"Loading messages from {messages_folder}...")
    try:
        transformer.load_and_parse(
            messages_folder, 
            time_threshold_seconds=time_threshold,
            group_consecutive=True # <---- FLAG TO GROUP MESSAGES
        )
    except FileNotFoundError:
        print(f"Error: {messages_folder} not found!")
        print("\nPlease place your Instagram message JSON files in the data/ directory.")
        print("See data/messages.json.example for the expected format.")
        return 1
    except Exception as e:
        print(f"Error loading messages: {e}")
        return 1
    
    # Get and display statistics
    stats = transformer.get_statistics()
    print("\nParsing complete! Statistics:")
    print(f"  Total messages: {stats.get('total_messages', 0)}")
    print(f"  Messages with content: {stats.get('messages_with_content', 0)}")
    print(f"  Total conversations: {stats.get('total_conversations', 0)}")
    print(f"  Participants: {len(stats.get('participants', []))}")
    print()
    
    # Save outputs
    print("Generating output files...")
    
    output_files = {
        './export/output_chatml.json': 'chatml',
        './export/output_text.txt': 'text',
        './export/output.jsonl': 'jsonl'
    }
    
    for filename, format_type in output_files.items():
        try:
            transformer.save_to_file(filename, output_format=format_type)
            print(f"  ✓ Created {filename}")
        except Exception as e:
            print(f"  ✗ Error creating {filename}: {e}")
    
    print()
    print("=" * 70)
    print("Conversion complete!")
    print("=" * 70)
    print()
    print("Output files:")
    print("  • output_chatml.json - ChatML format for LLM fine-tuning")
    print("  • output_text.txt    - Human-readable text format")
    print("  • output.jsonl       - JSONL format (one conversation per line)")
    print()
    print("You can now use these files to train or fine-tune your LLM!")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
