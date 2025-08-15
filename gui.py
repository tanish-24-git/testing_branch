import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import requests
import json
import logging
import threading
import base64
import webbrowser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load SMTP credentials from .env
load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Bot with Automation & Email")
        self.root.geometry("900x700")

        # Chat history
        self.chat_history = scrolledtext.ScrolledText(
            root, width=100, height=30, wrap=tk.WORD, font=("Arial", 10), bg="#f0f0f0"
        )
        self.chat_history.pack(pady=10, padx=10)
        self.chat_history.config(state=tk.DISABLED)

        # Input frame
        frame = tk.Frame(root)
        frame.pack(pady=5, padx=10, fill=tk.X)

        self.command_entry = tk.Entry(frame, width=70, font=("Arial", 12))
        self.command_entry.pack(side=tk.LEFT, padx=5)
        self.command_entry.bind("<Return>", lambda e: self.submit_command())

        btn_cfg = {"font": ("Arial", 10), "padx": 10, "pady": 5}
        tk.Button(frame, text="Send Chat", command=self.submit_command, **btn_cfg).pack(side=tk.LEFT)
        tk.Button(frame, text="Upload Image", command=self.upload_image, **btn_cfg).pack(side=tk.LEFT)
        tk.Button(frame, text="Run Automation", command=self.run_automation, **btn_cfg).pack(side=tk.LEFT)
        tk.Button(frame, text="Send Email", command=self.send_email_gui, **btn_cfg).pack(side=tk.LEFT)

    def append_message(self, message):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, message + "\n\n")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)

    def display_response(self, response):
        self.append_message("Bot: " + json.dumps(response, indent=2))

    def submit_command(self):
        cmd = self.command_entry.get().strip()
        if not cmd:
            return
        self.append_message(f"User: {cmd}")
        threading.Thread(target=self._send_command, args=(cmd,), daemon=True).start()
        self.command_entry.delete(0, tk.END)

    def _send_command(self, cmd):
        try:
            resp = requests.post("http://localhost:8000/command", json={"command": cmd}, timeout=200)
            resp.raise_for_status()
            self.display_response(resp.json())
        except Exception as e:
            self.append_message(f"Error: {e}")

    def upload_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.gif")])
        if not path:
            return
        self.append_message(f"Uploading: {path}")
        threading.Thread(target=self._upload_image, args=(path,), daemon=True).start()

    def _upload_image(self, path):
        try:
            data = base64.b64encode(open(path,"rb").read()).decode()
            resp = requests.post("http://localhost:8000/upload_image",
                                 json={"image_data": data, "file_type": path.split(".")[-1]},
                                 timeout=200)
            resp.raise_for_status()
            self.display_response(resp.json())
        except Exception as e:
            self.append_message(f"Error: {e}")

    def run_automation(self):
        cmd = self.command_entry.get().strip()
        if not cmd:
            return
        # Local handle for simple opens
        lower = cmd.lower()
        if lower.startswith("open ") or lower.startswith("navigate to "):
            import re
            m = re.search(r"(https?://\S+)", cmd)
            if m:
                url = m.group(1)
                webbrowser.open(url)
                self.append_message(f"🔗 Opened URL: {url}")
                self.command_entry.delete(0, tk.END)
                return
        # Else call backend
        if messagebox.askyesno("Confirm Automation", f"Execute: {cmd}?"):
            self.append_message(f"Automation: {cmd}")
            threading.Thread(target=self._run_automation, args=(cmd,), daemon=True).start()
        else:
            self.append_message("Automation canceled")

    def _run_automation(self, cmd):
        try:
            resp = requests.post("http://localhost:8000/automation", json={"command": cmd}, timeout=600)
            resp.raise_for_status()
            self.display_response(resp.json())
        except Exception as e:
            self.append_message(f"Error: {e}")

    def send_email_gui(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Send Email")
        tk.Label(dlg, text="To:").grid(row=0, column=0)
        to_e = tk.Entry(dlg, width=50); to_e.grid(row=0,column=1)
        tk.Label(dlg, text="Subject:").grid(row=1, column=0)
        sub_e = tk.Entry(dlg, width=50); sub_e.grid(row=1,column=1)
        tk.Label(dlg, text="Body:").grid(row=2, column=0)
        body_t = tk.Text(dlg, width=50, height=10); body_t.grid(row=2,column=1)
        def send():
            to = to_e.get().strip()
            sub = sub_e.get().strip()
            body = body_t.get("1.0", tk.END).strip()
            dlg.destroy()
            self.append_message(f"Sending email to {to}...")
            threading.Thread(target=self._send_email, args=(to, sub, body), daemon=True).start()
        tk.Button(dlg, text="Send", command=send).grid(row=3, column=1)
        
    def _send_email(self, to, subject, body):
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            self.append_message("❌ SMTP not configured. Update .env")
            return
        try:
            msg = MIMEMultipart()
            msg["From"] = SMTP_USERNAME
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            self.append_message(f"✅ Email sent to {to}")
        except Exception as e:
            self.append_message(f"❌ Email error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatGUI(root)
    root.mainloop()
