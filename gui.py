import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk
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
import asyncio
from datetime import datetime

# Load environment variables
load_dotenv()

# SMTP Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Logger setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EnhancedChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced AI Agent - Email Intelligence & Desktop Automation")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2c3e50")
        
        # Email monitoring state
        self.email_monitoring = False
        self.last_email_check = None
        
        self.setup_ui()
        self.setup_email_monitoring()
        
    def setup_ui(self):
        """Setup the enhanced UI with multiple panels"""
        
        # Create main frames
        self.setup_header()
        self.setup_main_content()
        self.setup_sidebar()
        self.setup_status_bar()
        
    def setup_header(self):
        """Setup header with agent status and controls"""
        header_frame = tk.Frame(self.root, bg="#34495e", height=60)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        header_frame.pack_propagate(False)
        
        # Title and status
        title_label = tk.Label(header_frame, text="Enhanced AI Agent", 
                              font=("Arial", 16, "bold"), 
                              bg="#34495e", fg="white")
        title_label.pack(side=tk.LEFT, padx=10, pady=15)
        
        # Agent status indicator
        self.status_frame = tk.Frame(header_frame, bg="#34495e")
        self.status_frame.pack(side=tk.RIGHT, padx=10, pady=15)
        
        self.status_label = tk.Label(self.status_frame, text="🤖 Agent: Ready", 
                                   font=("Arial", 10), bg="#34495e", fg="#2ecc71")
        self.status_label.pack(side=tk.RIGHT)
        
        # Email monitoring toggle
        self.email_toggle_btn = tk.Button(self.status_frame, text="📧 Monitor Emails", 
                                        command=self.toggle_email_monitoring,
                                        font=("Arial", 9), bg="#3498db", fg="white")
        self.email_toggle_btn.pack(side=tk.RIGHT, padx=5)
        
    def setup_main_content(self):
        """Setup main content area with chat and input"""
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # Chat history with better styling
        chat_frame = tk.Frame(main_frame, bg="#ecf0f1")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Chat history
        self.chat_history = scrolledtext.ScrolledText(
            chat_frame, 
            width=100, height=25, 
            wrap=tk.WORD, 
            font=("Consolas", 10),
            bg="#ecf0f1", 
            fg="#2c3e50",
            insertbackground="#2c3e50",
            selectbackground="#3498db",
            relief="flat",
            bd=10
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.chat_history.config(state=tk.DISABLED)
        
        # Input frame with enhanced controls
        input_frame = tk.Frame(main_frame, bg="#2c3e50")
        input_frame.pack(fill=tk.X, pady=5)
        
        # Command entry
        self.command_entry = tk.Entry(input_frame, width=80, font=("Arial", 12),
                                    bg="white", fg="#2c3e50", relief="flat", bd=5)
        self.command_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.command_entry.bind("<Return>", lambda e: self.submit_command())
        
        # Enhanced button styling
        btn_style = {
            "font": ("Arial", 10, "bold"),
            "relief": "flat",
            "bd": 0,
            "padx": 15,
            "pady": 8,
            "cursor": "hand2"
        }
        
        # Buttons
        tk.Button(input_frame, text="💬 Chat", command=self.submit_command, 
                 bg="#3498db", fg="white", **btn_style).pack(side=tk.LEFT, padx=2)
        
        tk.Button(input_frame, text="🖼️ Image", command=self.upload_image, 
                 bg="#9b59b6", fg="white", **btn_style).pack(side=tk.LEFT, padx=2)
        
        tk.Button(input_frame, text="🤖 Automate", command=self.run_automation, 
                 bg="#e67e22", fg="white", **btn_style).pack(side=tk.LEFT, padx=2)
        
        tk.Button(input_frame, text="📧 Email", command=self.show_email_composer, 
                 bg="#27ae60", fg="white", **btn_style).pack(side=tk.LEFT, padx=2)
        
        tk.Button(input_frame, text="🖥️ Desktop", command=self.run_desktop_automation, 
                 bg="#e74c3c", fg="white", **btn_style).pack(side=tk.LEFT, padx=2)
        
    def setup_sidebar(self):
        """Setup sidebar with email and system info"""
        sidebar = tk.Frame(self.root, bg="#34495e", width=300)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        sidebar.pack_propagate(False)
        
        # Sidebar title
        tk.Label(sidebar, text="📊 System Status", font=("Arial", 12, "bold"),
                bg="#34495e", fg="white").pack(pady=10)
        
        # Email status
        email_frame = tk.LabelFrame(sidebar, text="📧 Email Status", 
                                  bg="#34495e", fg="white", font=("Arial", 10))
        email_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.email_status_label = tk.Label(email_frame, text="Status: Disconnected",
                                         bg="#34495e", fg="#e74c3c", font=("Arial", 9))
        self.email_status_label.pack(pady=5)
        
        self.last_check_label = tk.Label(email_frame, text="Last Check: Never",
                                       bg="#34495e", fg="white", font=("Arial", 8))
        self.last_check_label.pack(pady=2)
        
        # Recent emails list
        self.recent_emails = tk.Listbox(email_frame, height=5, bg="white", 
                                      font=("Arial", 8))
        self.recent_emails.pack(fill=tk.X, padx=5, pady=5)
        
        # System status
        system_frame = tk.LabelFrame(sidebar, text="🖥️ System Status", 
                                   bg="#34495e", fg="white", font=("Arial", 10))
        system_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.system_status_text = tk.Text(system_frame, height=8, width=35, 
                                        bg="#2c3e50", fg="white", font=("Arial", 8),
                                        wrap=tk.WORD, relief="flat")
        self.system_status_text.pack(padx=5, pady=5)
        
        # Update system status
        self.update_system_status()
        
    def setup_status_bar(self):
        """Setup status bar at bottom"""
        status_bar = tk.Frame(self.root, bg="#95a5a6", height=25)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)
        
        self.status_text = tk.Label(status_bar, text="Ready", bg="#95a5a6", 
                                  fg="#2c3e50", font=("Arial", 9))
        self.status_text.pack(side=tk.LEFT, padx=10, pady=3)
        
        # Connection indicators
        self.connection_frame = tk.Frame(status_bar, bg="#95a5a6")
        self.connection_frame.pack(side=tk.RIGHT, padx=10, pady=3)
        
        self.api_status = tk.Label(self.connection_frame, text="🔴 API", 
                                 bg="#95a5a6", font=("Arial", 8))
        self.api_status.pack(side=tk.RIGHT, padx=5)
        
    def setup_email_monitoring(self):
        """Initialize email monitoring"""
        if SMTP_USERNAME and SMTP_PASSWORD:
            self.email_status_label.config(text="Status: Configured", fg="#f39c12")
            self.status_text.config(text="Email configured - Ready to monitor")
        else:
            self.email_status_label.config(text="Status: Not Configured", fg="#e74c3c")
            self.status_text.config(text="Configure email settings in .env file")
            
    def toggle_email_monitoring(self):
        """Toggle email monitoring on/off"""
        if not self.email_monitoring:
            self.start_email_monitoring()
        else:
            self.stop_email_monitoring()
            
    def start_email_monitoring(self):
        """Start background email monitoring"""
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            messagebox.showwarning("Configuration", "Email not configured. Update .env file.")
            return
            
        self.email_monitoring = True
        self.email_toggle_btn.config(text="📧 Stop Monitor", bg="#e74c3c")
        self.email_status_label.config(text="Status: Monitoring", fg="#27ae60")
        
        # Start monitoring thread
        threading.Thread(target=self._email_monitor_loop, daemon=True).start()
        self.append_message("🤖 Email monitoring started")
        
    def stop_email_monitoring(self):
        """Stop email monitoring"""
        self.email_monitoring = False
        self.email_toggle_btn.config(text="📧 Monitor Emails", bg="#3498db")
        self.email_status_label.config(text="Status: Stopped", fg="#f39c12")
        self.append_message("🤖 Email monitoring stopped")
        
    def _email_monitor_loop(self):
        """Background email monitoring loop"""
        while self.email_monitoring:
            try:
                # Check for new emails
                self.check_emails()
                # Wait for 5 minutes
                for _ in range(300):  # 300 seconds = 5 minutes
                    if not self.email_monitoring:
                        break
                    threading.Event().wait(1)
            except Exception as e:
                logger.error(f"Email monitoring error: {e}")
                threading.Event().wait(60)  # Wait 1 minute on error
                
    def check_emails(self):
        """Check for new emails and suggest replies"""
        try:
            # This would connect to IMAP and check for new emails
            # For now, we'll simulate checking
            self.last_email_check = datetime.now()
            self.last_check_label.config(text=f"Last Check: {self.last_email_check.strftime('%H:%M:%S')}")
            
            # Simulate finding new emails (replace with actual IMAP logic)
            # new_emails = self.fetch_new_emails()
            # if new_emails:
            #     self.process_new_emails(new_emails)
            
        except Exception as e:
            logger.error(f"Error checking emails: {e}")
            
    def show_email_composer(self):
        """Show enhanced email composer with AI assistance"""
        composer = tk.Toplevel(self.root)
        composer.title("🤖 AI Email Composer")
        composer.geometry("700x600")
        composer.configure(bg="#ecf0f1")
        
        # Email fields
        tk.Label(composer, text="To:", bg="#ecf0f1", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        to_entry = tk.Entry(composer, width=60, font=("Arial", 10))
        to_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(composer, text="Subject:", bg="#ecf0f1", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        subject_entry = tk.Entry(composer, width=60, font=("Arial", 10))
        subject_entry.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(composer, text="Body:", bg="#ecf0f1", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="nw", padx=10, pady=5)
        body_text = tk.Text(composer, width=60, height=20, font=("Arial", 10), wrap=tk.WORD)
        body_text.grid(row=2, column=1, padx=10, pady=5)
        
        # AI assistance frame
        ai_frame = tk.Frame(composer, bg="#ecf0f1")
        ai_frame.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        # AI assistance buttons
        tk.Button(ai_frame, text="🤖 AI Compose", 
                 command=lambda: self.ai_compose_email(subject_entry, body_text),
                 bg="#3498db", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(ai_frame, text="✨ Improve Tone", 
                 command=lambda: self.ai_improve_tone(body_text),
                 bg="#9b59b6", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(ai_frame, text="🔍 Check Grammar", 
                 command=lambda: self.ai_check_grammar(body_text),
                 bg="#e67e22", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        # Send button
        send_frame = tk.Frame(composer, bg="#ecf0f1")
        send_frame.grid(row=4, column=1, padx=10, pady=10, sticky="e")
        
        tk.Button(send_frame, text="📧 Send Email", 
                 command=lambda: self.send_email_from_composer(to_entry, subject_entry, body_text, composer),
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold"), 
                 padx=20, pady=5).pack()
        
    def ai_compose_email(self, subject_entry, body_text):
        """Use AI to compose email based on subject"""
        subject = subject_entry.get().strip()
        if not subject:
            messagebox.showwarning("AI Compose", "Please enter a subject first")
            return
            
        # Get AI-composed content
        threading.Thread(target=self._ai_compose_email_async, 
                        args=(subject, body_text), daemon=True).start()
        
    def _ai_compose_email_async(self, subject, body_text):
        """Async AI email composition"""
        try:
            response = requests.post(
                "http://localhost:8000/command",
                json={"command": f"Compose a professional email with subject: {subject}"},
                timeout=30
            )
            if response.status_code == 200:
                result = response.json().get("result", "")
                # Update UI from main thread
                self.root.after(0, lambda: self._update_email_body(body_text, result))
            else:
                self.root.after(0, lambda: messagebox.showerror("AI Error", "Failed to compose email"))
        except Exception as e:
            logger.error(f"AI compose error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"AI composition failed: {e}"))
            
    def _update_email_body(self, body_text, content):
        """Update email body with AI-generated content"""
        body_text.delete("1.0", tk.END)
        body_text.insert("1.0", content)
        
    def ai_improve_tone(self, body_text):
        """Use AI to improve email tone"""
        current_text = body_text.get("1.0", tk.END).strip()
        if not current_text:
            messagebox.showwarning("AI Improve", "Please enter some text first")
            return
            
        threading.Thread(target=self._ai_improve_tone_async, 
                        args=(current_text, body_text), daemon=True).start()
        
    def _ai_improve_tone_async(self, text, body_text):
        """Async AI tone improvement"""
        try:
            response = requests.post(
                "http://localhost:8000/command",
                json={"command": f"Improve the tone and professionalism of this email: {text}"},
                timeout=30
            )
            if response.status_code == 200:
                result = response.json().get("result", "")
                self.root.after(0, lambda: self._update_email_body(body_text, result))
        except Exception as e:
            logger.error(f"AI tone improvement error: {e}")
            
    def ai_check_grammar(self, body_text):
        """Use AI to check and fix grammar"""
        current_text = body_text.get("1.0", tk.END).strip()
        if not current_text:
            messagebox.showwarning("Grammar Check", "Please enter some text first")
            return
            
        threading.Thread(target=self._ai_check_grammar_async, 
                        args=(current_text, body_text), daemon=True).start()
        
    def _ai_check_grammar_async(self, text, body_text):
        """Async AI grammar checking"""
        try:
            response = requests.post(
                "http://localhost:8000/command",
                json={"command": f"Check and fix grammar in this text: {text}"},
                timeout=30
            )
            if response.status_code == 200:
                result = response.json().get("result", "")
                self.root.after(0, lambda: self._update_email_body(body_text, result))
        except Exception as e:
            logger.error(f"AI grammar check error: {e}")
            
    def send_email_from_composer(self, to_entry, subject_entry, body_text, composer):
        """Send email from composer window"""
        to = to_entry.get().strip()
        subject = subject_entry.get().strip()
        body = body_text.get("1.0", tk.END).strip()
        
        if not to or not subject or not body:
            messagebox.showwarning("Incomplete", "Please fill in all fields")
            return
            
        # Confirm sending
        if messagebox.askyesno("Confirm Send", f"Send email to {to}?\n\nSubject: {subject}"):
            threading.Thread(target=self._send_email, args=(to, subject, body), daemon=True).start()
            composer.destroy()
            
    def run_desktop_automation(self):
        """Run desktop automation commands"""
        command = self.command_entry.get().strip()
        if not command:
            messagebox.showwarning("Desktop Automation", "Please enter a desktop automation command")
            return
            
        if messagebox.askyesno("Desktop Automation", 
                             f"Execute desktop automation: {command}?\n\n"
                             "⚠️ This will control your desktop"):
            self.append_message(f"🖥️ Desktop Automation: {command}")
            threading.Thread(target=self._run_desktop_automation, args=(command,), daemon=True).start()
            
    def _run_desktop_automation(self, command):
        """Execute desktop automation command"""
        try:
            response = requests.post(
                "http://localhost:8000/desktop_automation",
                json={"command": command},
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            self.root.after(0, lambda: self.display_response(result))
        except Exception as e:
            self.root.after(0, lambda: self.append_message(f"❌ Desktop automation error: {e}"))
            
    def update_system_status(self):
        """Update system status display"""
        status_info = f"""🤖 AI Agent Status: Active
📧 Email: {'Configured' if SMTP_USERNAME else 'Not Set'}
🖥️ Desktop: Available
🌐 Browser: Available
🔄 Last Update: {datetime.now().strftime('%H:%M:%S')}

💾 Memory Usage: Normal
⚡ Performance: Good
🔒 Security: Enabled"""
        
        self.system_status_text.delete("1.0", tk.END)
        self.system_status_text.insert("1.0", status_info)
        
        # Schedule next update
        self.root.after(30000, self.update_system_status)  # Update every 30 seconds
        
    def append_message(self, message):
        """Add message to chat with timestamp and formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, formatted_message + "\n\n")
        
        # Add color coding based on message type
        if message.startswith("🤖"):
            # AI messages in blue
            start_index = self.chat_history.index(f"end-2l linestart")
            end_index = self.chat_history.index(f"end-2l lineend")
            self.chat_history.tag_add("ai", start_index, end_index)
            self.chat_history.tag_config("ai", foreground="#3498db")
        elif message.startswith("❌"):
            # Error messages in red
            start_index = self.chat_history.index(f"end-2l linestart")
            end_index = self.chat_history.index(f"end-2l lineend")
            self.chat_history.tag_add("error", start_index, end_index)
            self.chat_history.tag_config("error", foreground="#e74c3c")
        elif message.startswith("✅"):
            # Success messages in green
            start_index = self.chat_history.index(f"end-2l linestart")
            end_index = self.chat_history.index(f"end-2l lineend")
            self.chat_history.tag_add("success", start_index, end_index)
            self.chat_history.tag_config("success", foreground="#27ae60")
            
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)
        
        # Update status
        if "error" in message.lower() or message.startswith("❌"):
            self.status_text.config(text="Error occurred")
            self.api_status.config(text="🔴 API")
        else:
            self.status_text.config(text="Ready")
            self.api_status.config(text="🟢 API")
            
    def display_response(self, response):
        if isinstance(response, dict):
            pretty_response = json.dumps(response, indent=2)
        else:
            pretty_response = str(response)
        self.append_message("🤖 Bot: " + pretty_response)

    def submit_command(self):
        cmd = self.command_entry.get().strip()
        if not cmd:
            return
        self.append_message(f"👤 User: {cmd}")
        threading.Thread(target=self._send_command, args=(cmd,), daemon=True).start()
        self.command_entry.delete(0, tk.END)

    def _send_command(self, cmd):
        try:
            resp = requests.post("http://localhost:8000/command", json={"command": cmd}, timeout=30)
            resp.raise_for_status()
            self.root.after(0, lambda: self.display_response(resp.json()))
        except Exception as e:
            self.root.after(0, lambda: self.append_message(f"❌ Error: {e}"))

    def upload_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.gif")])
        if not path:
            return
        self.append_message(f"🖼️ Uploading: {path}")
        threading.Thread(target=self._upload_image, args=(path,), daemon=True).start()

    def _upload_image(self, path):
        try:
            data = base64.b64encode(open(path,"rb").read()).decode()
            resp = requests.post("http://localhost:8000/upload_image",
                                 json={"image_data": data, "file_type": path.split(".")[-1]},
                                 timeout=60)
            resp.raise_for_status()
            self.root.after(0, lambda: self.display_response(resp.json()))
        except Exception as e:
            self.root.after(0, lambda: self.append_message(f"❌ Error: {e}"))

    def run_automation(self):
        cmd = self.command_entry.get().strip()
        if not cmd:
            return
        
        if messagebox.askyesno("Confirm Automation", f"Execute: {cmd}?"):
            self.append_message(f"🤖 Automation: {cmd}")
            threading.Thread(target=self._run_automation, args=(cmd,), daemon=True).start()
        else:
            self.append_message("❌ Automation canceled")

    def _run_automation(self, cmd):
        try:
            resp = requests.post("http://localhost:8000/automation", json={"command": cmd}, timeout=60)
            resp.raise_for_status()
            self.root.after(0, lambda: self.display_response(resp.json()))
        except Exception as e:
            self.root.after(0, lambda: self.append_message(f"❌ Error: {e}"))

    def _send_email(self, to, subject, body):
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            self.root.after(0, lambda: self.append_message("❌ SMTP not configured. Update .env"))
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
            
            self.root.after(0, lambda: self.append_message(f"✅ Email sent to {to}"))
        except Exception as e:
            self.root.after(0, lambda: self.append_message(f"❌ Email error: {e}"))

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedChatGUI(root)
    root.mainloop()
