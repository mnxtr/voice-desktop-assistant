"""
WebSocket server for real-time communication between Python backend and Electron frontend.

Uses asyncio and websockets library for asynchronous bidirectional communication.
"""

import asyncio
import json
import logging
from typing import Set, Optional, Callable, Any, Dict
import websockets
from websockets.server import WebSocketServerProtocol


class WebSocketServer:
    """
    Async WebSocket server for desktop_llm_assistant.

    Handles client connections, message routing, and broadcasting status updates
    to all connected Electron clients.
    """

    def __init__(self, host: str = "localhost", port: int = 8765):
        """
        Initialize WebSocket server.

        Args:
            host: Server host address (default: localhost)
            port: Server port (default: 8765)
        """
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.server = None
        self._running = False
        self._message_handler: Optional[
            Callable[[Dict[str, Any], WebSocketServerProtocol], None]
        ] = None

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"WebSocket server initialized on {host}:{port}")

    def set_message_handler(
        self, handler: Callable[[Dict[str, Any], WebSocketServerProtocol], None]
    ):
        """
        Set the callback for handling incoming messages from clients.

        Args:
            handler: Callback function that receives (message_dict, websocket) and returns None
        """
        self._message_handler = handler
        self.logger.info("Message handler registered")

    async def _handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """
        Handle a single client connection.

        Args:
            websocket: WebSocket connection
            path: Request path (unused)
        """
        # Add client to set
        self.clients.add(websocket)
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self.logger.info(
            f"Client connected: {client_id} (total clients: {len(self.clients)})"
        )

        try:
            # Send welcome message
            await websocket.send(
                json.dumps(
                    {
                        "type": "connection_established",
                        "message": "Connected to desktop_llm_assistant backend",
                        "timestamp": asyncio.get_event_loop().time(),
                    }
                )
            )

            # Listen for messages from client
            async for message in websocket:
                try:
                    # Parse incoming JSON message
                    data = json.loads(message)
                    self.logger.debug(
                        f"Received from {client_id}: {data.get('type', 'unknown')}"
                    )

                    # Route to message handler
                    if self._message_handler:
                        # Call handler synchronously (it will queue actions for main thread)
                        self._message_handler(data, websocket)
                    else:
                        self.logger.warning(
                            "No message handler registered, ignoring message"
                        )

                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON from {client_id}: {e}")
                    await websocket.send(
                        json.dumps(
                            {
                                "type": "error",
                                "message": "Invalid JSON format",
                                "timestamp": asyncio.get_event_loop().time(),
                            }
                        )
                    )
                except Exception as e:
                    self.logger.error(f"Error processing message from {client_id}: {e}")
                    await websocket.send(
                        json.dumps(
                            {
                                "type": "error",
                                "message": f"Error processing message: {str(e)}",
                                "timestamp": asyncio.get_event_loop().time(),
                            }
                        )
                    )

        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Client {client_id} closed connection normally")
        except Exception as e:
            self.logger.error(f"Error in client handler for {client_id}: {e}")
        finally:
            # Remove client from set
            self.clients.remove(websocket)
            self.logger.info(
                f"Client disconnected: {client_id} (total clients: {len(self.clients)})"
            )

    async def broadcast(self, message: Dict[str, Any]):
        """
        Broadcast a message to all connected clients.

        Args:
            message: Dictionary to broadcast (will be JSON serialized)
        """
        if not self.clients:
            self.logger.debug("No clients connected, skipping broadcast")
            return

        # Serialize message
        try:
            message_json = json.dumps(message)
        except Exception as e:
            self.logger.error(f"Failed to serialize broadcast message: {e}")
            return

        # Send to all clients
        disconnected_clients = set()
        for websocket in self.clients:
            try:
                await websocket.send(message_json)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(websocket)
            except Exception as e:
                self.logger.error(f"Failed to send to client: {e}")
                disconnected_clients.add(websocket)

        # Remove disconnected clients
        self.clients -= disconnected_clients
        if disconnected_clients:
            self.logger.info(
                f"Removed {len(disconnected_clients)} disconnected clients"
            )

        self.logger.debug(
            f"Broadcast {message.get('type', 'unknown')} to {len(self.clients)} clients"
        )

    async def start(self):
        """
        Start the WebSocket server.

        This is a coroutine that runs the server until stopped.
        """
        if self._running:
            self.logger.warning("Server already running")
            return

        self._running = True
        self.logger.info(f"Starting WebSocket server on ws://{self.host}:{self.port}")

        try:
            async with websockets.serve(self._handle_client, self.host, self.port):
                self.logger.info("WebSocket server started successfully")
                # Keep server running
                await asyncio.Future()  # Run forever
        except Exception as e:
            self.logger.error(f"WebSocket server error: {e}")
            raise
        finally:
            self._running = False
            self.logger.info("WebSocket server stopped")

    async def stop(self):
        """
        Stop the WebSocket server and disconnect all clients.
        """
        if not self._running:
            return

        self.logger.info("Stopping WebSocket server...")

        # Close all client connections
        for websocket in list(self.clients):
            try:
                await websocket.close(code=1000, reason="Server shutting down")
            except Exception as e:
                self.logger.error(f"Error closing client connection: {e}")

        self.clients.clear()
        self._running = False
        self.logger.info("WebSocket server stopped")

    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running

    def get_client_count(self) -> int:
        """Get number of connected clients."""
        return len(self.clients)
