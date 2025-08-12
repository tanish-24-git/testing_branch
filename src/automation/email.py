# New file for cross-platform email
import logging
import smtplib
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

from src.pipelines.handlers import BaseHandler

class EmailHandler(BaseHandler):
    def __init__(self, intent="email"):
        super().__init__()
        self.intent = intent
        # Configurable SMTP settings

    def can_handle(self, intent, entities, context):
        return intent == self.intent or context.get("is_email") or "send email" in intent

    def handle(self, command, intent, entities, context):
        to = entities.get("to")
        subject = entities.get("subject")
        body = entities.get("body", context.get("screen_content"))
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['To'] = to
        # Send via SMTP (assume configured)
        with smtplib.SMTP('localhost') as server:  # Placeholder
            server.sendmail("from@example.com", to, msg.as_string())
        return "Email sent"