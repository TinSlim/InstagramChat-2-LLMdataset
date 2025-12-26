"""
Parser for Instagram messages.json export files.
Loads, processes, and groups messages into conversations.
"""
import json
import os
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
        Load messages from JSON file or folder containing multiple JSON files.
        
        Args:
            filepath: Path to a messages.json file or folder containing multiple .json files
        """
        # Check if filepath is a directory
        if os.path.isdir(filepath):
            # Load all JSON files from the directory
            all_messages = []
            json_files = [f for f in os.listdir(filepath) if f.endswith('.json')]
            
            if not json_files:
                raise FileNotFoundError(f"No JSON files found in {filepath}")
            
            for json_file in sorted(json_files):
                file_path = os.path.join(filepath, json_file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_data = json.load(f)
                        # Fix Instagram's encoding issue
                        file_data = self._fix_encoding(file_data)
                        # Handle both single message objects and arrays of messages
                        if isinstance(file_data, dict) and 'messages' in file_data:
                            all_messages.extend(file_data['messages'])
                        elif isinstance(file_data, list):
                            all_messages.extend(file_data)
                        else:
                            # Assume it's a single message object
                            all_messages.append(file_data)
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Warning: Error loading {json_file}: {e}")
                    continue
            
            # Create a combined messages structure
            self.messages_data = {'messages': all_messages}
        else:
            # Load single file
            with open(filepath, 'r', encoding='utf-8') as f:
                self.messages_data = json.load(f)
                self.messages_data = self._fix_encoding(self.messages_data)
    
    def _fix_encoding(self, obj):
        """
        Fix Instagram's encoding issue where UTF-8 bytes are incorrectly decoded as latin1.
        
        Args:
            obj: Object to fix (can be dict, list, str, or other types)
            
        Returns:
            Object with fixed encoding
        """
        if isinstance(obj, str):
            # Try to fix the encoding by encoding as latin1 and decoding as utf-8
            try:
                return obj.encode('latin1').decode('utf-8')
            except (UnicodeDecodeError, UnicodeEncodeError):
                return obj
        elif isinstance(obj, dict):
            return {key: self._fix_encoding(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._fix_encoding(item) for item in obj]
        else:
            return obj
    
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
                               time_threshold_seconds: int = 30,
                               conversation: List[Dict[str, Any]] = None) -> bool:
        """
        Determine if two messages should be grouped in the same conversation.
        
        Args:
            msg1: First message
            msg2: Second message
            time_threshold_seconds: Maximum time difference in seconds (default: 30)
            conversation: Current conversation to check for interchange
            
        Returns:
            True if messages should be grouped, False otherwise
        """
        # Get timestamps in milliseconds
        ts1 = msg1.get('timestamp_ms', 0)
        ts2 = msg2.get('timestamp_ms', 0)
        
        # Calculate time difference in seconds
        time_diff = abs(ts2 - ts1) / 1000.0
        
        # Check if there's an interchange (at least 2 different senders)
        has_interchange = False
        if conversation:
            senders = set(msg['sender'] for msg in conversation)
            has_interchange = len(senders) > 1
        
        # Use extended threshold (60 seconds) if there's no interchange yet
        threshold = time_threshold_seconds if has_interchange else 60
        
        return time_diff <= threshold
    
    def parse_conversations(self, time_threshold_seconds: int = 30, 
                          interchange_only: bool = True,
                          max_messages: int = 10,
                          group_consecutive: bool = False) -> List[List[Dict[str, Any]]]:
        """
        Parse messages and group them into conversations.
        
        Messages are grouped into the same conversation if they are within
        the specified time threshold from each other. Uses an extended threshold
        (60 seconds) until there's an interchange between different senders.
        
        Args:
            time_threshold_seconds: Maximum time difference in seconds for grouping (default: 30)
            interchange_only: If True, only include conversations with at least 2 different senders (default: True)
            max_messages: Maximum number of messages per conversation (default: 10)
            group_consecutive: If True, group consecutive messages from the same sender (default: False)
            
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
            
            # Create processed message with attachment handling
            sender = self._replace_username(message.get('sender_name', ''))
            content_raw = message.get('content', '')
            share_text = None
            if isinstance(message.get('share'), dict):
                share_text = message['share'].get('share_text')

            # Replace Instagram's generic attachment placeholder with a readable marker
            if content_raw.strip().lower() == 'enviaste un archivo adjunto.':
                if share_text and share_text.strip():
                    content = f"[image from {sender}: {share_text.strip()}]"
                else:
                    content = f"[image from {sender}]"
            else:
                content = content_raw

            processed_msg = {
                'sender': sender,
                'content': content,
                'timestamp_ms': message.get('timestamp_ms', 0),
                'timestamp': datetime.fromtimestamp(
                    message.get('timestamp_ms', 0) / 1000.0
                ).isoformat() if message.get('timestamp_ms') else None
            }
            
            # First message starts a new conversation
            if not current_conversation:
                current_conversation.append(processed_msg)
            else:
                # Check if we've reached the maximum messages limit
                if len(current_conversation) >= max_messages:
                    # Save current conversation if it meets the criteria
                    if self._is_valid_conversation(current_conversation, interchange_only):
                        conversations.append(current_conversation)
                    current_conversation = [processed_msg]
                else:
                    # Check if this message should be in the same conversation
                    last_msg = current_conversation[-1]
                    if self._should_group_messages(last_msg, processed_msg, time_threshold_seconds, current_conversation):
                        current_conversation.append(processed_msg)
                    else:
                        # Save current conversation if it meets the criteria
                        if current_conversation:
                            if self._is_valid_conversation(current_conversation, interchange_only):
                                conversations.append(current_conversation)
                        current_conversation = [processed_msg]
        
        # Add the last conversation if it meets the criteria
        if current_conversation:
            if self._is_valid_conversation(current_conversation, interchange_only):
                conversations.append(current_conversation)
        
        # Group consecutive messages from the same sender if requested
        if group_consecutive:
            conversations = [self._group_consecutive_messages(conv) for conv in conversations]
        
        self.conversations = conversations
        return conversations
    
    def _is_valid_conversation(self, conversation: List[Dict[str, Any]], 
                              interchange_only: bool) -> bool:
        """
        Check if a conversation is valid based on interchange criteria.
        
        Args:
            conversation: List of messages in the conversation
            interchange_only: If True, require at least 2 different senders
            
        Returns:
            True if the conversation is valid, False otherwise
        """
        if not interchange_only:
            return True
        
        # Check if there are at least 2 different senders
        senders = set(msg['sender'] for msg in conversation)
        return len(senders) >= 2
    
    def _group_consecutive_messages(self, conversation: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Group consecutive messages from the same sender into single messages.
        
        Args:
            conversation: List of messages in the conversation
            
        Returns:
            List of messages with consecutive messages from same sender grouped
        """
        if not conversation:
            return conversation
        
        grouped = []
        current_group = None
        
        for msg in conversation:
            if current_group is None:
                # Start first group
                current_group = msg.copy()
            elif current_group['sender'] == msg['sender']:
                # Same sender - append content to current group
                current_group['content'] += ', ' + msg['content'] # TODO caracter to separate messages
                # Update timestamp to the latest one
                current_group['timestamp_ms'] = msg['timestamp_ms']
                current_group['timestamp'] = msg['timestamp']
            else:
                # Different sender - save current group and start new one
                grouped.append(current_group)
                current_group = msg.copy()
        
        # Add the last group
        if current_group is not None:
            grouped.append(current_group)
        
        return grouped
    
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
