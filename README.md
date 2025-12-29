# WebSocket Server API Documentation

WebSocket server for inbound call handling. Processes call-related events and handles binary audio data streaming.

## Table of Contents

- [Server Information](#server-information)
- [Message Formats](#message-formats)
- [API Events](#api-events)
- [Call Flow](#call-flow)

## Server Information

- **Port**: `4143`
- **Protocol**: `ws://`

## Message Formats

The server handles two types of messages:

1. **JSON Text**: For signaling and control events
2. **Binary**: For audio data streaming

## API Events

### Client → Server Events

#### `incoming_call`

Sent when a new call is received by the server.

**Payload:**
```json
{
  "event": "incoming_call",
  "callerId": "string",
  "didNumber": "string",
  "sessionId": "string"
}
```

#### `dtmf`

Sent when a DTMF digit is pressed.

**Payload:**
```json
{
  "event": "dtmf",
  "digit": "string"
}
```

**Valid Digits:** `0-9`, `*`, `#`, `A-D`

#### `hangup`

Sent when client terminates call.

**Payload:**
```json
{
  "event": "hangup"
}
```

### Server → Client Events

#### `answer`

Answer call

**Payload:**
```json
{
  "event": "answer"
}
```

#### `dtmf`

Sent to initiate DTMF tone.

**Payload:**
```json
{
  "event": "dtmf",
  "digit": "string",
  "duration": number
}
```

**Parameters:**
- `digit`: DTMF digit to send (`0-9`, `*`, `#`)
- `duration`: Tone duration in milliseconds (max 1000ms)

#### `hangup`

Sent hangup request

**Payload:**
```json
{
  "event": "hangup"
}
```

## Call Flow

```
Timeline:  0s     5s     7s     17s
           │      │      │      │
           ▼      ▼      ▼      ▼
Client ───[incoming_call]─► Server
                           │
                           │
Server ────────────────────[answer]─► Client
                           │
                           │
Server ─────────────────────[dtmf]──► Client
                           │
                           │
Client ─────[Audio Stream]┼──► Server
            │             │
            │             │
Client ─────[DTMF Events]──┼──► Server
            │             │
            │             │
Server ─────────────────────[hangup]─► Client
```

**Detailed Flow:**

1. **Connection** (0s)

   - Client connects to `ws://localhost:4143`

2. **Incoming Call** (5s)

   - Client sends `{ "event": "incoming_call", "callerId": "...", "didNumber": "...", "sessionId": "..." }`

3. **Answer** (5s)

   - Server sends `{ "event": "answer" }`

4. **Send DTMF** (7s)

   - Server sends `{ "event": "dtmf", "digit": "1", "duration": 200 }`

5. **Audio Stream & DTMF** (7s - 17s)

   - Client streams binary audio
   - Server echoes audio back
   - Client sends DTMF events: `{ "event": "dtmf", "digit": "1" }`

6. **Hangup** (17s)

   - Server sends `{ "event": "hangup" }`
   - Connection closes
