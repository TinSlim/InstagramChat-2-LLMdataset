"""
Transformer for converting Instagram messages to LLM training format.
Uses the MessageParser to transform messages into training data.
"""
import json
from typing import Dict, List, Any, Optional
from parser import MessageParser


class MessageTransformer:
    """
    Transforms Instagram messages into LLM fine-tuning format.
    
    This class uses MessageParser to load and process messages, then
    formats them for LLM training (e.g., ChatML, conversational format).
    """
    
    def __init__(self, user_mapping_file: str = 'users.json'):
        """
        Initialize the transformer.
        
        Args:
            user_mapping_file: Path to users.json configuration file
        """
        self.user_mapping = self._load_user_mapping(user_mapping_file)
        self.parser = MessageParser(self.user_mapping)
        
    def _load_user_mapping(self, filepath: str) -> Dict[str, str]:
        """
        Load user mapping from JSON file.
        
        Args:
            filepath: Path to users.json file
            
        Returns:
            Dictionary mapping roles to Instagram usernames
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {filepath} not found. Using empty mapping.")
            return {}
        except json.JSONDecodeError:
            print(f"Warning: {filepath} is not valid JSON. Using empty mapping.")
            return {}
    
    def load_and_parse(self, messages_file: str, time_threshold_seconds: int = 30) -> None:
        """
        Load messages and parse into conversations.
        
        Args:
            messages_file: Path to messages.json file
            time_threshold_seconds: Time threshold for grouping messages (default: 30)
        """
        self.parser.load_messages(messages_file)
        self.parser.parse_conversations(time_threshold_seconds)
    
    def to_chatml_format(self) -> List[Dict[str, Any]]:
        """
        Convert conversations to ChatML format for LLM training.
        
        ChatML format example:
        {
            "messages": [
                {"role": "user", "content": "Hello!"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        }
        
        Returns:
            List of conversation objects in ChatML format
        """
        conversations = self.parser.get_conversations()
        chatml_data = []
        
        for conversation in conversations:
            messages = []
            for msg in conversation:
                # Map sender to role (customize as needed)
                role = self._map_sender_to_role(msg['sender'])
                messages.append({
                    'role': role,
                    'content': msg['content']
                })
            
            if messages:
                chatml_data.append({'messages': messages})
        
        return chatml_data
    
    def to_text_format(self, include_timestamp: bool = False) -> List[str]:
        """
        Convert conversations to simple text format.
        
        Args:
            include_timestamp: Whether to include timestamps in output
            
        Returns:
            List of formatted conversation strings
        """
        conversations = self.parser.get_conversations()
        text_data = []
        
        for i, conversation in enumerate(conversations):
            lines = [f"=== Conversation {i+1} ==="]
            for msg in conversation:
                timestamp_str = f"[{msg['timestamp']}] " if include_timestamp and msg.get('timestamp') else ""
                lines.append(f"{timestamp_str}{msg['sender']}: {msg['content']}")
            lines.append("")  # Empty line between conversations
            text_data.append('\n'.join(lines))
        
        return text_data
    
    def to_jsonl_format(self) -> List[str]:
        """
        Convert conversations to JSONL format (one JSON object per line).
        
        Each line contains a conversation in ChatML format.
        
        Returns:
            List of JSON strings, one per conversation
        """
        chatml_data = self.to_chatml_format()
        return [json.dumps(conv) for conv in chatml_data]
    
    def _map_sender_to_role(self, sender: str) -> str:
        """
        Map sender name/role to LLM role.
        
        Args:
            sender: Sender name or role
            
        Returns:
            LLM role ('user', 'assistant', or 'system')
        """
        # Default mapping: 'user' role stays as 'user', others become 'assistant'
        # Customize this based on your needs
        if sender.lower() == 'user':
            return 'user'
        else:
            return 'assistant'
    
    def save_to_file(self, output_file: str, output_format: str = 'chatml') -> None:
        """
        Save transformed data to file.
        
        Args:
            output_file: Path to output file
            output_format: Output format ('chatml', 'text', 'jsonl')
        """
        if output_format == 'chatml':
            data = self.to_chatml_format()
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif output_format == 'text':
            data = self.to_text_format()
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(data))
        elif output_format == 'jsonl':
            data = self.to_jsonl_format()
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(data))
        else:
            raise ValueError(f"Unsupported format: {output_format}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the transformed data.
        
        Returns:
            Dictionary containing statistics
        """
        return self.parser.get_statistics()


def main():
    """
    Example usage of the transformer.
    """
    # Initialize transformer with user mapping
    transformer = MessageTransformer('users.json')
    
    # Load and parse messages
    transformer.load_and_parse('data/messages.json', time_threshold_seconds=30)
    
    # Get statistics
    stats = transformer.get_statistics()
    print("Statistics:")
    print(f"  Total messages: {stats.get('total_messages', 0)}")
    print(f"  Messages with content: {stats.get('messages_with_content', 0)}")
    print(f"  Total conversations: {stats.get('total_conversations', 0)}")
    
    # Save in different formats
    transformer.save_to_file('output_chatml.json', output_format='chatml')
    transformer.save_to_file('output_text.txt', output_format='text')
    transformer.save_to_file('output.jsonl', output_format='jsonl')
    
    print("\nOutput files created:")
    print("  - output_chatml.json (ChatML format for LLM training)")
    print("  - output_text.txt (Human-readable text format)")
    print("  - output.jsonl (JSONL format)")


if __name__ == '__main__':
    main()
