"""
Email Automation Module - Enhanced email operations
"""

import asyncio
import logging
import smtplib
import imaplib
import email
import os
from datetime import datetime
from typing import Dict, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class EmailAutomation:
    """
    Enhanced email automation with SMTP and IMAP support
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Email configuration
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        self.imap_port = int(os.getenv("IMAP_PORT", "993"))
        self.username = os.getenv("SMTP_USERNAME", "")
        self.password = os.getenv("SMTP_PASSWORD", "")
        
        logger.info("Email automation initialized")
    
    async def send_email(self, to: str, subject: str, body: str, html_body: str = None) -> str:
        """Send email via SMTP"""
        try:
            if not self.username or not self.password:
                return "❌ Email credentials not configured. Set SMTP_USERNAME and SMTP_PASSWORD in .env"
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = to
            msg['Subject'] = subject
            
            # Add text body
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to}")
            return f"✅ Email sent to {to}"
            
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return f"❌ Email send failed: {e}"
    
    async def check_emails(self, count: int = 5) -> str:
        """Check recent emails"""
        try:
            if not self.username or not self.password:
                return "❌ Email credentials not configured"
            
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.username, self.password)
            mail.select('INBOX')
            
            # Search for recent emails
            status, messages = mail.search(None, 'ALL')
            email_ids = messages[0].split()
            
            if not email_ids:
                return "📭 No emails found"
            
            recent_emails = []
            for email_id in email_ids[-count:]:  # Get latest emails
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                email_message = email.message_from_bytes(msg_data[0][1])
                
                subject = email_message.get('Subject', 'No Subject')
                from_addr = email_message.get('From', 'Unknown')
                date = email_message.get('Date', 'Unknown')
                
                recent_emails.append({
                    'subject': subject,
                    'from': from_addr,
                    'date': date
                })
            
            mail.close()
            mail.logout()
            
            # Format response
            if recent_emails:
                result = f"📧 Found {len(recent_emails)} recent emails:\n\n"
                for i, email_info in enumerate(recent_emails, 1):
                    result += f"{i}. From: {email_info['from']}\n"
                    result += f"   Subject: {email_info['subject']}\n"
                    result += f"   Date: {email_info['date']}\n\n"
                return result
            else:
                return "📭 No recent emails found"
            
        except Exception as e:
            logger.error(f"Email check failed: {e}")
            return f"❌ Email check failed: {e}"