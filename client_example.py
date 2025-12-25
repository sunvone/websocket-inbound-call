import asyncio
import websockets
import json
import uuid
import os
import argparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VoIPVendorClient:
    def __init__(self, server_url="ws://localhost:4143", send_dtmf=True, auto_hangup=False):
        self.server_url = server_url
        self.session_id = str(uuid.uuid4())
        self.send_dtmf = send_dtmf
        self.auto_hangup = auto_hangup
        self.audio_task = None
        self.call_active = False

    async def send_audio_mock(self, ws):
        """
        Simulates sending binary audio data after the call is answered.
        Each chunk is 160 bytes (8kHz, 20ms, 16-bit PCM).
        """
        logger.info("Audio stream started (sending dummy PCM data)...")
        try:
            while self.call_active:
                audio_chunk = os.urandom(160)
                await ws.send(audio_chunk)
                await asyncio.sleep(0.02)
                
            logger.info("Audio stream finished.")
        except asyncio.CancelledError:
            logger.info("Audio stream stopped (Call Ended).")
        except Exception as e:
            logger.error(f"Audio stream error: {e}")



    async def send_hangup(self, ws):
        """
        Simulates sending hangup events.
        """
        payload = {
            "event": "hangup",
            "sessionId": self.session_id
        }
        await ws.send(json.dumps(payload))
        logger.info(f"Sent hangup for session: {self.session_id}")

    async def handle_incoming_call(self, data):
        """
        Handles incoming_call event from server.
        """
        self.session_id = data.get("sessionId", self.session_id)
        logger.info(f"Received incoming_call event. SessionId: {self.session_id}")


    async def process_messages(self, ws):
        """
        Process incoming messages from the server.
        """
        try:
            async for message in ws:
                if isinstance(message, bytes):
                    logger.debug(f"Received binary audio echo: {len(message)} bytes")
                else:
                    data = json.loads(message)
                    event = data.get("event")
                    logger.info(f"Received JSON: {data}")

                    if event == "incoming_call":
                        await self.handle_incoming_call(data)

                    elif event == "answer":
                        logger.info("Call ANSWERED!")
                        self.call_active = True
                        
                        self.audio_task = asyncio.create_task(self.send_audio_mock(ws))
                        

                        if self.auto_hangup:
                            await asyncio.sleep(8)
                            await self.send_hangup(ws)

                    elif event == "hangup":
                        logger.info("Call HANGUP received.")
                        self.call_active = False
                        break

        except websockets.exceptions.ConnectionClosed as e:
            logger.warning(f"Connection closed by server: {e}")
        except Exception as e:
            logger.error(f"Error processing messages: {e}")

    async def run(self):
        """
        Main run loop for the VoIP Vendor client.
        """
        logger.info(f"Connecting to {self.server_url}...")

        try:
            async with websockets.connect(self.server_url) as ws:
                logger.info("Connected!")
                logger.info("Waiting for events from server...")

                await self.process_messages(ws)

        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            self.call_active = False
            if self.audio_task:
                self.audio_task.cancel()
                try:
                    await self.audio_task
                except asyncio.CancelledError:
                    pass


def main():
    parser = argparse.ArgumentParser(description='VoIP Vendor WebSocket Client')
    parser.add_argument(
        '--url',
        default='ws://localhost:4143',
        help='WebSocket server URL (default: ws://localhost:4143)'
    )
    parser.add_argument(
        '--no-dtmf',
        action='store_true',
        help='Disable sending DTMF events'
    )
    parser.add_argument(
        '--auto-hangup',
        action='store_true',
        help='Automatically hangup after sending audio'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    client = VoIPVendorClient(
        server_url=args.url,
        send_dtmf=not args.no_dtmf,
        auto_hangup=args.auto_hangup
    )

    try:
        asyncio.run(client.run())
    except KeyboardInterrupt:
        logger.info("VoIP Vendor Client stopped manually.")


if __name__ == "__main__":
    main()
