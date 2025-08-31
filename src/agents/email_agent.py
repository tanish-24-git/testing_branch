import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
import asyncio
import logging
import re
from email.mime.text import MIMEText
from typing import Dict, Optional, List
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class EmailAgent(BaseAgent):
    def __init__(self, llm_manager, config):
        super().__init__("email", llm_manager, config)
        self.service = self._build_service()

    def _build_service(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return build('gmail', 'v1', credentials=creds)

    async def process_command(self, command: str, context: Dict = None) -> str:
        command_lower = command.lower()
        if "send email" in command_lower:
            match = re.search(r"send email to (\S+) with subject (.+) and body (.+)", command, re.I)
            if match:
                return await self._send_email(match.group(1), match.group(2), match.group(3))
        elif "check emails" in command_lower:
            emails = await self._receive_emails(10)
            return "\n".join([f"From: {e['from']} - Subject: {e['subject']}" for e in emails]) if emails else "No emails"
        elif "schedule email" in command_lower:
            match = re.search(r"schedule email to (\S+) with subject (.+) and body (.+) at (.+)", command, re.I)
            if match:
                return await self._schedule_email(match.group(1), match.group(2), match.group(3), match.group(4))
        elif "auto-reply" in command_lower:
            match = re.search(r"auto-reply to (\S+)", command, re.I)
            if match:
                return await self._auto_reply(match.group(1))
        return await self.llm_manager.process(command, context)

    async def _send_email(self, to: str, subject: str, body: str) -> str:
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            self.service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            return "Email sent"
        except HttpError as e:
            logger.error(str(e))
            return "Send failed"

    async def _receive_emails(self, count: int, label: Optional[str] = None) -> List[Dict]:
        try:
            query_params = {'userId': 'me', 'maxResults': count}
            if label:
                query_params['labelIds'] = [label.upper()]  # Labels like 'INBOX' or 'SENT' are uppercase
            results = self.service.users().messages().list(**query_params).execute()
            messages = results.get('messages', [])
            emails = []
            for msg in messages:
                msg_data = self.service.users().messages().get(userId='me', id=msg['id'], format='minimal').execute()
                headers = {h['name']: h['value'] for h in msg_data.get('payload', {}).get('headers', [])}
                emails.append({
                    'id': msg['id'],
                    'from': headers.get('From'),
                    'subject': headers.get('Subject'),
                    'snippet': msg_data.get('snippet')
                })
            return emails
        except HttpError as e:
            logger.error(str(e))
            return []

    async def _schedule_email(self, to: str, subject: str, body: str, time_str: str) -> str:
        try:
            send_time = datetime.fromisoformat(time_str)
            delay = (send_time - datetime.now()).total_seconds()
            if delay > 0:
                asyncio.create_task(self._delayed_send(delay, to, subject, body))
                return "Scheduled"
            return "Invalid time"
        except ValueError:
            return "Invalid format"

    async def _delayed_send(self, delay: float, to: str, subject: str, body: str):
        await asyncio.sleep(delay)
        await self._send_email(to, subject, body)

    async def _auto_reply(self, email_id: str) -> str:
        try:
            msg = self.service.users().messages().get(userId='me', id=email_id).execute()
            original_body = msg['snippet']
            reply_prompt = f"Generate reply to: {original_body}"
            reply_body = await self.llm_manager.process(reply_prompt)
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}
            to = headers.get('From')
            subject = "Re: " + headers.get('Subject', '')
            return await self._send_email(to, subject, reply_body)
        except HttpError as e:
            logger.error(str(e))
            return "Auto-reply failed"