"""
Parser for Instagram messages.json export files.
Loads, processes, and groups messages into conversations.
"""
import json
from typing import Dict, List, Any
from datetime import datetime


class MessageParser:
    """
    Parser for Instagram exported messages.
    
    This class loads Instagram messages from JSON, replaces usernames with
    role labels, and groups messages into conversations based on time proximity.
    """
    
    def __init__(self, user_mapping: Dict[str, str] = None):
        """
        Initialize the parser.
        
        Args:
            user_mapping: Dictionary mapping role names (e.g., 'user', 'girlfriend')
                         to Instagram usernames
        """
        self.user_mapping = user_mapping or {}
        self.messages_data = None
        self.conversations = []
        
    def load_messages(self, filepath: str) -> None:
        """
        Load messages from JSON file.
        
        Args:
            filepath: Path to the messages.json file
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            self.messages_data = json.load(f)
    
    def _replace_username(self, username: str) -> str:
        """
        Replace Instagram username with role label.
        
        Args:
            username: Original Instagram username
            
        Returns:
            Role label if found in mapping, otherwise original username
        """
        for role, instagram_user in self.user_mapping.items():
            if instagram_user.lower() == username.lower():
                return role
        return username
    
    def _should_group_messages(self, msg1: Dict[str, Any], msg2: Dict[str, Any], 
                               time_threshold_seconds: int = 30) -> bool:
        """
        Determine if two messages should be grouped in the same conversation.
        
        Args:
            msg1: First message
            msg2: Second message
            time_threshold_seconds: Maximum time difference in seconds (default: 30)
            
        Returns:
            True if messages should be grouped, False otherwise
        """
        # Get timestamps in milliseconds
        ts1 = msg1.get('timestamp_ms', 0)
        ts2 = msg2.get('timestamp_ms', 0)
        
        # Calculate time difference in seconds
        time_diff = abs(ts2 - ts1) / 1000.0
        
        return time_diff <= time_threshold_seconds
    
    def parse_conversations(self, time_threshold_seconds: int = 30) -> List[List[Dict[str, Any]]]:
        """
        Parse messages and group them into conversations.
        
        Messages are grouped into the same conversation if they are within
        the specified time threshold from each other.
        
        Args:
            time_threshold_seconds: Maximum time difference in seconds for grouping (default: 30)
            
        Returns:
            List of conversations, where each conversation is a list of messages
        """
        if not self.messages_data:
            return []
        
        messages = self.messages_data.get('messages', [])
        
        # Sort messages by timestamp (oldest first for chronological order)
        sorted_messages = sorted(messages, key=lambda x: x.get('timestamp_ms', 0))
        
        if not sorted_messages:
            return []
        
        conversations = []
        current_conversation = []
        
        for i, message in enumerate(sorted_messages):
            # Skip messages without content
            if 'content' not in message:
                continue
            
            # Create processed message
            processed_msg = {
                'sender': self._replace_username(message.get('sender_name', '')),
                'content': message.get('content', ''),
                'timestamp_ms': message.get('timestamp_ms', 0),
                'timestamp': datetime.fromtimestamp(
                    message.get('timestamp_ms', 0) / 1000.0
                ).isoformat() if message.get('timestamp_ms') else None
            }
            
            # First message starts a new conversation
            if not current_conversation:
                current_conversation.append(processed_msg)
            else:
                # Check if this message should be in the same conversation
                last_msg = current_conversation[-1]
                if self._should_group_messages(last_msg, processed_msg, time_threshold_seconds):
                    current_conversation.append(processed_msg)
                else:
                    # Start a new conversation
                    if current_conversation:
                        conversations.append(current_conversation)
                    current_conversation = [processed_msg]
        
        # Add the last conversation
        if current_conversation:
            conversations.append(current_conversation)
        
        self.conversations = conversations
        return conversations
    
    def get_conversations(self) -> List[List[Dict[str, Any]]]:
        """
        Get parsed conversations.
        
        Returns:
            List of conversations
        """
        return self.conversations
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the parsed messages.
        
        Returns:
            Dictionary containing statistics
        """
        if not self.messages_data:
            return {}
        
        total_messages = len(self.messages_data.get('messages', []))
        messages_with_content = sum(
            1 for msg in self.messages_data.get('messages', []) 
            if 'content' in msg
        )
        
        return {
            'total_messages': total_messages,
            'messages_with_content': messages_with_content,
            'total_conversations': len(self.conversations),
            'participants': self.messages_data.get('participants', [])
        }
