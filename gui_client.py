import tkinter as tk
from tkinter import scrolledtext, messagebox
from PIL import Image, ImageTk
import socket
import struct
import json
import cv2
import threading
import time
from datetime import datetime

class VideoChatApp:
    def __init__(self, window, server_ip, port):
        self.window = window
        self.window.title("TCP Video Chat")
        self.window.geometry("1200x600")
        
        self.server_ip = server_ip
        self.port = port
        self.running = False
        self.client_socket = None
        
        self.setup_ui()
        self.connect_to_server()

    def setup_ui(self):
        """Create UI layout: Chat (left) + Video (right)"""
        # Main container
        self.main_frame = tk.Frame(self.window, bg="#1e1e1e")
        self.main_frame.pack(fill="both", expand=True)

        # LEFT: Chat Panel
        self.chat_frame = tk.Frame(self.main_frame, bg="#2d2d2d")
        self.chat_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        tk.Label(self.chat_frame, text="Chat", font=("Arial", 12, "bold"), bg="#2d2d2d", fg="white").pack()

        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, height=20, width=35, bg="#1e1e1e", fg="white", state="disabled")
        self.chat_display.pack(fill="both", expand=True, pady=5)

        self.msg_input = tk.Entry(self.chat_frame, bg="#3d3d3d", fg="white", font=("Arial", 10))
        self.msg_input.pack(fill="x", pady=5)
        self.msg_input.bind("<Return>", lambda e: self.send_message())

        tk.Button(self.chat_frame, text="Send", command=self.send_message, bg="#0d7377", fg="white").pack(fill="x")

        # RIGHT: Video Panel
        self.video_frame = tk.Frame(self.main_frame, bg="#2d2d2d")
        self.video_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        tk.Label(self.video_frame, text="Video", font=("Arial", 12, "bold"), bg="#2d2d2d", fg="white").pack()

        self.remote_video = tk.Label(self.video_frame, bg="black", text="Waiting for remote...", fg="white")
        self.remote_video.pack(fill="both", expand=True, pady=5)

    def connect_to_server(self):
        """Connect to server and start communication threads"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, self.port))
            self.running = True
            
            self.add_chat("System", "Connected to server!")
            
            threading.Thread(target=self.send_video, daemon=True).start()
            threading.Thread(target=self.receive_data, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            self.window.destroy()

    def send_message(self):
        """Send chat message"""
        message = self.msg_input.get().strip()
        if not message or not self.running:
            return
        
        self.add_chat("You", message)
        self.msg_input.delete(0, tk.END)

        try:
            msg_packet = json.dumps({"type": "message", "text": message}).encode()
            self.client_socket.sendall(struct.pack("L", len(msg_packet)) + msg_packet)
        except Exception as e:
            print(f"Error sending message: {e}")

    def send_video(self):
        """Capture and send video frames"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        cap.set(cv2.CAP_PROP_FPS, 15)

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            try:
                _, encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
                video_packet = json.dumps({"type": "video"}).encode() + encoded.tobytes()
                self.client_socket.sendall(struct.pack("L", len(video_packet)) + video_packet)
                time.sleep(0.066)  # ~15 FPS
            except Exception as e:
                print(f"Error sending video: {e}")
                break

        cap.release()

    def receive_data(self):
        """Receive messages and video frames"""
        buffer = b""
        payload_size = struct.calcsize("L")

        while self.running:
            try:
                while len(buffer) < payload_size:
                    chunk = self.client_socket.recv(4096)
                    if not chunk:
                        self.running = False
                        return
                    buffer += chunk

                msg_size = struct.unpack("L", buffer[:payload_size])[0]
                buffer = buffer[payload_size:]

                while len(buffer) < msg_size:
                    buffer += self.client_socket.recv(4096)

                data = buffer[:msg_size]
                buffer = buffer[msg_size:]

                try:
                    json_data = json.loads(data.decode())
                    if json_data["type"] == "message":
                        self.add_chat("Remote", json_data["text"])
                except:
                    # Video frame
                    frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
                    if frame is not None:
                        self.display_remote_video(frame)
            except Exception as e:
                print(f"Error receiving: {e}")
                break

    def display_remote_video(self, frame):
        """Display remote video"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img.thumbnail((480, 360), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(image=img)
        self.remote_video.config(image=img_tk, text="")
        self.remote_video.image = img_tk

    def add_chat(self, sender, message):
        """Add message to chat display"""
        self.chat_display.config(state="normal")
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.insert(tk.END, f"[{timestamp}] {sender}: {message}\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")

    def on_closing(self):
        """Cleanup on window close"""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", lambda: app.on_closing() if 'app' in locals() else root.destroy())
    
    # Configuration
    SERVER_IP = "127.0.0.1"  # Change to server's public IP for remote connection
    PORT = 5555
    
    app = VideoChatApp(root, SERVER_IP, PORT)
    root.mainloop()