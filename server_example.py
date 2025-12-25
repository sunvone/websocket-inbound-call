import asyncio
import websockets
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InboundWebSocketServer:
    def __init__(self, host="localhost", port=4143):
        self.host = host
        self.port = port

    async def handle_client(self, ws):
        """
        Handle client connection and messages.
        """
        logger.info("Client connected")

        try:
            asyncio.create_task(self.call_flow(ws))

            async for message in ws:
                if isinstance(message, bytes):
                    await self.handle_audio(ws, message)
                else:
                    try:
                        data = json.loads(message)
                        event = data.get("event")
                        logger.info(f"Received JSON: {data}")

                        if event == "dtmf":
                            await self.handle_dtmf(data)
                        elif event == "hangup":
                            await self.handle_hangup(data)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON received: {message}")

        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")
        except Exception as e:
            logger.error(f"Error handling client: {e}")

    async def call_flow(self, ws):
        """
        Automated call flow: incoming_call -> answer -> hangup
        """
        try:
            await asyncio.sleep(1)

            payload = {
                "event": "incoming_call"
            }
            await ws.send(json.dumps(payload))
            logger.info("Sent incoming_call")

            await asyncio.sleep(5)

            payload = {
                "event": "answer"
            }
            await ws.send(json.dumps(payload))
            logger.info("Sent answer")

            await asyncio.sleep(10)

            payload = {
                "event": "hangup"
            }
            await ws.send(json.dumps(payload))
            logger.info("Sent hangup")

        except Exception as e:
            logger.error(f"Error in call flow: {e}")

    async def handle_audio(self, ws, data):
        """
        Echo binary audio data back to client.
        """
        try:
            await ws.send(data)
            logger.debug(f"Echoed audio: {len(data)} bytes")
        except Exception as e:
            logger.error(f"Error echoing audio: {e}")

    async def handle_dtmf(self, data):
        """
        Handle DTMF event from client.
        """
        logger.info(f"DTMF received: {data}")

    async def handle_hangup(self, data):
        """
        Handle hangup event from client.
        """
        logger.info(f"Hangup received: {data}")

    async def start(self):
        """
        Start the WebSocket server.
        """
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")

        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info(f"WebSocket server listening on ws://{self.host}:{self.port}")
            await asyncio.Future()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Inbound WebSocket Server')
    parser.add_argument(
        '--host',
        default='localhost',
        help='Host to bind to (default: localhost)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=4143,
        help='Port to bind to (default: 4143)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    server = InboundWebSocketServer(host=args.host, port=args.port)

    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("Server stopped manually.")


if __name__ == "__main__":
    main()
