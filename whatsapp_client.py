"""
FT9 WhatsApp Integration - WhatsApp Business API Client
"""
import httpx
import logging
from typing import Dict, Any, Optional
from config import settings

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """Client for interacting with WhatsApp Business API"""
    
    def __init__(self):
        self.api_url = settings.whatsapp_api_url
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.access_token = settings.whatsapp_api_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def send_message(
        self, 
        to: str, 
        message: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Send a text message to a WhatsApp user
        
        Args:
            to: Phone number in international format (e.g., 5511999999999)
            message: Message text to send
            message_type: Type of message (text, image, document, etc.)
        
        Returns:
            API response dictionary
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": message_type,
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, 
                    json=payload, 
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                logger.info(f"Message sent successfully to {to}")
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending message: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise
    
    async def send_media(
        self,
        to: str,
        media_type: str,
        media_id: Optional[str] = None,
        media_link: Optional[str] = None,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send media (image, video, document, audio) to a WhatsApp user
        
        Args:
            to: Phone number in international format
            media_type: Type of media (image, video, document, audio)
            media_id: Media ID from uploaded file
            media_link: Direct link to media file
            caption: Optional caption for the media
        
        Returns:
            API response dictionary
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        media_object = {}
        if media_id:
            media_object["id"] = media_id
        elif media_link:
            media_object["link"] = media_link
        else:
            raise ValueError("Either media_id or media_link must be provided")
        
        if caption:
            media_object["caption"] = caption
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": media_type,
            media_type: media_object
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                logger.info(f"Media sent successfully to {to}")
                return response.json()
        except Exception as e:
            logger.error(f"Error sending media: {str(e)}")
            raise
    
    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Mark a message as read
        
        Args:
            message_id: WhatsApp message ID
        
        Returns:
            API response dictionary
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error marking message as read: {str(e)}")
            raise


# Global client instance
whatsapp_client = WhatsAppClient()
