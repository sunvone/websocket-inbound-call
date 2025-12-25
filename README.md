# WebSocket Server API Documentation

This project implements a WebSocket server acting as an inbound call handler. It listens for incoming WebSocket connections, processes specific call-related events, and handles binary audio data.

## Table of Contents

- [Server Information](#server-information)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Message Formats](#message-formats)
- [API Events](#api-events)
- [Architecture](#architecture)
- [Call Flow](#call-flow)
- [Server Implementations](#server-implementations)
- [Troubleshooting](#troubleshooting)

## Server Information

- **Port**: `4143`
- **Protocol**: `ws://`
- **Node.js Version**: 14+
- **Python Version**: 3.7+

## Installation

### Node.js Server

```bash
npm install
```

### Python Server

```bash
pip install websockets
```

## Quick Start

### Node.js Server

```bash
node index.js
```

### Python Server

```bash
python server_example.py
```

### Server Output

Node.js:
```
WS server listening on :4143
```

Python:
```
2025-12-25 00:00:00 - INFO - Starting WebSocket server on localhost:4143
2025-12-25 00:00:00 - INFO - WebSocket server listening on ws://localhost:4143
```

## Message Formats

The server handles two types of messages:

1. **JSON Text**: For signaling and control events
2. **Binary**: For audio data streaming

## API Events

### Client → Server Events

**Note:** Client generates its own `sessionId` upon connection and includes it in `dtmf` and `hangup` events.

#### `dtmf`

Sent when a DTMF digit is pressed.

```json
{
  "event": "dtmf",
  "sessionId": "string",
  "digit": "string"
}
```

**Valid Digits:** `0-9`, `*`, `#`, `A-D`

**Server Response:**

- Logs the DTMF event

#### `hangup`

Sent when client terminates call.

```json
{
  "event": "hangup",
  "sessionId": "string"
}
```

**Server Response:**

- Logs the hangup event

### Server → Client Events

#### `incoming_call`

Sent when a new call is received by the server.

```json
{
  "event": "incoming_call"
}
```

#### `answer`

Sent 5 seconds after receiving `incoming_call`.

```json
{
  "event": "answer"
}
```

#### `hangup`

Sent 10 seconds after sending `answer` (total 15 seconds after `incoming_call`).

```json
{
  "event": "hangup"
}
```

## Architecture

```
┌─────────────────┐         WebSocket          ┌─────────────────┐
│  VoIP Vendor    │ ◄────────────────────────► │  Inbound Server │
│  (Client)       │                            │   (Node.js/Python) │
│                 │                            │                 │
│ - Connect       │                            │ - Listen        │
│ - Stream Audio  │                            │ - incoming_call │
│ - DTMF Events   │                            │ - Answer        │
│ - hangup        │                            │ - Echo Audio    │
│                 │                            │ - Log Events    │
│                 │                            │ - Auto Hangup   │
└─────────────────┘                            └─────────────────┘
```

**Server Options:**
- `index.js` - Node.js implementation
- `server_example.py` - Python implementation

## Call Flow

```
Timeline:  0s     1s     6s     16s
           │      │      │      │
           ▼      ▼      ▼      ▼
Server ───[incoming_call]─► Client
                          │
                          │
Server ────────────────────[answer]─► Client
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
   - Client generates `sessionId`

2. **Incoming Call** (1s)
   - Server sends `{ "event": "incoming_call" }`

3. **Answer** (6s)
   - Server sends `{ "event": "answer" }`
   - Client starts streaming binary audio
   - Server echoes audio back

4. **DTMF** (6s - 16s)
   - Client sends DTMF events: `{ "event": "dtmf", "sessionId": "...", "digit": "1" }`
   - Server logs each DTMF event

5. **Hangup** (16s)
   - Server sends `{ "event": "hangup" }`
   - Connection closes

## Server Implementations

### Node.js Server (`index.js`)

**Start:**
```bash
node index.js
```

**Features:**
- Native WebSocket implementation using `ws` library
- Event-driven architecture
- Echo binary audio data

### Python Server (`server_example.py`)

**Start:**
```bash
python server_example.py
```

**Options:**
```bash
python server_example.py --help
```

| Option | Description | Default |
|--------|-------------|---------|
| `--host` | Host to bind to | `localhost` |
| `--port` | Port to bind to | `4143` |
| `--verbose` | Enable verbose logging | `false` |

**Examples:**
```bash
# Custom host and port
python server_example.py --host 0.0.0.0 --port 8080

# Verbose mode
python server_example.py --verbose
```

**Features:**
- Async/await architecture using `websockets` library
- Class-based design for better organization
- Configurable host and port
- Echo binary audio data
- Comprehensive logging

## Troubleshooting

### Server Not Starting

**Error:** `EADDRINUSE: address already in use`

**Solution:** Another process is using port 4143. Kill it or change the port.

### DTMF Not Received

**Check:** Verify the `sessionId` is included in the DTMF event.

### Audio Echo Not Working

**Check:** Ensure binary data is being sent, not JSON.

### Python ImportError

**Error:** `ModuleNotFoundError: No module named 'websockets'`

**Solution:** Install the dependency:

```bash
pip install websockets
```

## License

MIT
