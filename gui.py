import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import requests
import json
import logging
import threading
import base64  # For image encoding

logger = logging.getLogger(__name__)

class ChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Bot with Automation")
        self.root.geometry("800x600")  # Changed: Larger window

        # Chat history
        self.chat_history = scrolledtext.ScrolledText(root, width=80, height=25, wrap=tk.WORD, font=("Arial", 10))
        self.chat_history.pack(pady=10, padx=10)
        self.chat_history.config(state=tk.DISABLED, bg="#f0f0f0")  # Changed: Styled

        # Input frame
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(pady=5, padx=10, fill=tk.X)

        # Command entry
        self.command_entry = tk.Entry(self.input_frame, width=60, font=("Arial", 12))
        self.command_entry.pack(side=tk.LEFT, pady=5, padx=5)

        # Send button
        self.submit_button = tk.Button(self.input_frame, text="Send", command=self.submit_command, font=("Arial", 10))
        self.submit_button.pack(side=tk.LEFT, padx=5)

        # Image upload button
        self.image_button = tk.Button(self.input_frame, text="Upload Image", command=self.upload_image, font=("Arial", 10))
        self.image_button.pack(side=tk.LEFT, padx=5)

        # Automation button
        self.automation_button = tk.Button(self.input_frame, text="Run Automation", command=self.run_automation, font=("Arial", 10))
        self.automation_button.pack(side=tk.LEFT, padx=5)  # New: Automation button

    def submit_command(self):
        command = self.command_entry.get().strip()
        if command:
            self.append_message(f"User: {command}")
            threading.Thread(target=self._send_command, args=(command,)).start()
            self.command_entry.delete(0, tk.END)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.gif")])
        if file_path:
            self.append_message(f"Uploading image: {file_path}")
            threading.Thread(target=self._upload_image, args=(file_path,)).start()

    def run_automation(self):
        command = self.command_entry.get().strip()
        if command:
            if messagebox.askyesno("Confirm Automation", f"Execute automation: {command}?"):
                self.append_message(f"User (Automation): {command}")
                threading.Thread(target=self._run_automation, args=(command,)).start()
            else:
                self.append_message("Automation canceled")

    def _send_command(self, command):
        try:
            response = requests.post(
                "http://localhost:8000/command",
                json={"command": command},
                timeout=10
            )
            response.raise_for_status()
            self.display_response(response.json())
        except requests.RequestException as e:
            self.display_response({"error": f"Backend error: {str(e)}"})

    def _upload_image(self, file_path):
        try:
            with open(file_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
            response = requests.post(
                "http://localhost:8000/upload_image",
                json={"image_data": image_data, "file_type": file_path.split('.')[-1]},
                timeout=10
            )
            response.raise_for_status()
            self.display_response(response.json())
        except requests.RequestException as e:
            self.display_response({"error": f"Backend error: {str(e)}"})

    def _run_automation(self, command):
        try:
            response = requests.post(
                "http://localhost:8000/automation",
                json={"command": command},
                timeout=30  # Longer timeout for automation
            )
            response.raise_for_status()
            self.display_response(response.json())
        except requests.RequestException as e:
            self.display_response({"error": f"Automation error: {str(e)}"})

    def append_message(self, message):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, message + "\n\n")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)

    def display_response(self, response):
        self.append_message("Bot: " + json.dumps(response, indent=2))

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatGUI(root)
    root.mainloop()