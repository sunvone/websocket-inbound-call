import asyncio
import json
import websockets

async def handle_incoming_call(websocket, payload):
    print("Incoming call received:", {
        "event": "incoming_call",
        "callerId": payload.get("callerId"),
        "didNumber": payload.get("didNumber"),
        "sessionId": payload.get("sessionId"),
    })
    
    # Tunggu 5 detik lalu kirim answer
    await asyncio.sleep(5)
    print("send action answer call")
    await websocket.send(json.dumps({
        "event": "answer"
    }))
    
    # Simulation send dtmf
    await asyncio.sleep(2)
    await websocket.send(json.dumps({
        "event": "dtmf",
        "digit": "1",  # digit 0-9 * and #
        "duration": 200,  # duration dtmf in milisecond max 1000ms
    }))
    
    # Send interrupt audio
    await asyncio.sleep(1)
    await websocket.send(json.dumps({
        "event": "interrupt"
    }))
    
    # Tunggu 7 detik lalu kirim hangup
    await asyncio.sleep(7)
    print("send action hangup call")
    await websocket.send(json.dumps({
        "event": "hangup"
    }))

async def handle_client(websocket):
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
                            asyncio.create_task(handle_incoming_call(websocket, payload))
                        
                        elif event == "dtmf":
                            print("DTMF received:", {
                                "event": "dtmf",
                                "digit": payload.get("digit"),
                            })
                        
                        elif event == "hangup":
                            print("Hangup received:", {
                                "event": "hangup",
                            })
                        
                        elif event == "cdr":
                            print("Cdr received:", {
                                "event": "cdr",
                                "sessionId": payload.get("sessionId"),
                                "source": payload.get("source"),
                                "destination": payload.get("destination"),
                                "startTime": payload.get("startTime"),
                                "answerTime": payload.get("answerTime"),
                                "endTime": payload.get("endTime"),
                                "duration": payload.get("duration"),
                                "billableSeconds": payload.get("billableSeconds"),
                                "disposition": payload.get("disposition"),
                                "hangupBy": payload.get("hangupBy"),
                                "hangupCauseCode": payload.get("hangupCauseCode"),
                                "hangupCauseText": payload.get("hangupCauseText"),
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
    async with websockets.serve(handle_client, "0.0.0.0", 4143):
        print("WS server listening on :4143")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
