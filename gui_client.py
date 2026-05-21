import tkinter as tk
from PIL import Image, ImageTk
import socket
import struct
import pickle
import cv2
import threading
import time

class TwoWayVideoApp:
    def __init__(self, window, server_ip, port):
        self.window = window
        self.window.title("P2P Video Chat")
        
        # UI Layout: Two video panels side-by-side
        self.main_frame = tk.Frame(window, bg="black")
        self.main_frame.pack(fill="both", expand=True)

        self.remote_label = tk.Label(self.main_frame, text="Waiting for Remote...", bg="black", fg="white")
        self.remote_label.grid(row=0, column=0, padx=5, pady=5)

        self.local_label = tk.Label(self.main_frame, text="Local Preview", bg="black", fg="white")
        self.local_label.grid(row=0, column=1, padx=5, pady=5)

        # Networking Setup
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((server_ip, port))
        except Exception as e:
            print(f"Connection failed: {e}")
            return

        # Control flag
        self.running = True

        # Start Threads
        threading.Thread(target=self.send_video, daemon=True).start()
        threading.Thread(target=self.receive_video, daemon=True).start()

    def send_video(self):
        cap = cv2.VideoCapture(0)
        # Low res for network stability
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        while self.running:
            ret, frame = cap.read()
            if not ret: continue

            # Update Local Preview in GUI
            self.show_frame(frame, self.local_label)

            # Encode and Send
            _, encoded = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            data = pickle.dumps(encoded)
            size = struct.pack("L", len(data))
            
            try:
                self.client_socket.sendall(size + data)
            except:
                self.running = False
                break
            
            # Small sleep to prevent network congestion
            time.sleep(0.03) 
        cap.release()

    def receive_video(self):
        data = b""
        payload_size = struct.calcsize("L")
        
        try:
            while self.running:
                while len(data) < payload_size:
                    packet = self.client_socket.recv(4096)
                    if not packet: return
                    data += packet
                
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("L", packed_msg_size)[0]

                while len(data) < msg_size:
                    data += self.client_socket.recv(4096)

                frame_data = data[:msg_size]
                data = data[msg_size:]

                frame_encoded = pickle.loads(frame_data)
                frame = cv2.imdecode(frame_encoded, cv2.IMREAD_COLOR)
                
                # Update Remote View in GUI
                self.show_frame(frame, self.remote_label)
        except:
            self.running = False

    def show_frame(self, frame, label):
        """Helper to convert OpenCV frame and update a Tkinter label."""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img_tk = ImageTk.PhotoImage(image=img)
        label.config(image=img_tk)
        label.image = img_tk

if __name__ == "__main__":
    root = tk.Tk()
    # Replace with Server IP
    app = TwoWayVideoApp(root, "127.0.0.1", 5555)
    root.mainloop()