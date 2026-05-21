import socket
import threading

# Configuration
HOST = '0.0.0.0' # Listen on all available interfaces
PORT = 5555      # Ensure this port is open in your firewall

clients = []

def handle_client(current_socket, partner_socket):
    """
    Receives data from one client and sends it to the other.
    """
    try:
        while True:
            # Receive data (Video frames or Text)
            data = current_socket.recv(4096)
            if not data:
                break
            
            # Relay to the partner
            partner_socket.sendall(data)
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        current_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)
    print(f"Server started on {HOST}:{PORT}. Waiting for 2 clients...")

    # Wait for exactly two clients to connect
    while len(clients) < 2:
        conn, addr = server.accept()
        print(f"Client connected from {addr}")
        clients.append(conn)

    print("Both clients connected. Starting relay...")
    
    # Thread 1: Relay Client A -> Client B
    t1 = threading.Thread(target=handle_client, args=(clients[0], clients[1]))
    # Thread 2: Relay Client B -> Client A
    t2 = threading.Thread(target=handle_client, args=(clients[1], clients[0]))

    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    print("Session ended.")

if __name__ == "__main__":
    start_server()