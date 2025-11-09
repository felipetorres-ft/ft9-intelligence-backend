"""
FT9 WhatsApp Integration - Session Management Module
Manages conversation context and user sessions
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages user sessions and conversation history
    In-memory implementation (can be replaced with Redis for production)
    """
    
    def __init__(self, session_timeout_minutes: int = 30):
        self.sessions: Dict[str, Dict] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
    
    def get_session(self, user_phone: str) -> Dict:
        """
        Get or create a session for a user
        
        Args:
            user_phone: User's phone number
        
        Returns:
            Session dictionary
        """
        # Check if session exists and is not expired
        if user_phone in self.sessions:
            session = self.sessions[user_phone]
            last_activity = session.get("last_activity")
            
            if datetime.now() - last_activity < self.session_timeout:
                return session
            else:
                logger.info(f"Session expired for user {user_phone}")
                del self.sessions[user_phone]
        
        # Create new session
        session = {
            "user_phone": user_phone,
            "conversation_history": [],
            "user_data": {},
            "created_at": datetime.now(),
            "last_activity": datetime.now()
        }
        
        self.sessions[user_phone] = session
        logger.info(f"New session created for user {user_phone}")
        
        return session
    
    def add_message(
        self,
        user_phone: str,
        role: str,
        content: str
    ) -> None:
        """
        Add a message to the conversation history
        
        Args:
            user_phone: User's phone number
            role: Message role (user or assistant)
            content: Message content
        """
        session = self.get_session(user_phone)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        session["conversation_history"].append(message)
        session["last_activity"] = datetime.now()
        
        # Keep only last 10 messages to avoid context overflow
        if len(session["conversation_history"]) > 10:
            session["conversation_history"] = session["conversation_history"][-10:]
    
    def get_conversation_history(
        self,
        user_phone: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Get conversation history for a user
        
        Args:
            user_phone: User's phone number
            limit: Optional limit on number of messages
        
        Returns:
            List of message dictionaries
        """
        session = self.get_session(user_phone)
        history = session["conversation_history"]
        
        if limit:
            history = history[-limit:]
        
        # Return in OpenAI format (without timestamp)
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history
        ]
    
    def update_user_data(
        self,
        user_phone: str,
        data: Dict
    ) -> None:
        """
        Update user data in session
        
        Args:
            user_phone: User's phone number
            data: Dictionary with user data to update
        """
        session = self.get_session(user_phone)
        session["user_data"].update(data)
        session["last_activity"] = datetime.now()
    
    def get_user_data(self, user_phone: str) -> Dict:
        """
        Get user data from session
        
        Args:
            user_phone: User's phone number
        
        Returns:
            User data dictionary
        """
        session = self.get_session(user_phone)
        return session.get("user_data", {})
    
    def clear_session(self, user_phone: str) -> None:
        """
        Clear a user's session
        
        Args:
            user_phone: User's phone number
        """
        if user_phone in self.sessions:
            del self.sessions[user_phone]
            logger.info(f"Session cleared for user {user_phone}")
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len(self.sessions)


# Global session manager instance
session_manager = SessionManager()
