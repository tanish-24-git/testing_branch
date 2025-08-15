"""
Email AI Agent - Intelligent email handling with auto-reply capabilities
"""

import asyncio
import logging
import smtplib
import imaplib
import email
import re
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import email.utils

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class EmailAgent(BaseAgent):
    """
    AI Agent for intelligent email operations
    Features:
    - Send emails with AI assistance
    - Read and monitor incoming emails
    - Generate intelligent auto-replies
    - Email sentiment analysis
    - Priority detection
    """
    
    def __init__(self, llm_manager=None, config: Dict = None):
        super().__init__("email_agent", llm_manager, config)
        
        # Email configuration from environment
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        self.imap_port = int(os.getenv("IMAP_PORT", "993"))
        self.username = os.getenv("SMTP_USERNAME", "")
        self.password = os.getenv("SMTP_PASSWORD", "")
        
        # Agent configuration
        self.check_interval = int(os.getenv("EMAIL_CHECK_INTERVAL", "300"))  # 5 minutes
        self.auto_reply_enabled = os.getenv("EMAIL_AUTO_REPLY", "false").lower() == "true"
        self.max_history = int(os.getenv("MAX_EMAIL_HISTORY", "50"))
        self.context_window = int(os.getenv("EMAIL_CONTEXT_WINDOW", "10"))
        
        # Email storage
        self.recent_emails = []
        self.sent_emails = []
        self.pending_replies = []
        
        # Monitoring state
        self.monitoring_active = False
        self.last_check = None
        
    async def initialize(self) -> bool:
        """Initialize email agent"""
        try:
            # Validate configuration
            if not self.username or not self.password:
                logger.warning("Email credentials not configured")
                return False
            
            # Test SMTP connection
            smtp_test = await self._test_smtp_connection()
            if not smtp_test:
                logger.error("SMTP connection test failed")
                return False
            
            # Test IMAP connection
            imap_test = await self._test_imap_connection()
            if not imap_test:
                logger.warning("IMAP connection test failed - email reading unavailable")
            
            logger.info("Email agent initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize email agent: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup email agent resources"""
        self.monitoring_active = False
        logger.info("Email agent cleanup completed")
    
    async def process_command(self, command: str, context: Dict[str, Any] = None) -> str:
        """Process email-related commands"""
        try:
            self.last_activity = datetime.now()
            command_lower = command.lower()
            
            # Enhanced email parsing with better regex
            if any(keyword in command_lower for keyword in ["send email", "email", "mail"]):
                return await self._handle_send_email(command)
            
            elif "check email" in command_lower or "read email" in command_lower:
                return await self._handle_check_emails()
            
            elif "reply to" in command_lower:
                return await self._handle_reply_email(command)
            
            elif "start monitoring" in command_lower:
                return await self._handle_start_monitoring()
            
            elif "stop monitoring" in command_lower:
                return await self._handle_stop_monitoring()
            
            elif "email status" in command_lower:
                return self._handle_email_status()
            
            else:
                # Use AI to understand the email intent
                return await self._handle_ai_email_command(command, context)
                
        except Exception as e:
            return await self.handle_error(e, "processing email command")
    
    async def _handle_send_email(self, command: str) -> str:
        """Handle email sending with improved parsing"""
        try:
            # Enhanced regex patterns for better email parsing
            patterns = [
                # Full format: send email to user@example.com with subject Hello and body Message text
                r"send email to\s+([^\s@]+@[^\s@]+\.[^\s@]+)\s+with subject\s+(.+?)\s+and body\s+(.+)",
                
                # Subject only: send email to user@example.com with subject Hello
                r"send email to\s+([^\s@]+@[^\s@]+\.[^\s@]+)\s+with subject\s+(.+)",
                
                # Email only: send email to user@example.com
                r"send email to\s+([^\s@]+@[^\s@]+\.[^\s@]+)",
                
                # Alternative format: email user@example.com about subject with message
                r"email\s+([^\s@]+@[^\s@]+\.[^\s@]+)\s+about\s+(.+?)\s+with\s+(.+)",
                
                # Simple format: email user@example.com
                r"email\s+([^\s@]+@[^\s@]+\.[^\s@]+)"
            ]
            
            recipient = None
            subject = "Message from AI Assistant"
            body = "This is an automated message from your AI assistant."
            
            for pattern in patterns:
                match = re.search(pattern, command, re.IGNORECASE)
                if match:
                    recipient = match.group(1)
                    if len(match.groups()) >= 2:
                        subject = match.group(2).strip()
                    if len(match.groups()) >= 3:
                        body = match.group(3).strip()
                    break
            
            if not recipient:
                return "❌ Could not parse email command. Use format: 'send email to user@example.com with subject Hello and body Your message here'"
            
            # AI enhancement of email content
            if self.llm_manager:
                enhanced_email = await self._enhance_email_content(recipient, subject, body, command)
                if enhanced_email:
                    subject = enhanced_email.get("subject", subject)
                    body = enhanced_email.get("body", body)
            
            # Send the email
            result = await self._send_email(recipient, subject, body)
            
            # Add to history
            self.add_to_history(command, result, {
                "recipient": recipient,
                "subject": subject,
                "action": "send_email"
            })
            
            return result
            
        except Exception as e:
            return await self.handle_error(e, "sending email")
    
    async def _enhance_email_content(self, recipient: str, subject: str, body: str, original_command: str) -> Dict[str, str]:
        """Use AI to enhance email content"""
        try:
            enhancement_prompt = f"""
            Enhance this email for better clarity and professionalism:
            
            Original command: {original_command}
            Recipient: {recipient}
            Subject: {subject}
            Body: {body}
            
            Please improve the subject and body while maintaining the original intent.
            Return ONLY a JSON object with 'subject' and 'body' keys.
            Make it professional but friendly.
            """
            
            response = await self.generate_response(enhancement_prompt)
            
            # Try to parse JSON response
            import json
            try:
                enhanced = json.loads(response)
                if isinstance(enhanced, dict) and "subject" in enhanced and "body" in enhanced:
                    return enhanced
            except:
                pass
            
            return None
            
        except Exception as e:
            logger.warning(f"Email enhancement failed: {e}")
            return None
    
    async def _send_email(self, recipient: str, subject: str, body: str) -> str:
        """Send email via SMTP"""
        try:
            # Validate email format
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', recipient):
                return f"❌ Invalid email address: {recipient}"
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = recipient
            msg['Subject'] = subject
            msg['Date'] = email.utils.formatdate(localtime=True)
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            # Store in sent emails
            sent_email = {
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "timestamp": datetime.now().isoformat(),
                "message_id": msg.get('Message-ID')
            }
            self.sent_emails.append(sent_email)
            
            # Keep only recent sent emails
            if len(self.sent_emails) > self.max_history:
                self.sent_emails = self.sent_emails[-self.max_history:]
            
            logger.info(f"Email sent successfully to {recipient}")
            return f"✅ Email sent to {recipient}\n📧 Subject: {subject}\n📝 Body: {body[:100]}{'...' if len(body) > 100 else ''}"
            
        except smtplib.SMTPAuthenticationError:
            return "❌ Email authentication failed. Check your email credentials."
        except smtplib.SMTPException as e:
            return f"❌ Email sending failed: {str(e)}"
        except Exception as e:
            return f"❌ Unexpected error sending email: {str(e)}"
    
    async def _handle_check_emails(self) -> str:
        """Check and read recent emails"""
        try:
            emails = await self._fetch_recent_emails()
            if not emails:
                return "📬 No new emails found"
            
            # Format email summary
            summary = f"📧 Found {len(emails)} recent email(s):\n\n"
            
            for i, email_data in enumerate(emails[:5], 1):  # Show max 5 emails
                summary += f"{i}. From: {email_data['from']}\n"
                summary += f"   Subject: {email_data['subject']}\n"
                summary += f"   Date: {email_data['date']}\n"
                summary += f"   Preview: {email_data['preview'][:100]}...\n\n"
            
            # AI analysis of emails
            if self.llm_manager and emails:
                analysis = await self._analyze_emails(emails)
                summary += f"🤖 AI Analysis:\n{analysis}"
            
            return summary
            
        except Exception as e:
            return await self.handle_error(e, "checking emails")
    
    async def _fetch_recent_emails(self, count: int = 10) -> List[Dict]:
        """Fetch recent emails via IMAP"""
        try:
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.username, self.password)
            mail.select('INBOX')
            
            # Search for recent emails
            search_criteria = 'ALL'
            status, messages = mail.search(None, search_criteria)
            
            if status != 'OK':
                return []
            
            email_ids = messages[0].split()
            emails = []
            
            # Fetch recent emails (latest first)
            for email_id in email_ids[-count:]:
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status == 'OK':
                        email_message = email.message_from_bytes(msg_data[0][1])
                        
                        # Extract email details
                        email_info = self._parse_email(email_message)
                        if email_info:
                            emails.append(email_info)
                            
                except Exception as e:
                    logger.warning(f"Error processing email {email_id}: {e}")
                    continue
            
            mail.close()
            mail.logout()
            
            # Store recent emails
            self.recent_emails = emails
            self.last_check = datetime.now()
            
            return emails[::-1]  # Return in reverse order (newest first)
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []
    
    def _parse_email(self, email_message) -> Optional[Dict]:
        """Parse email message and extract relevant information"""
        try:
            # Get subject
            subject = email_message.get('Subject', 'No Subject')
            if subject:
                subject = self._decode_header(subject)
            
            # Get sender
            from_header = email_message.get('From', 'Unknown Sender')
            from_name, from_email = email.utils.parseaddr(from_header)
            from_display = from_name if from_name else from_email
            
            # Get date
            date_str = email_message.get('Date', '')
            try:
                date_parsed = email.utils.parsedate_to_datetime(date_str)
                date_formatted = date_parsed.strftime('%Y-%m-%d %H:%M')
            except:
                date_formatted = date_str
            
            # Get body
            body = self._extract_email_body(email_message)
            preview = body[:200] if body else "No content"
            
            return {
                "subject": subject,
                "from": from_display,
                "from_email": from_email,
                "date": date_formatted,
                "body": body,
                "preview": preview,
                "message_id": email_message.get('Message-ID', ''),
                "in_reply_to": email_message.get('In-Reply-To', ''),
                "references": email_message.get('References', '')
            }
            
        except Exception as e:
            logger.warning(f"Error parsing email: {e}")
            return None
    
    def _decode_header(self, header_value: str) -> str:
        """Decode email header"""
        try:
            decoded_parts = decode_header(header_value)
            decoded_string = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_string += part.decode(encoding or 'utf-8')
                else:
                    decoded_string += part
            return decoded_string
        except:
            return header_value
    
    def _extract_email_body(self, email_message) -> str:
        """Extract email body text"""
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            return payload.decode('utf-8', errors='ignore')
            else:
                payload = email_message.get_payload(decode=True)
                if payload:
                    return payload.decode('utf-8', errors='ignore')
            return ""
        except Exception as e:
            logger.warning(f"Error extracting email body: {e}")
            return ""
    
    async def _analyze_emails(self, emails: List[Dict]) -> str:
        """AI analysis of emails"""
        try:
            email_summaries = []
            for email_data in emails[:5]:  # Analyze max 5 emails
                summary = f"From: {email_data['from']}, Subject: {email_data['subject']}, Preview: {email_data['preview'][:100]}"
                email_summaries.append(summary)
            
            analysis_prompt = f"""
            Analyze these recent emails and provide insights:
            
            {chr(10).join(email_summaries)}
            
            Please provide:
            1. Priority assessment (high/medium/low)
            2. Sentiment analysis
            3. Action items or responses needed
            4. Summary of key topics
            
            Keep response concise and actionable.
            """
            
            analysis = await self.generate_response(analysis_prompt)
            return analysis
            
        except Exception as e:
            logger.warning(f"Email analysis failed: {e}")
            return "Analysis unavailable"
    
    async def _handle_reply_email(self, command: str) -> str:
        """Handle email reply generation"""
        try:
            if not self.recent_emails:
                return "❌ No recent emails to reply to. Check emails first."
            
            # Get the most recent email
            latest_email = self.recent_emails[0]
            
            # Extract reply intent from command
            reply_intent = self._extract_reply_intent(command)
            
            # Generate AI reply
            reply_content = await self._generate_reply(latest_email, reply_intent)
            
            if not reply_content:
                return "❌ Failed to generate reply"
            
            # Show generated reply for approval
            approval_message = f"""
📧 Generated Reply for: {latest_email['subject']}
👤 To: {latest_email['from']}

📝 Subject: Re: {latest_email['subject']}

📄 Body:
{reply_content}

✅ Send this reply? (Respond with 'yes' to send, 'no' to cancel, or provide modifications)
"""
            
            # Store pending reply
            pending_reply = {
                "to": latest_email['from_email'],
                "subject": f"Re: {latest_email['subject']}",
                "body": reply_content,
                "in_reply_to": latest_email['message_id'],
                "timestamp": datetime.now().isoformat()
            }
            self.pending_replies.append(pending_reply)
            
            return approval_message
            
        except Exception as e:
            return await self.handle_error(e, "generating email reply")
    
    def _extract_reply_intent(self, command: str) -> str:
        """Extract the intended reply from command"""
        # Remove "reply to" part and get the rest
        patterns = [
            r"reply to.*?with\s+(.+)",
            r"reply.*?saying\s+(.+)",
            r"reply.*?that\s+(.+)",
            r"reply to.*?(.+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "acknowledgment"  # Default intent
    
    async def _generate_reply(self, original_email: Dict, intent: str) -> str:
        """Generate AI reply to email"""
        try:
            reply_prompt = f"""
            Generate a professional email reply based on:
            
            Original Email:
            From: {original_email['from']}
            Subject: {original_email['subject']}
            Body: {original_email['body'][:500]}
            
            Reply Intent: {intent}
            
            Please generate a professional, helpful reply that:
            1. Acknowledges the original email
            2. Addresses the main points
            3. Provides appropriate response based on intent
            4. Maintains professional tone
            5. Is concise but complete
            
            Return only the reply body text, no headers.
            """
            
            reply = await self.generate_response(reply_prompt)
            return reply
            
        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            return None
    
    async def _handle_start_monitoring(self) -> str:
        """Start email monitoring"""
        if self.monitoring_active:
            return "📧 Email monitoring is already active"
        
        self.monitoring_active = True
        asyncio.create_task(self._monitoring_loop())
        return f"✅ Email monitoring started (checking every {self.check_interval} seconds)"
    
    async def _handle_stop_monitoring(self) -> str:
        """Stop email monitoring"""
        self.monitoring_active = False
        return "✅ Email monitoring stopped"
    
    async def _monitoring_loop(self):
        """Background email monitoring loop"""
        while self.monitoring_active:
            try:
                await asyncio.sleep(self.check_interval)
                if not self.monitoring_active:
                    break
                
                # Check for new emails
                new_emails = await self._fetch_recent_emails(5)
                
                # Process new emails for auto-reply if enabled
                if self.auto_reply_enabled and new_emails:
                    await self._process_auto_replies(new_emails)
                
            except Exception as e:
                logger.error(f"Error in email monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _process_auto_replies(self, emails: List[Dict]):
        """Process emails for automatic replies"""
        for email_data in emails:
            try:
                # Check if we should auto-reply
                if self._should_auto_reply(email_data):
                    reply = await self._generate_auto_reply(email_data)
                    if reply:
                        # Note: In production, add user confirmation here
                        await self._send_email(
                            email_data['from_email'],
                            f"Re: {email_data['subject']}",
                            reply
                        )
                        logger.info(f"Auto-reply sent to {email_data['from_email']}")
                        
            except Exception as e:
                logger.error(f"Error processing auto-reply: {e}")
    
    def _should_auto_reply(self, email_data: Dict) -> bool:
        """Determine if email should receive auto-reply"""
        # Don't auto-reply to:
        # - Emails from yourself
        # - Auto-generated emails
        # - Out of office replies
        # - Mailing lists
        
        from_email = email_data.get('from_email', '').lower()
        subject = email_data.get('subject', '').lower()
        
        if from_email == self.username.lower():
            return False
        
        auto_generated_indicators = [
            'noreply', 'no-reply', 'donotreply', 'auto-reply',
            'out of office', 'vacation', 'away', 'bounce'
        ]
        
        if any(indicator in from_email or indicator in subject 
               for indicator in auto_generated_indicators):
            return False
        
        return True
    
    async def _generate_auto_reply(self, email_data: Dict) -> str:
        """Generate automatic reply"""
        try:
            auto_reply_prompt = f"""
            Generate a brief, professional auto-reply for this email:
            
            From: {email_data['from']}
            Subject: {email_data['subject']}
            Content: {email_data['preview']}
            
            The auto-reply should:
            1. Acknowledge receipt
            2. Be brief and professional
            3. Indicate this is an automated response
            4. Provide helpful information if possible
            
            Keep it under 100 words.
            """
            
            reply = await self.generate_response(auto_reply_prompt)
            return reply
            
        except Exception as e:
            logger.error(f"Error generating auto-reply: {e}")
            return None
    
    def _handle_email_status(self) -> str:
        """Get email agent status"""
        status = f"""
📧 Email Agent Status:
━━━━━━━━━━━━━━━━━━━━
🔧 Configuration:
   • SMTP: {self.smtp_server}:{self.smtp_port}
   • IMAP: {self.imap_server}:{self.imap_port}
   • Username: {self.username}
   • Credentials: {'✅ Configured' if self.password else '❌ Missing'}

📊 Statistics:
   • Recent emails: {len(self.recent_emails)}
   • Sent emails: {len(self.sent_emails)}
   • Pending replies: {len(self.pending_replies)}
   • Last check: {self.last_check.strftime('%Y-%m-%d %H:%M:%S') if self.last_check else 'Never'}

⚙️ Settings:
   • Monitoring: {'🟢 Active' if self.monitoring_active else '🔴 Inactive'}
   • Auto-reply: {'🟢 Enabled' if self.auto_reply_enabled else '🔴 Disabled'}
   • Check interval: {self.check_interval} seconds
   • Context window: {self.context_window} emails
"""
        return status
    
    async def _handle_ai_email_command(self, command: str, context: Dict[str, Any] = None) -> str:
        """Handle general email commands using AI"""
        try:
            ai_prompt = f"""
            I am an AI email assistant. The user said: "{command}"
            
            This seems to be an email-related request. Based on the command, determine what the user wants to do:
            
            Available email actions:
            - Send email
            - Check/read emails  
            - Reply to emails
            - Start/stop monitoring
            - Get email status
            
            If the request is unclear, ask for clarification with specific examples.
            If it's a valid email action, provide helpful guidance.
            """
            
            response = await self.generate_response(ai_prompt, context)
            return f"🤖 Email Assistant: {response}"
            
        except Exception as e:
            return await self.handle_error(e, "processing AI email command")
    
    async def _test_smtp_connection(self) -> bool:
        """Test SMTP connection"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
            return True
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return False
    
    async def _test_imap_connection(self) -> bool:
        """Test IMAP connection"""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.username, self.password)
            mail.logout()
            return True
        except Exception as e:
            logger.error(f"IMAP connection test failed: {e}")
            return False