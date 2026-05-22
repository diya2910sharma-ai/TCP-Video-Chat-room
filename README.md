# TCP Video Chat Room

A lightweight, efficient peer-to-peer video chat application for two users connected over the internet using TCP sockets.

## Features

- **Split-Panel UI**: Chat on the left, video stream on the right
- **Real-time Communication**: Simultaneous video and text messaging
- **Efficient Streaming**: JPEG compression (60% quality) + 15 FPS for bandwidth optimization
- **JSON Protocol**: Structured message types for clean data separation
- **Relay Server**: Central server that pairs and relays data between two clients
- **Low Latency**: Direct socket communication without heavy frameworks

## Requirements

```bash
pip install opencv-python pillow
```

- Python 3.7+
- OpenCV (cv2)
- Pillow (PIL)
- tkinter (usually included with Python)

## Project Structure

```
TCP-Video-Chat-room/
├── server.py          # Relay server that pairs clients
├── gui_client.py      # Client GUI (chat + video)
└── README.md          # Documentation
```

## Setup

### 1. Start the Server

On the server machine:

```bash
python server.py
```

The server will start on `0.0.0.0:5555` and wait for two clients to connect.

### 2. Connect First Client

On the first machine:

```bash
# Edit SERVER_IP in gui_client.py to your server's public IP
python gui_client.py
```

### 3. Connect Second Client

On the second machine:

```bash
# Use the same SERVER_IP as the first client
python gui_client.py
```

Once both clients connect, they'll be paired automatically and communication will begin.

## Usage

- **Send Chat**: Type in the left panel and press Enter or click "Send"
- **Video**: Automatically streams from your webcam to the remote user
- **Close**: Close the window to disconnect

## Configuration

Edit `gui_client.py` to change:

- `SERVER_IP`: Server's IP address or hostname
- `PORT`: Server port (default: 5555)

Example for remote connection:

```python
SERVER_IP = "your.server.com"  # or public IP like "203.0.113.42"
PORT = 5555
```

## Architecture

### Efficient Layering

1. **Message Format**:
   - Size header (4 bytes): Message length
   - Payload: JSON metadata + binary data
   - Video frames are raw JPEG-encoded bytes
   - Chat messages are JSON objects

2. **Server Design**:
   - Pairs incoming clients
   - Relays data without parsing (pass-through)
   - Supports multiple client pairs simultaneously

3. **Client Optimization**:
   - 480x360 resolution, 15 FPS
   - JPEG compression (60% quality)
   - Separate threads for send/receive
   - Non-blocking UI updates

## Performance Tips

- **Bandwidth**: ~200-400 KB/s per video stream (depends on motion)
- **Latency**: 50-200ms typical (depends on network)
- **CPU**: Low usage with 15 FPS cap
- **Reduce resolution** in `gui_client.py` if experiencing lag

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" | Check server IP and port, ensure firewall allows port 5555 |
| Video lag | Reduce FPS or resolution in `send_video()` |
| One-way video | Check if both clients can send frames (webcam permissions) |
| High CPU | Reduce FPS from 15 to 10, or lower resolution |

## Future Improvements

- Screen sharing mode
- Recording functionality
- Multi-client support (group chat)
- Audio support
- End-to-end encryption

## License

MIT License - Feel free to use and modify for educational purposes.

---

**Made for university project** 🎓
