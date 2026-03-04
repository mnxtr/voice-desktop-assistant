"""
Message handler for processing commands from Electron frontend.

Routes incoming WebSocket messages to appropriate handlers in the main application.
"""

import logging
from typing import Dict, Any, Callable, Optional
from websockets.server import WebSocketServerProtocol
import json


class MessageHandler:
    """
    Handles incoming WebSocket messages from Electron clients.

    Routes messages to registered handlers based on message type.
    """

    def __init__(self):
        """Initialize message handler."""
        self.logger = logging.getLogger(__name__)
        self._handlers: Dict[str, Callable] = {}
        self.logger.info("MessageHandler initialized")

    def register_handler(self, message_type: str, handler: Callable):
        """
        Register a handler for a specific message type.

        Args:
            message_type: Type of message (e.g., 'toggle_listening')
            handler: Callback function to handle the message
        """
        self._handlers[message_type] = handler
        self.logger.debug(f"Registered handler for message type: {message_type}")

    async def handle_message(
        self, data: Dict[str, Any], websocket: WebSocketServerProtocol
    ):
        """
        Process an incoming message and route to appropriate handler.

        Args:
            data: Parsed JSON message
            websocket: WebSocket connection (for sending responses)
        """
        message_type = data.get("type")

        if not message_type:
            self.logger.warning(f"Message missing 'type' field: {data}")
            await self._send_error(websocket, "Message must include 'type' field")
            return

        # Route to handler
        handler = self._handlers.get(message_type)
        if handler:
            try:
                self.logger.debug(f"Routing message type '{message_type}' to handler")
                # Call handler - it may be sync or async
                result = handler(data)

                # If handler is async, await it
                if hasattr(result, "__await__"):
                    await result

                # Send acknowledgment
                await self._send_ack(websocket, message_type, data)
            except Exception as e:
                self.logger.error(f"Error in handler for '{message_type}': {e}")
                await self._send_error(
                    websocket, f"Error processing {message_type}: {str(e)}"
                )
        else:
            self.logger.warning(
                f"No handler registered for message type: {message_type}"
            )
            await self._send_error(websocket, f"Unknown message type: {message_type}")

    async def _send_ack(
        self,
        websocket: WebSocketServerProtocol,
        message_type: str,
        original_data: Dict[str, Any],
    ):
        """
        Send acknowledgment to client.

        Args:
            websocket: WebSocket connection
            message_type: Original message type
            original_data: Original message data
        """
        try:
            await websocket.send(
                json.dumps(
                    {
                        "type": "ack",
                        "original_type": message_type,
                        "message": f"Processed {message_type}",
                        "data": original_data,
                    }
                )
            )
        except Exception as e:
            self.logger.error(f"Failed to send acknowledgment: {e}")

    async def _send_error(self, websocket: WebSocketServerProtocol, error_message: str):
        """
        Send error response to client.

        Args:
            websocket: WebSocket connection
            error_message: Error description
        """
        try:
            await websocket.send(
                json.dumps({"type": "error", "message": error_message})
            )
        except Exception as e:
            self.logger.error(f"Failed to send error message: {e}")


# Default handler implementations for common message types
class DefaultHandlers:
    """
    Default handler implementations that can be used by the main application.

    These serve as templates - the main application should provide actual implementations.
    """

    def __init__(self, app_instance):
        """
        Initialize default handlers.

        Args:
            app_instance: Reference to main application instance (VoiceDesktopAssistant)
        """
        self.app = app_instance
        self.logger = logging.getLogger(__name__)

    def handle_toggle_listening(self, data: Dict[str, Any]):
        """
        Handle toggle_listening command.

        Expected data: {'type': 'toggle_listening', 'enabled': true/false}
        """
        enabled = data.get("enabled")
        if enabled is None:
            self.logger.warning("toggle_listening missing 'enabled' field")
            return

        self.logger.info(f"Toggle listening: {enabled}")

        # Queue action for main thread
        if hasattr(self.app, "_toggle_listening"):
            self.app._toggle_listening(enabled)
        else:
            self.logger.warning("App does not implement _toggle_listening")

    def handle_toggle_gaze(self, data: Dict[str, Any]):
        """
        Handle toggle_gaze command.

        Expected data: {'type': 'toggle_gaze', 'enabled': true/false}
        """
        enabled = data.get("enabled")
        if enabled is None:
            self.logger.warning("toggle_gaze missing 'enabled' field")
            return

        self.logger.info(f"Toggle gaze tracking: {enabled}")

        # Queue action for main thread
        if hasattr(self.app, "_toggle_gaze_tracking"):
            self.app._toggle_gaze_tracking(enabled)
        else:
            self.logger.warning("App does not implement _toggle_gaze_tracking")

    def handle_show_grid(self, data: Dict[str, Any]):
        """
        Handle show_grid command.

        Expected data: {'type': 'show_grid'}
        """
        self.logger.info("Show grid")

        # Queue action for main thread
        if hasattr(self.app, "_show_grid"):
            self.app._show_grid()
        else:
            self.logger.warning("App does not implement _show_grid")

    def handle_hide_grid(self, data: Dict[str, Any]):
        """
        Handle hide_grid command.

        Expected data: {'type': 'hide_grid'}
        """
        self.logger.info("Hide grid")

        # Queue action for main thread
        if hasattr(self.app, "_hide_grid"):
            self.app._hide_grid()
        else:
            self.logger.warning("App does not implement _hide_grid")

    def handle_update_config(self, data: Dict[str, Any]):
        """
        Handle update_config command.

        Expected data: {'type': 'update_config', 'config': {...}}
        """
        config_updates = data.get("config")
        if not config_updates:
            self.logger.warning("update_config missing 'config' field")
            return

        self.logger.info(f"Update config: {config_updates}")

        # Queue action for main thread
        if hasattr(self.app, "_update_config"):
            self.app._update_config(config_updates)
        else:
            self.logger.warning("App does not implement _update_config")

    def handle_correct_interpretation(self, data: Dict[str, Any]):
        """
        Handle correct_interpretation command (for fine-tuning).

        Expected data: {
            'type': 'correct_interpretation',
            'original_command': 'open chrome',
            'correct_action': {...}
        }
        """
        original_command = data.get("original_command")
        correct_action = data.get("correct_action")

        if not original_command or not correct_action:
            self.logger.warning("correct_interpretation missing required fields")
            return

        self.logger.info(f"Correction: '{original_command}' -> {correct_action}")

        # Queue action for main thread (will be implemented in Phase 4)
        if hasattr(self.app, "_log_correction"):
            self.app._log_correction(original_command, correct_action)
        else:
            self.logger.warning(
                "App does not implement _log_correction (Phase 4 feature)"
            )
