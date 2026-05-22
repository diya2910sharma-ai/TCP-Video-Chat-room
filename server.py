import socket
import threading
import json
import struct

# Configuration
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 5555       # Ensure this port is open in your firewall

clients = []
clients_lock = threading.Lock()

def relay_data(sender_socket, receiver_socket):
    """Relay data between two clients with efficient buffering"""
    buffer = b""
    payload_size = struct.calcsize("L")

    while True:
        try:
            while len(buffer) < payload_size:
                chunk = sender_socket.recv(4096)
                if not chunk:
                    return
                buffer += chunk

            msg_size = struct.unpack("L", buffer[:payload_size])[0]
            buffer = buffer[payload_size:]

            while len(buffer) < msg_size:
                buffer += sender_socket.recv(4096)

            data = buffer[:msg_size]
            buffer = buffer[msg_size:]

            # Send to receiver without processing (pass-through for efficiency)
            receiver_socket.sendall(struct.pack("L", len(data)) + data)

        except Exception as e:
            print(f"Relay error: {e}")
            break

def handle_client_pair(client1, client2, addr1, addr2):
    """Handle communication between two clients"""
    print(f"Pairing {addr1} <-> {addr2}")

    # Start bidirectional relay threads
    t1 = threading.Thread(target=relay_data, args=(client1, client2), daemon=True)
    t2 = threading.Thread(target=relay_data, args=(client2, client1), daemon=True)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print(f"Session ended for {addr1} <-> {addr2}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Server started on {HOST}:{PORT}. Waiting for clients...")

    try:
        while True:
            # Wait for first client
            conn1, addr1 = server.accept()
            print(f"Client 1 connected from {addr1}")

            # Wait for second client
            conn2, addr2 = server.accept()
            print(f"Client 2 connected from {addr2}")

            # Handle this pair in a new thread
            threading.Thread(
                target=handle_client_pair,
                args=(conn1, conn2, addr1, addr2),
                daemon=True
            ).start()

    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()