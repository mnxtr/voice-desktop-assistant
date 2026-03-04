"""
Broadcaster utilities for sending status updates from Python backend to Electron frontend.

Provides convenient methods for broadcasting different types of messages.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional


class Broadcaster:
    """
    Helper class for broadcasting messages to WebSocket clients.

    Wraps the WebSocketServer's broadcast method with convenient
    message formatting for different event types.
    """

    def __init__(self, websocket_server):
        """
        Initialize broadcaster.

        Args:
            websocket_server: WebSocketServer instance
        """
        self.server = websocket_server
        self.logger = logging.getLogger(__name__)
        self._loop = None

    def _get_timestamp(self) -> float:
        """Get current timestamp."""
        return time.time()

    def _ensure_loop(self):
        """Ensure we have access to the event loop."""
        if self._loop is None:
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                # If called from non-async context, get the running loop
                self._loop = asyncio.get_running_loop()

    def _schedule_broadcast(self, message: Dict[str, Any]):
        """
        Schedule a broadcast to be sent asynchronously.

        This allows broadcasting from synchronous code (like Tkinter callbacks).

        Args:
            message: Message dictionary to broadcast
        """
        try:
            self._ensure_loop()
            # Schedule broadcast as a coroutine in the event loop
            asyncio.run_coroutine_threadsafe(self.server.broadcast(message), self._loop)
        except Exception as e:
            self.logger.error(f"Failed to schedule broadcast: {e}")

    async def broadcast_async(self, message: Dict[str, Any]):
        """
        Broadcast a message asynchronously.

        Use this when calling from async context.

        Args:
            message: Message dictionary to broadcast
        """
        await self.server.broadcast(message)

    def broadcast_status_update(self, state: str):
        """
        Broadcast status update.

        Args:
            state: Current state (idle, listening, processing, executing, error)
        """
        message = {
            "type": "status_update",
            "state": state,
            "timestamp": self._get_timestamp(),
        }
        self._schedule_broadcast(message)
        self.logger.debug(f"Broadcasting status: {state}")

    def broadcast_command_received(self, command: str):
        """
        Broadcast that a voice command was received.

        Args:
            command: The voice command text
        """
        message = {
            "type": "command_received",
            "command": command,
            "timestamp": self._get_timestamp(),
        }
        self._schedule_broadcast(message)
        self.logger.debug(f"Broadcasting command: {command}")

    def broadcast_workflow_plan(self, steps: List[Dict[str, Any]]):
        """
        Broadcast a multi-step workflow plan.

        Args:
            steps: List of workflow steps
                Each step: {'action': str, 'target': str, 'status': str, ...}
        """
        message = {
            "type": "workflow_plan",
            "steps": steps,
            "timestamp": self._get_timestamp(),
        }
        self._schedule_broadcast(message)
        self.logger.debug(f"Broadcasting workflow with {len(steps)} steps")

    def broadcast_step_executed(
        self, step_index: int, status: str, step_message: str = ""
    ):
        """
        Broadcast that a workflow step was executed.

        Args:
            step_index: Index of the step (0-based)
            status: Status of execution (completed, failed)
            step_message: Optional message about the step
        """
        message = {
            "type": "step_executed",
            "step_index": step_index,
            "status": status,
            "message": step_message,
            "timestamp": self._get_timestamp(),
        }
        self._schedule_broadcast(message)
        self.logger.debug(f"Broadcasting step {step_index}: {status}")

    def broadcast_error(self, error_message: str, error_type: str = "general"):
        """
        Broadcast an error.

        Args:
            error_message: Error description
            error_type: Type of error (general, llm, action, voice, etc.)
        """
        message = {
            "type": "error",
            "error_type": error_type,
            "message": error_message,
            "timestamp": self._get_timestamp(),
        }
        self._schedule_broadcast(message)
        self.logger.debug(f"Broadcasting error: {error_type} - {error_message}")

    def broadcast_config_updated(self, config_changes: Dict[str, Any]):
        """
        Broadcast that configuration was updated.

        Args:
            config_changes: Dictionary of changed configuration values
        """
        message = {
            "type": "config_updated",
            "changes": config_changes,
            "timestamp": self._get_timestamp(),
        }
        self._schedule_broadcast(message)
        self.logger.debug(f"Broadcasting config update: {list(config_changes.keys())}")

    def broadcast_gaze_position(self, x: int, y: int, confidence: float = 1.0):
        """
        Broadcast gaze tracking position.

        Args:
            x: Screen X coordinate
            y: Screen Y coordinate
            confidence: Confidence level (0-1)
        """
        message = {
            "type": "gaze_position",
            "x": x,
            "y": y,
            "confidence": confidence,
            "timestamp": self._get_timestamp(),
        }
        self._schedule_broadcast(message)
        # Don't log gaze positions (too frequent)

    def broadcast_llm_status(self, llm_type: str, available: bool, message: str = ""):
        """
        Broadcast LLM connection status.

        Args:
            llm_type: Type of LLM (gemini, ollama, hybrid)
            available: Whether LLM is available
            message: Optional status message
        """
        message_dict = {
            "type": "llm_status",
            "llm_type": llm_type,
            "available": available,
            "message": message,
            "timestamp": self._get_timestamp(),
        }
        self._schedule_broadcast(message_dict)
        self.logger.debug(
            f"Broadcasting LLM status: {llm_type} - {'available' if available else 'unavailable'}"
        )

    def broadcast_custom(self, message_type: str, data: Dict[str, Any]):
        """
        Broadcast a custom message.

        Args:
            message_type: Type identifier for the message
            data: Message data (will have type and timestamp added)
        """
        message = {"type": message_type, "timestamp": self._get_timestamp(), **data}
        self._schedule_broadcast(message)
        self.logger.debug(f"Broadcasting custom message: {message_type}")
