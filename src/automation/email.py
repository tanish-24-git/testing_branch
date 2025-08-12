# src/automation/email.py
import logging
import smtplib
from email.mime.text import MIMEText
from src.settings import settings
import platform
import os
from src.automation.windows import WindowsAutomation  # Import for Gmail API fallback

logger = logging.getLogger(__name__)

from src.pipelines.handlers import BaseHandler

class EmailHandler(BaseHandler):
    def __init__(self, intent="email"):
        super().__init__()
        self.intent = intent
        self.windows_automation = WindowsAutomation() if platform.system() == "Windows" else None
        self.use_gmail_api = platform.system() == "Windows" and os.path.exists("credentials.json")

    def can_handle(self, intent, entities, context):
        return intent == self.intent or context.get("is_email") or "send email" in intent

    def handle(self, command, intent, entities, context):
        to = entities.get("to")
        subject = entities.get("subject", "No Subject")
        body = entities.get("body", context.get("screen_content", ""))
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['To'] = to
        msg['From'] = settings.gmail_user

        # Try SMTP first (cross-platform)
        if settings.gmail_user and settings.gmail_app_password:
            try:
                with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                    server.starttls()
                    server.login(settings.gmail_user, settings.gmail_app_password)
                    server.sendmail(settings.gmail_user, to, msg.as_string())
                return "Email sent"
            except Exception as e:
                logger.error(f"SMTP error: {e}")
                if not self.use_gmail_api:
                    return f"Error sending email: {str(e)}"

        # Fallback to Gmail API on Windows if credentials.json exists
        if self.use_gmail_api:
            try:
                result = self.windows_automation.send_email(to, subject, body)
                return result
            except Exception as e:
                logger.error(f"Gmail API error: {e}")
                return f"Error sending email via Gmail API: {str(e)}"

        return "Error: No valid email configuration found"