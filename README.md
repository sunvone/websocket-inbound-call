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
- [Python Client](#python-client)
- [Troubleshooting](#troubleshooting)

## Server Information

- **Port**: `4143`
- **Protocol**: `ws://`
- **Node.js Version**: 14+

## Installation

### Server

```bash
npm install
```

### Python Client

```bash
pip install websockets
```

## Quick Start

### 1. Start the Server

```bash
node index.js
```

Server output:

```
WS server listening on :4143
```

### 2. Run the Python Client

```bash
python client_example.py
```

Client output:

```
2025-12-25 00:00:00 - INFO - Connecting to ws://localhost:4143...
2025-12-25 00:00:00 - INFO - Connected!
2025-12-25 00:00:00 - INFO - Waiting for events from server...
2025-12-25 00:00:00 - INFO - Received JSON: {'event': 'incoming_call', 'sessionId': '550e8400...'}
2025-12-25 00:00:05 - INFO - Call ANSWERED!

...
```

## Message Formats

The server handles two types of messages:

1. **JSON Text**: For signaling and control events
2. **Binary**: For audio data streaming

## API Events

### Client → Server Events

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

Sent when the client terminates the call.

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
  "event": "incoming_call",
  "sessionId": "string"
}
```

#### `answer`

Sent 5 seconds after receiving `incoming_call`.

```json
{
  "event": "answer",
  "sessionId": "string"
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
│  (Client)       │                            │   (index.js)    │
│                 │                            │                 │
│ - Connect       │                            │ - Listen        │
│ - Stream Audio  │                            │ - incoming_call │
│ - DTMF Events   │                            │ - Answer        │
│ - hangup        │                            │ - Echo Audio    │
│                 │                            │ - Log Events    │
│                 │                            │ - Auto Hangup   │
└─────────────────┘                            └─────────────────┘
```

## Call Flow

```
Timeline:  0s      5s       15s
           │       │        │
           ▼       ▼        ▼
Server ───[incoming_call]──► Client
                           │
                           │
Server ─────────────────────[answer]───► Client
                           │
                           │
Client ────[Audio Stream]──┼──► Server
           │               │
           │               │
Client ────[DTMF Events]───┼──► Server
           │               │
           │               │
Server ────────────────────[hangup]──► Client
```

**Detailed Flow:**

1. **Connection** (0s)

   - Client connects to `ws://localhost:4143`

2. **Incoming Call** (0s)

   - Server sends `{ "event": "incoming_call", "sessionId": "..." }`

3. **Answer** (5s)

   - Server sends `{ "event": "answer", "sessionId": "..." }`
   - Client starts streaming binary audio
   - Server echoes audio back

4. **DTMF** (5s - 15s)

   - Client sends DTMF events: `{ "event": "dtmf", "digit": "1" }`
   - Server logs each DTMF event

5. **Hangup** (15s)
   - Server sends `{ "event": "hangup" }`
   - Connection closes

## Python Client

### Basic Usage

```bash
python client_example.py
```

### Command-Line Options

```bash
python client_example.py --help
```

| Option          | Description                     | Default               |
| --------------- | ------------------------------- | --------------------- |
| `--url`         | WebSocket server URL            | `ws://localhost:4143` |
| `--no-dtmf`     | Disable sending DTMF events     | `false`               |
| `--auto-hangup` | Auto hangup after sending audio | `false`               |
| `--verbose`     | Enable verbose logging          | `false`               |

### Examples

**Connect to custom server:**

```bash
python client_example.py --url ws://192.168.1.100:4143
```

**Disable DTMF:**

```bash
python client_example.py --no-dtmf
```

**Auto hangup:**

```bash
python client_example.py --auto-hangup
```

**Verbose mode:**

```bash
python client_example.py --verbose
```

### Client Features

- **Audio Streaming**: Simulates PCM audio streaming (8kHz, 20ms frames)
- **DTMF Support**: Automatically sends DTMF sequence `1-5` after answer
- **Error Handling**: Proper connection error handling and cleanup
- **Configurable**: URL, DTMF, auto-hangup via CLI arguments
- **Logging**: Timestamped logging for debugging

## Troubleshooting

### Server Not Starting

**Error:** `EADDRINUSE: address already in use`

**Solution:** Another process is using port 4143. Kill it or change the port in `index.js`.

### Client Connection Failed

**Error:** `Connection refused`

**Solution:** Make sure the server is running on `http://localhost:4143`.

### DTMF Not Received

**Check:** Verify the `sessionId` matches between `incoming_call` and `dtmf` events.

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
