# InstagramChat-2-LLMdataset

Convert exported Instagram chats into datasets for training Large Language Models (LLMs).

## Overview

This tool processes Instagram message export files and transforms them into conversation datasets suitable for LLM fine-tuning. It supports user anonymization through role mapping, intelligent conversation grouping based on message timing, and automatic handling of multimedia content.

## Features

- **User Role Mapping**: Replace Instagram usernames with role labels (e.g., "user", "friend", "girlfriend")
- **Smart Conversation Grouping**: 
  - Uses 30-second threshold for grouped messages (configurable)
  - Uses extended 60-second threshold until different senders interact
  - Filters single-speaker conversations by default
- **Consecutive Message Grouping**: Optionally groups consecutive messages from the same sender with newline separators
- **Message Limits**: Set maximum messages per conversation (default: 10) - longer conversations are split
- **Image Handling**: Automatically replaces Instagram attachment placeholders with descriptive markers
- **Encoding Fix**: Handles Instagram's UTF-8 encoding issues automatically
- **Multiple Output Formats**:
  - ChatML format (for LLM training)
  - Plain text format (human-readable)
  - JSONL format (one conversation per line)
- **Batch Processing**: Load and process multiple JSON files from a folder

## Setup

1. Export your Instagram messages (Settings → Your activity → Download your information)
2. Place the exported message JSON files in the `data/{other_username}` directory (can be a single file or a folder with multiple files)
3. Configure `users.json` with your user mappings

### Configure users.json

Edit `users.json` to map role names to Instagram usernames. A template is provided in `users.json.template`:

```json
{
  "user": "your_instagram_username",
  "friend": "other_person"
}
```

**Note:** The `users.json` file comes pre-configured with example mappings that work with `data/other_person/` folder. Update it with your actual Instagram usernames when using your own data.

## Usage

### Basic Usage

```python
from src.transformer import MessageTransformer

# Initialize transformer
transformer = MessageTransformer('users.json')

# Load and parse messages with all options
transformer.load_and_parse(
    'data/other_person/',           # File or folder path
    time_threshold_seconds=30,      # Time threshold for grouping
    interchange_only=True,          # Only conversations with multiple speakers
    max_messages=10,                # Max messages per conversation
    group_consecutive=True          # Group consecutive messages from same sender
)

# Save in ChatML format for LLM training
transformer.save_to_file('output_chatml.json', output_format='chatml')

# Get statistics
stats = transformer.get_statistics()
print(f"Total conversations: {stats['total_conversations']}")
```

### Command Line Usage

**Quick Start:**
```bash
python example.py
```

This interactive script will:
1. Load `users.json` and all messages from `data/other_person/`
2. Parse conversations with smart grouping
3. Display statistics about your messages
4. Generate three output files in `export/` directory:
   - `output_chatml.json` - ChatML format for LLM training
   - `output_text.txt` - Human-readable text format
   - `output.jsonl` - JSONL format

**Alternative (Direct Transformer):**
```bash
python src/transformer.py
```

This will run the transformer's main function with the same functionality.

### Using the Parser Directly

```python
from src.parser import MessageParser

# Initialize with user mapping
user_mapping = {
    "user": "john_doe",
    "friend": "other_person"
}
parser = MessageParser(user_mapping)

# Load messages from single file or folder
parser.load_messages('data/other_person/')

# Parse into conversations with all options
conversations = parser.parse_conversations(
    time_threshold_seconds=30,
    interchange_only=True,
    max_messages=10,
    group_consecutive=True
)

# Access conversations
for conv in conversations:
    for msg in conv:
        print(f"{msg['sender']}: {msg['content']}")
```

## File Structure

```
InstagramChat-2-LLMdataset/
├── data/
│   ├── other_person/                   # Folder with Instagram message exports
│   │   ├── message_1.json
│   │   ├── . . .
│   │   └── message_60.json
├── export/                    # Output directory (created after running)
│   ├── output_chatml.json
│   ├── output_text.txt
│   └── output.jsonl
├── src/
│   ├── parser.py              # Message parser class
│   ├── transformer.py         # Message transformer class
│   └── __pycache__/
├── example.py                 # Example usage script
├── test.py                    # Test suite
├── users.json                 # User role mapping configuration
├── users.json.template        # Template for user role mapping
└── README.md
```

## Output Formats

### ChatML Format
```json
[
  {
    "messages": [
      {"role": "user", "content": "Hello!"},
      {"role": "assistant", "content": "Hi there!"}
    ]
  }
]
```

### Text Format
```
=== Conversation 1 ===
user: Hello!
friend: Hi there!

=== Conversation 2 ===
...
```

### JSONL Format
```
{"messages": [{"role": "user", "content": "Hello!"}, {"role": "assistant", "content": "Hi!"}]}
{"messages": [{"role": "user", "content": "How are you?"}, {"role": "assistant", "content": "Good!"}]}
```

## Conversation Grouping

Messages are grouped into conversations based on multiple criteria:

### Time-based Grouping
- **Default threshold: 30 seconds** for regular message grouping
- **Extended threshold: 60 seconds** before interchange between different senders is detected
- Once senders alternate, the 30-second threshold applies

### Filtering Options
- **`interchange_only=True` (default)**: Only includes conversations where at least 2 different senders have messages
- **`interchange_only=False`**: Includes all conversations, even if only one person speaks

### Message Limits
- **`max_messages=10` (default)**: Conversations are split if they exceed this limit
- Prevents overly long single conversations in training data

### Consecutive Message Grouping
- **`group_consecutive=True`**: Consecutive messages from the same sender are grouped into one message separated by newlines
- **`group_consecutive=False` (default)**: Each message is kept separate

Example with grouping enabled:
```
friend: Message 1
friend: Message 2
friend: Message 3
```

Becomes:
```
friend: Message 1
Message 2
Message 3
```

## Image Handling

Instagram attachment placeholders are automatically converted:
- Generic placeholder "Enviaste un archivo adjunto." → `[image from sender]`
- With share text → `[image from sender: description]`

Example:
```json
{
  "content": "[image from friend: Beautiful sunset photo]"
}
```

## Requirements

- Python 3.7+
- No external dependencies (uses only standard library: json, os, datetime)

## Troubleshooting

### JSONDecodeError when loading files
- Ensure your JSON files are valid (use a JSON validator)
- Check that files are encoded in UTF-8
- The parser automatically handles Instagram's encoding issues

### Missing or incorrect role mapping
- Verify `users.json` exists and contains valid Instagram usernames
- Run the script to see which participants are in your messages
- Update the mapping as needed

### Empty output
- Check that `interchange_only` is set correctly (True requires messages from 2+ people)
- Verify the time threshold isn't too strict (try `time_threshold_seconds=60`)
- Ensure messages have content (some messages might be reactions or calls only)
