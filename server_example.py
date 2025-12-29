import asyncio
import json
import websockets
from websockets.server import serve

async def handle_client(websocket, path):
    print("Client connected")
    
    try:
        async for message in websocket:
            # Cek apakah message adalah binary atau text
            if isinstance(message, str):
                # Text message (JSON)
                try:
                    payload = json.loads(message)
                    
                    if payload and "event" in payload:
                        event = payload["event"]
                        
                        if event == "incoming_call":
                            print("Incoming call received:", {
                                "event": "incoming_call"
                            })
                            
                            # Tunggu 5 detik lalu kirim answer
                            await asyncio.sleep(5)
                            print("send action answer call")
                            await websocket.send(json.dumps({
                                "event": "answer"
                            }))
                            
                            # Tunggu 10 detik lalu kirim hangup
                            await asyncio.sleep(10)
                            print("send action hangup call")
                            await websocket.send(json.dumps({
                                "event": "hangup"
                            }))
                        
                        elif event == "dtmf":
                            print("DTMF received:", {
                                "event": "dtmf",
                                "digit": payload.get("digit")
                            })
                        
                        elif event == "hangup":
                            print("Hangup received:", {
                                "event": "hangup"
                            })
                
                except json.JSONDecodeError:
                    print("Invalid JSON received")
            
            else:
                # Binary message (audio data) send back audio echo.
                # you can implement tts or other audio in pcm 8khz 
                await websocket.send(message)
    
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    except Exception as err:
        print(f"WS error: {err}")

async def main():
    async with serve(handle_client, "0.0.0.0", 4143):
        print("WS server listening on :4143")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())