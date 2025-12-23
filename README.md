# InstagramChat-2-LLMdataset

Convert exported Instagram chats into datasets for training Large Language Models (LLMs).

## Overview

This tool processes Instagram message export files and transforms them into conversation datasets suitable for LLM fine-tuning. It supports user anonymization through role mapping and intelligent conversation grouping based on message timing.

## Features

- **User Role Mapping**: Replace Instagram usernames with role labels (e.g., "user", "girlfriend", "friend1")
- **Conversation Grouping**: Automatically groups messages into conversations (messages within 30 seconds are grouped together)
- **Multiple Output Formats**:
  - ChatML format (for LLM training)
  - Plain text format (human-readable)
  - JSONL format (one conversation per line)

## Setup

1. Export your Instagram messages (Settings → Your activity → Download your information)
2. Place the exported `messages.json` file in the `data/` directory
3. Configure `users.json` with your user mappings

### Configure users.json

Edit `users.json` to map role names to Instagram usernames. A template is provided in `users.json.template`:

```json
{
  "user": "your_instagram_username",
  "friend1": "friend1_instagram_username"
}
```

**Note:** The `users.json` file comes pre-configured with example mappings that work with `data/messages.json.example`. Update it with your actual Instagram usernames when using your own data.

## Usage

### Basic Usage

```python
from transformer import MessageTransformer

# Initialize transformer
transformer = MessageTransformer('users.json')

# Load and parse messages (30 seconds threshold for conversation grouping)
transformer.load_and_parse('data/messages.json', time_threshold_seconds=30)

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
1. Load `users.json` and `data/messages.json`
2. Parse conversations (grouping messages within 30 seconds)
3. Display statistics about your messages
4. Generate three output files:
   - `output_chatml.json` - ChatML format for LLM training
   - `output_text.txt` - Human-readable text format
   - `output.jsonl` - JSONL format

**Alternative (Direct Transformer):**
```bash
python transformer.py
```

This will run the transformer's main function with the same functionality.

### Using the Parser Directly

```python
from parser import MessageParser

# Initialize with user mapping
user_mapping = {
    "user": "john_doe",
    "girlfriend": "jane_smith"
}
parser = MessageParser(user_mapping)

# Load messages
parser.load_messages('data/messages.json')

# Parse into conversations (30 second threshold)
conversations = parser.parse_conversations(time_threshold_seconds=30)

# Access conversations
for conv in conversations:
    for msg in conv:
        print(f"{msg['sender']}: {msg['content']}")
```

## File Structure

```
InstagramChat-2-LLMdataset/
├── data/
│   ├── messages.json          # Your Instagram message export (place here)
│   └── messages.json.example  # Example format
├── parser.py                  # Message parser class
├── transformer.py             # Message transformer class
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

Messages are grouped into conversations based on time proximity. By default, messages sent within 30 seconds of each other are considered part of the same conversation. You can adjust this threshold:

```python
transformer.load_and_parse('data/messages.json', time_threshold_seconds=60)  # 60 seconds
```

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

## License

See LICENSE file for details.
