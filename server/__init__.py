"""
WebSocket server package for desktop_llm_assistant.

Provides real-time bidirectional communication between Python backend
and Electron frontend.
"""

from .websocket_server import WebSocketServer
from .message_handler import MessageHandler
from .broadcaster import Broadcaster

__all__ = ["WebSocketServer", "MessageHandler", "Broadcaster"]
