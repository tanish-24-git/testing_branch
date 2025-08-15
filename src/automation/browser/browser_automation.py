# FIXED src/automation/browser_automation.py - Enhanced with multiple fallback methods

import os
import sys
import asyncio
import logging
import smtplib
import webbrowser
import subprocess
import platform
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
import re

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.config import config

logger = logging.getLogger(__name__)

class browserAutomation:
    def __init__(self):
        self.browser = None
        self.page = None
        self.playwright = None
        self.browser_type = config.get("automation", {}).get("browser", "chrome").lower()
        self.headless = config.get("automation", {}).get("headless", True)
        self.timeout = config.get("automation", {}).get("timeout", 30000)
        
        # SMTP Configuration - Add these to your .env file
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")  # Use app password for Gmail
        
        logger.info(f"Initialized browser automation with {self.browser_type} browser")

    async def start_browser(self):
        """Enhanced browser startup with better error handling"""
        logger.info(f"Starting {self.browser_type} browser...")
        
        try:
            # Import playwright here to handle import errors gracefully
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            
            # Browser-specific launch options
            launch_options = {
                "headless": self.headless,
                "args": [
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-setuid-sandbox",
                    "--disable-gpu",
                    "--disable-web-security",
                    "--allow-running-insecure-content",
                    "--disable-features=VizDisplayCompositor"
                ]
            }
            
            # Launch browser based on type
            if self.browser_type in ["chrome", "chromium"]:
                self.browser = await self.playwright.chromium.launch(**launch_options)
            elif self.browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(**launch_options)
            elif self.browser_type in ["safari", "webkit"]:
                self.browser = await self.playwright.webkit.launch(**launch_options)
            else:
                # Default to chromium
                logger.warning(f"Unknown browser type {self.browser_type}, defaulting to chromium")
                self.browser = await self.playwright.chromium.launch(**launch_options)
            
            # Create browser context and page
            context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            self.page = await context.new_page()
            await self.page.set_default_timeout(self.timeout)
            
            logger.info(f"Browser {self.browser_type} started successfully")
            return True
            
        except ImportError as e:
            logger.error(f"Playwright not installed properly: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False

    async def close_browser(self):
        """Safely close browser and cleanup resources"""
        try:
            if self.page:
                await self.page.close()
                logger.debug("Page closed")
            
            if self.browser:
                await self.browser.close()
                logger.debug("Browser closed")
            
            if self.playwright:
                await self.playwright.stop()
                logger.debug("Playwright stopped")
                
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
        finally:
            self.page = None
            self.browser = None
            self.playwright = None

    def open_url_system_browser(self, url: str) -> str:
        """Fallback method: Open URL in system default browser"""
        try:
            logger.info(f"Opening {url} in system default browser")
            webbrowser.open(url)
            return f"✅ Opened {url} in system default browser"
        except Exception as e:
            logger.error(f"Failed to open URL in system browser: {e}")
            return f"❌ Failed to open {url}: {e}"

    def open_url_command_line(self, url: str) -> str:
        """Alternative method: Open URL using command line"""
        try:
            system = platform.system().lower()
            
            if system == "windows":
                subprocess.run(["start", url], shell=True, check=True)
            elif system == "darwin":  # macOS
                subprocess.run(["open", url], check=True)
            elif system == "linux":
                subprocess.run(["xdg-open", url], check=True)
            else:
                return f"❌ Unsupported operating system: {system}"
            
            logger.info(f"Opened {url} using command line on {system}")
            return f"✅ Opened {url} using {system} command line"
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Command line browser opening failed: {e}")
            return f"❌ Command line method failed: {e}"
        except Exception as e:
            logger.error(f"Unexpected error in command line method: {e}")
            return f"❌ Unexpected error: {e}"

    async def navigate(self, url: str) -> str:
        """Navigate to URL with Playwright"""
        if not self.page:
            return "❌ Browser not initialized"
        
        try:
            logger.info(f"Navigating to {url}")
            await self.page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)
            title = await self.page.title()
            logger.info(f"Successfully navigated to {url}, page title: {title}")
            return f"✅ Navigated to {url}\nPage title: {title}"
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return f"❌ Navigation failed: {e}"

    async def click_element(self, selector: str) -> str:
        """Click element by selector"""
        if not self.page:
            return "❌ Browser not initialized"
        
        try:
            logger.info(f"Clicking element: {selector}")
            await self.page.wait_for_selector(selector, timeout=10000)
            await self.page.click(selector)
            logger.info(f"Successfully clicked {selector}")
            return f"✅ Clicked element: {selector}"
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return f"❌ Click failed for {selector}: {e}"

    async def fill_form(self, fields: Dict[str, str]) -> str:
        """Fill form fields"""
        if not self.page:
            return "❌ Browser not initialized"
        
        try:
            logger.info(f"Filling form with {len(fields)} fields")
            results = []
            
            for field_selector, value in fields.items():
                await self.page.wait_for_selector(field_selector, timeout=10000)
                await self.page.fill(field_selector, value)
                results.append(f"  • {field_selector}: {value}")
                
            logger.info("Form filled successfully")
            return f"✅ Form filled:\n" + "\n".join(results)
            
        except Exception as e:
            logger.error(f"Form fill failed: {e}")
            return f"❌ Form fill failed: {e}"

    async def submit_form(self, selector: str = None) -> str:
        """Submit form"""
        if not self.page:
            return "❌ Browser not initialized"
        
        try:
            logger.info(f"Submitting form: {selector}")
            if selector:
                await self.page.click(selector)
            else:
                await self.page.evaluate("document.querySelector('form').submit()")
            return "✅ Form submitted"
        except Exception as e:
            logger.error(f"Form submission failed: {e}")
            return f"❌ Form submission failed: {e}"

    def send_email_smtp(self, recipient: str, subject: str, body: str, html_body: str = None) -> str:
        """Send email using SMTP"""
        try:
            if not self.smtp_username or not self.smtp_password:
                return "❌ SMTP credentials not configured. Set SMTP_USERNAME and SMTP_PASSWORD in .env file"
            
            logger.info(f"Sending email to {recipient}")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_username
            msg['To'] = recipient
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
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {recipient}")
            return f"✅ Email sent to {recipient}\nSubject: {subject}"
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed")
            return "❌ Email authentication failed. Check SMTP credentials"
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return f"❌ Email send failed: {e}"
        except Exception as e:
            logger.error(f"Unexpected email error: {e}")
            return f"❌ Unexpected email error: {e}"

    async def execute_command(self, command: str, llm_manager=None, rag=None) -> str:
        """Enhanced command execution with multiple fallback methods"""
        logger.info(f"Executing automation command: {command}")
        
        # Parse command using LLM if available
        if llm_manager and rag:
            try:
                context = {"rag": rag.retrieve(command)}
                parsed_command = await llm_manager.process(
                    f"Parse this automation command and extract the action and parameters: {command}", 
                    context
                )
                logger.info(f"LLM parsed command: {parsed_command}")
            except Exception as e:
                logger.warning(f"LLM parsing failed: {e}")
        
        command_lower = command.lower()
        
        # Extract URL from command
        url_match = re.search(r'https?://[^\s]+', command)
        url = url_match.group(0) if url_match else None
        
        # 1. Simple navigation/opening URLs
        if any(keyword in command_lower for keyword in ["open", "navigate", "go to", "visit"]):
            if url:
                # Try multiple approaches
                
                # Method 1: Try Playwright first
                if await self.start_browser():
                    try:
                        result = await self.navigate(url)
                        await self.close_browser()
                        return result
                    except Exception as e:
                        logger.warning(f"Playwright method failed: {e}")
                        await self.close_browser()
                
                # Method 2: Fallback to system browser
                system_result = self.open_url_system_browser(url)
                if "✅" in system_result:
                    return system_result
                
                # Method 3: Fallback to command line
                return self.open_url_command_line(url)
            else:
                return "❌ No valid URL found in command"
        
        # 2. Email sending
        elif any(keyword in command_lower for keyword in ["send email", "email", "mail"]):
            # Parse email components
            email_pattern = r"send email to ([^\s]+)(?:\s+with subject (.+?)(?:\s+and body (.+))?)?|email ([^\s@]+@[^\s@]+\.[^\s@]+)"
            match = re.search(email_pattern, command, re.IGNORECASE)
            
            if match:
                recipient = match.group(1) or match.group(4)
                subject = match.group(2) or "Automated Email"
                body = match.group(3) or "This is an automated email from the chat bot."
                
                return self.send_email_smtp(recipient, subject, body)
            else:
                return "❌ Could not parse email command. Use format: 'send email to user@example.com with subject Hello and body How are you?'"
        
        # 3. Advanced browser automation
        elif any(keyword in command_lower for keyword in ["click", "fill", "submit", "screenshot"]):
            if not await self.start_browser():
                return "❌ Could not start browser for advanced automation"
            
            try:
                if "click" in command_lower:
                    selector_match = re.search(r"click\s+(.+)", command, re.IGNORECASE)
                    if selector_match:
                        result = await self.click_element(selector_match.group(1).strip())
                        await self.close_browser()
                        return result
                
                elif "fill form" in command_lower:
                    # Parse form fields: fill form name=John,email=john@example.com
                    fields_match = re.search(r"fill form\s+(.+)", command, re.IGNORECASE)
                    if fields_match:
                        try:
                            field_pairs = fields_match.group(1).split(',')
                            fields = {}
                            for pair in field_pairs:
                                key, value = pair.split('=', 1)
                                fields[key.strip()] = value.strip()
                            result = await self.fill_form(fields)
                            await self.close_browser()
                            return result
                        except ValueError:
                            await self.close_browser()
                            return "❌ Invalid form format. Use: fill form field1=value1,field2=value2"
                
                elif "submit form" in command_lower:
                    result = await self.submit_form()
                    await self.close_browser()
                    return result
                
                await self.close_browser()
                return f"❌ Could not parse advanced automation command: {command}"
                
            except Exception as e:
                await self.close_browser()
                return f"❌ Advanced automation failed: {e}"
        
        # 4. Unknown command
        else:
            return f"❌ Unknown automation command: {command}\n\nSupported commands:\n• open <url>\n• send email to <email> with subject <subject> and body <body>\n• click <selector>\n• fill form field1=value1,field2=value2\n• submit form"

    def open_link_in_default_browser(self, url: str):
        """Legacy method for compatibility"""
        return self.open_url_system_browser(url)