import tkinter as tk
from tkinter import scrolledtext, filedialog
import requests
import json

class ChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Bot")

        # Chat history
        self.chat_history = scrolledtext.ScrolledText(root, width=60, height=20, wrap=tk.WORD)
        self.chat_history.pack(pady=10, padx=10)
        self.chat_history.config(state=tk.DISABLED)  # Read-only

        # Text input for commands
        self.command_entry = tk.Entry(root, width=50)
        self.command_entry.pack(pady=5, padx=10)

        # Button to submit text command
        self.submit_button = tk.Button(root, text="Send", command=self.submit_command)
        self.submit_button.pack(pady=5)

        # Button for image upload
        self.image_button = tk.Button(root, text="Upload Image", command=self.upload_image)
        self.image_button.pack(pady=5)

    def submit_command(self):
        """Handle text command submission."""
        command = self.command_entry.get().strip()
        if command:
            self.append_message("User: " + command)
            response = self.send_command(command)
            self.display_response(response)
            self.command_entry.delete(0, tk.END)  # Clear input field

    def upload_image(self):
        """Handle image upload."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.gif")])
        if file_path:
            self.append_message("Uploading image: " + file_path)
            response = self.send_image(file_path)
            self.display_response(response)

    def send_command(self, command):
        """Send command to FastAPI backend."""
        try:
            response = requests.post(
                "http://localhost:8000/command",
                json={"command": command},
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Backend error: {str(e)}"}

    def send_image(self, file_path):
        """Send image to FastAPI backend."""
        try:
            with open(file_path, "rb") as f:
                files = {"file": f}
                response = requests.post(
                    "http://localhost:8000/upload_image",
                    files=files
                )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Backend error: {str(e)}"}

    def append_message(self, message):
        """Append message to chat history."""
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, message + "\n\n")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)  # Scroll to the end

    def display_response(self, response):
        """Display the backend response in the chat history."""
        self.append_message("Bot: " + json.dumps(response, indent=2))

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatGUI(root)
    root.mainloop()