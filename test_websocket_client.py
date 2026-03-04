"""
Test client for WebSocket server.

Tests the WebSocket server by connecting, sending messages, and receiving broadcasts.
Run this after starting the main application to validate Phase 2 implementation.
"""

import asyncio
import json
import sys
import websockets
from websockets.client import WebSocketClientProtocol


class TestWebSocketClient:
    """Test client for desktop_llm_assistant WebSocket server."""

    def __init__(self, uri: str = "ws://localhost:8765"):
        """
        Initialize test client.

        Args:
            uri: WebSocket server URI
        """
        self.uri = uri
        self.websocket: WebSocketClientProtocol = None

    async def connect(self):
        """Connect to WebSocket server."""
        print(f"Connecting to {self.uri}...")
        self.websocket = await websockets.connect(self.uri)
        print("✓ Connected successfully")

    async def disconnect(self):
        """Disconnect from WebSocket server."""
        if self.websocket:
            await self.websocket.close()
            print("✓ Disconnected")

    async def send_message(self, message: dict):
        """
        Send a message to the server.

        Args:
            message: Message dictionary (will be JSON serialized)
        """
        message_json = json.dumps(message)
        print(f"\n→ Sending: {message}")
        await self.websocket.send(message_json)

    async def receive_message(self, timeout: float = 2.0):
        """
        Receive a message from the server.

        Args:
            timeout: Timeout in seconds

        Returns:
            Parsed message dictionary or None on timeout
        """
        try:
            message_json = await asyncio.wait_for(
                self.websocket.recv(), timeout=timeout
            )
            message = json.loads(message_json)
            print(f"← Received: {message}")
            return message
        except asyncio.TimeoutError:
            print("  (no response within timeout)")
            return None
        except Exception as e:
            print(f"  Error receiving message: {e}")
            return None

    async def test_connection(self):
        """Test 1: Verify connection and welcome message."""
        print("\n" + "=" * 60)
        print("TEST 1: Connection and Welcome Message")
        print("=" * 60)

        await self.connect()

        # Expect welcome message
        message = await self.receive_message()
        if message and message.get("type") == "connection_established":
            print("✓ Received welcome message")
            return True
        else:
            print("✗ Did not receive expected welcome message")
            return False

    async def test_toggle_listening(self):
        """Test 2: Toggle listening command."""
        print("\n" + "=" * 60)
        print("TEST 2: Toggle Listening Command")
        print("=" * 60)

        # Send toggle listening on
        await self.send_message({"type": "toggle_listening", "enabled": True})

        # Expect acknowledgment
        message = await self.receive_message()
        if message and message.get("type") == "ack":
            print("✓ Received acknowledgment")
            return True
        else:
            print("✗ Did not receive expected acknowledgment")
            return False

    async def test_toggle_gaze(self):
        """Test 3: Toggle gaze tracking command."""
        print("\n" + "=" * 60)
        print("TEST 3: Toggle Gaze Tracking Command")
        print("=" * 60)

        # Send toggle gaze on
        await self.send_message({"type": "toggle_gaze", "enabled": True})

        # Expect acknowledgment
        message = await self.receive_message()
        if message and message.get("type") == "ack":
            print("✓ Received acknowledgment")
            return True
        else:
            print("✗ Did not receive expected acknowledgment")
            return False

    async def test_invalid_message(self):
        """Test 4: Send invalid message (missing type field)."""
        print("\n" + "=" * 60)
        print("TEST 4: Invalid Message (Missing Type)")
        print("=" * 60)

        # Send message without type field
        await self.send_message({"data": "invalid message"})

        # Expect error response
        message = await self.receive_message()
        if message and message.get("type") == "error":
            print("✓ Received error response as expected")
            return True
        else:
            print("✗ Did not receive expected error response")
            return False

    async def test_unknown_message_type(self):
        """Test 5: Send message with unknown type."""
        print("\n" + "=" * 60)
        print("TEST 5: Unknown Message Type")
        print("=" * 60)

        # Send message with unknown type
        await self.send_message({"type": "unknown_command_type", "data": "test"})

        # Expect error response
        message = await self.receive_message()
        if message and message.get("type") == "error":
            print("✓ Received error response as expected")
            return True
        else:
            print("✗ Did not receive expected error response")
            return False

    async def test_broadcast_listener(self, duration: float = 5.0):
        """Test 6: Listen for broadcasts from server."""
        print("\n" + "=" * 60)
        print(f"TEST 6: Listen for Broadcasts ({duration}s)")
        print("=" * 60)
        print("Listening for status updates from the server...")
        print("(Try using voice commands in the main app)")

        broadcasts_received = []
        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < duration:
            message = await self.receive_message(timeout=1.0)
            if message:
                broadcasts_received.append(message)

        print(f"\n✓ Received {len(broadcasts_received)} broadcasts")
        if broadcasts_received:
            print("  Broadcast types:")
            for msg in broadcasts_received:
                print(f"    - {msg.get('type')}")

        return True

    async def run_all_tests(self):
        """Run all tests."""
        print("\n" + "=" * 60)
        print("WEBSOCKET CLIENT TEST SUITE")
        print("=" * 60)

        results = []

        try:
            # Test 1: Connection
            results.append(("Connection", await self.test_connection()))

            # Test 2: Toggle listening
            results.append(("Toggle Listening", await self.test_toggle_listening()))

            # Test 3: Toggle gaze
            results.append(("Toggle Gaze", await self.test_toggle_gaze()))

            # Test 4: Invalid message
            results.append(("Invalid Message", await self.test_invalid_message()))

            # Test 5: Unknown message type
            results.append(
                ("Unknown Message Type", await self.test_unknown_message_type())
            )

            # Test 6: Broadcast listener
            results.append(
                ("Broadcast Listener", await self.test_broadcast_listener(duration=3.0))
            )

        except Exception as e:
            print(f"\n✗ Test suite failed with error: {e}")
            import traceback

            traceback.print_exc()
        finally:
            await self.disconnect()

        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status} - {test_name}")

        print(f"\nTotal: {passed}/{total} tests passed")

        if passed == total:
            print("\n✓ All tests passed!")
            return 0
        else:
            print(f"\n✗ {total - passed} test(s) failed")
            return 1


async def main():
    """Main entry point."""
    client = TestWebSocketClient()
    exit_code = await client.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    print("Desktop LLM Assistant - WebSocket Test Client")
    print("=" * 60)
    print("\nIMPORTANT: Make sure the main application is running first!")
    print("  python main.py\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
