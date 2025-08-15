"""
Desktop Automation Module - Cross-platform desktop control
"""

import os
import sys
import logging
import time
import platform
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import pyautogui
    import pygetwindow as gw
    import psutil
    import pyperclip
    from pynput import mouse, keyboard
    from pynput.mouse import Button, Listener as MouseListener
    from pynput.keyboard import Key, Listener as KeyboardListener
    DESKTOP_AUTOMATION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Desktop automation libraries not available: {e}")
    DESKTOP_AUTOMATION_AVAILABLE = False
    # Create dummy classes to prevent errors
    class pyautogui:
        @staticmethod
        def click(*args, **kwargs): pass
        @staticmethod
        def hotkey(*args, **kwargs): pass
        @staticmethod
        def screenshot(*args, **kwargs): pass
        @staticmethod
        def typewrite(*args, **kwargs): pass
        FAILSAFE = True

class DesktopAutomation:
    """
    Cross-platform desktop automation capabilities
    Features:
    - Window management (find, focus, minimize, maximize)
    - Mouse control (click, scroll, drag)
    - Keyboard automation (type, shortcuts)
    - Screen capture (screenshot, recording)
    - Application control (launch, close)
    - File operations
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.safety_delay = float(os.getenv("DESKTOP_SAFETY_DELAY", "1.0"))
        self.screenshot_dir = os.getenv("SCREENSHOT_DIR", "screenshots")
        self.failsafe_enabled = os.getenv("DESKTOP_FAILSAFE", "true").lower() == "true"
        
        # Ensure screenshot directory exists
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Configure PyAutoGUI if available
        if DESKTOP_AUTOMATION_AVAILABLE:
            pyautogui.FAILSAFE = self.failsafe_enabled
            pyautogui.PAUSE = self.safety_delay
        
        self.system = platform.system().lower()
        logger.info(f"Desktop automation initialized for {self.system}")
    
    def is_available(self) -> bool:
        """Check if desktop automation is available"""
        return DESKTOP_AUTOMATION_AVAILABLE
    
    async def execute_command(self, command: str, llm_manager=None, rag=None) -> str:
        """Execute desktop automation command"""
        if not DESKTOP_AUTOMATION_AVAILABLE:
            return "❌ Desktop automation not available. Install required packages: pip install pyautogui pygetwindow pynput psutil"
        
        try:
            command_lower = command.lower()
            
            # Window management
            if "minimize" in command_lower:
                if "all" in command_lower:
                    return await self.minimize_all_windows()
                else:
                    window_name = self._extract_window_name(command)
                    return await self.minimize_window(window_name)
            
            elif "maximize" in command_lower:
                window_name = self._extract_window_name(command)
                return await self.maximize_window(window_name)
            
            elif "close" in command_lower and "window" in command_lower:
                window_name = self._extract_window_name(command)
                return await self.close_window(window_name)
            
            elif "focus" in command_lower or "switch to" in command_lower:
                window_name = self._extract_window_name(command)
                return await self.focus_window(window_name)
            
            # Application control
            elif "open" in command_lower and any(app in command_lower for app in ["notepad", "calculator", "browser", "terminal"]):
                app_name = self._extract_app_name(command)
                return await self.open_application(app_name)
            
            # Mouse actions
            elif "click" in command_lower:
                coords = self._extract_coordinates(command)
                if coords:
                    return await self.click_at_coordinates(coords[0], coords[1])
                else:
                    return "❌ Please specify coordinates: 'click at 100 200'"
            
            elif "scroll" in command_lower:
                return await self.scroll_action(command)
            
            # Keyboard actions
            elif "type" in command_lower:
                text = self._extract_text_to_type(command)
                return await self.type_text(text)
            
            elif "press" in command_lower:
                keys = self._extract_keys(command)
                return await self.press_keys(keys)
            
            # Screen capture
            elif "screenshot" in command_lower or "capture" in command_lower:
                filename = self._extract_filename(command) or f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                return await self.take_screenshot(filename)
            
            # System information
            elif "list windows" in command_lower:
                return await self.list_windows()
            
            elif "system info" in command_lower:
                return await self.get_system_info()
            
            # File operations
            elif "copy file" in command_lower:
                return await self.copy_file_operation(command)
            
            else:
                # Use AI to interpret complex commands
                if llm_manager:
                    return await self._handle_ai_desktop_command(command, llm_manager)
                else:
                    return f"❌ Unknown desktop command: {command}"
                    
        except Exception as e:
            logger.error(f"Desktop automation error: {e}")
            return f"❌ Desktop automation error: {str(e)}"
    
    async def minimize_window(self, window_name: str = None) -> str:
        """Minimize a specific window or active window"""
        try:
            if window_name:
                windows = gw.getWindowsWithTitle(window_name)
                if not windows:
                    return f"❌ Window '{window_name}' not found"
                window = windows[0]
            else:
                window = gw.getActiveWindow()
                if not window:
                    return "❌ No active window found"
            
            window.minimize()
            return f"✅ Minimized window: {window.title}"
            
        except Exception as e:
            return f"❌ Error minimizing window: {e}"
    
    async def minimize_all_windows(self) -> str:
        """Minimize all windows"""
        try:
            if self.system == "windows":
                pyautogui.hotkey('win', 'm')
            elif self.system == "darwin":  # macOS
                pyautogui.hotkey('cmd', 'option', 'm')
            else:  # Linux
                pyautogui.hotkey('ctrl', 'alt', 'd')
            
            return "✅ Minimized all windows"
            
        except Exception as e:
            return f"❌ Error minimizing all windows: {e}"
    
    async def maximize_window(self, window_name: str = None) -> str:
        """Maximize a specific window"""
        try:
            if window_name:
                windows = gw.getWindowsWithTitle(window_name)
                if not windows:
                    return f"❌ Window '{window_name}' not found"
                window = windows[0]
            else:
                window = gw.getActiveWindow()
                if not window:
                    return "❌ No active window found"
            
            window.maximize()
            return f"✅ Maximized window: {window.title}"
            
        except Exception as e:
            return f"❌ Error maximizing window: {e}"
    
    async def focus_window(self, window_name: str) -> str:
        """Focus/activate a specific window"""
        try:
            windows = gw.getWindowsWithTitle(window_name)
            if not windows:
                # Try partial match
                all_windows = gw.getAllWindows()
                matching_windows = [w for w in all_windows if window_name.lower() in w.title.lower()]
                if not matching_windows:
                    return f"❌ Window '{window_name}' not found"
                windows = matching_windows
            
            window = windows[0]
            window.activate()
            return f"✅ Focused window: {window.title}"
            
        except Exception as e:
            return f"❌ Error focusing window: {e}"
    
    async def close_window(self, window_name: str) -> str:
        """Close a specific window"""
        try:
            windows = gw.getWindowsWithTitle(window_name)
            if not windows:
                return f"❌ Window '{window_name}' not found"
            
            window = windows[0]
            window.close()
            return f"✅ Closed window: {window.title}"
            
        except Exception as e:
            return f"❌ Error closing window: {e}"
    
    async def open_application(self, app_name: str) -> str:
        """Open an application"""
        try:
            app_commands = {
                "notepad": {
                    "windows": "notepad.exe",
                    "darwin": "open -a TextEdit",
                    "linux": "gedit"
                },
                "calculator": {
                    "windows": "calc.exe",
                    "darwin": "open -a Calculator",
                    "linux": "gnome-calculator"
                },
                "browser": {
                    "windows": "start chrome",
                    "darwin": "open -a 'Google Chrome'",
                    "linux": "google-chrome"
                },
                "terminal": {
                    "windows": "cmd",
                    "darwin": "open -a Terminal",
                    "linux": "gnome-terminal"
                }
            }
            
            if app_name not in app_commands:
                return f"❌ Unknown application: {app_name}"
            
            command = app_commands[app_name].get(self.system)
            if not command:
                return f"❌ Application '{app_name}' not supported on {self.system}"
            
            if self.system == "windows":
                os.system(command)
            else:
                subprocess.Popen(command.split())
            
            await self._async_sleep(2)  # Wait for app to open
            return f"✅ Opened {app_name}"
            
        except Exception as e:
            return f"❌ Error opening application: {e}"
    
    async def click_at_coordinates(self, x: int, y: int, button: str = "left") -> str:
        """Click at specific coordinates"""
        try:
            if button.lower() == "right":
                pyautogui.rightClick(x, y)
            else:
                pyautogui.click(x, y)
            
            return f"✅ Clicked at ({x}, {y}) with {button} button"
            
        except Exception as e:
            return f"❌ Error clicking: {e}"
    
    async def scroll_action(self, command: str) -> str:
        """Perform scroll action"""
        try:
            if "up" in command.lower():
                pyautogui.scroll(3)
                direction = "up"
            elif "down" in command.lower():
                pyautogui.scroll(-3)
                direction = "down"
            else:
                pyautogui.scroll(1)
                direction = "up (default)"
            
            return f"✅ Scrolled {direction}"
            
        except Exception as e:
            return f"❌ Error scrolling: {e}"
    
    async def type_text(self, text: str) -> str:
        """Type text"""
        try:
            pyautogui.typewrite(text, interval=0.05)
            return f"✅ Typed: {text[:50]}{'...' if len(text) > 50 else ''}"
            
        except Exception as e:
            return f"❌ Error typing text: {e}"
    
    async def press_keys(self, keys: List[str]) -> str:
        """Press key combination"""
        try:
            if len(keys) == 1:
                pyautogui.press(keys[0])
            else:
                pyautogui.hotkey(*keys)
            
            return f"✅ Pressed keys: {' + '.join(keys)}"
            
        except Exception as e:
            return f"❌ Error pressing keys: {e}"
    
    async def take_screenshot(self, filename: str = None) -> str:
        """Take a screenshot"""
        try:
            if not filename:
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            filepath = os.path.join(self.screenshot_dir, filename)
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            return f"✅ Screenshot saved: {filepath}"
            
        except Exception as e:
            return f"❌ Error taking screenshot: {e}"
    
    async def list_windows(self) -> str:
        """List all open windows"""
        try:
            windows = gw.getAllWindows()
            window_list = []
            
            for i, window in enumerate(windows[:20], 1):  # Limit to 20 windows
                if window.title.strip():  # Only show windows with titles
                    window_list.append(f"{i}. {window.title} ({window.width}x{window.height})")
            
            if not window_list:
                return "No windows found"
            
            return f"🪟 Open Windows:\n" + "\n".join(window_list)
            
        except Exception as e:
            return f"❌ Error listing windows: {e}"
    
    async def get_system_info(self) -> str:
        """Get system information"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Running processes count
            process_count = len(psutil.pids())
            
            info = f"""
🖥️ System Information:
━━━━━━━━━━━━━━━━━━━━
🏷️  Platform: {platform.system()} {platform.release()}
🔧 CPU Usage: {cpu_percent}%
💾 Memory Usage: {memory_percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)
💿 Disk Usage: {disk_percent:.1f}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)
⚙️  Running Processes: {process_count}
🖱️  Desktop Automation: {'✅ Available' if DESKTOP_AUTOMATION_AVAILABLE else '❌ Unavailable'}
"""
            return info
            
        except Exception as e:
            return f"❌ Error getting system info: {e}"
    
    async def copy_file_operation(self, command: str) -> str:
        """Handle file copy operations"""
        try:
            # This is a basic implementation - extend as needed
            return "✅ File operation commands not yet implemented. Use system file manager."
            
        except Exception as e:
            return f"❌ Error with file operation: {e}"
    
    def _extract_window_name(self, command: str) -> str:
        """Extract window name from command"""
        # Remove common command words and extract the window name
        words_to_remove = ['minimize', 'maximize', 'close', 'focus', 'switch', 'to', 'window', 'the']
        words = command.split()
        filtered_words = [word for word in words if word.lower() not in words_to_remove]
        return ' '.join(filtered_words) if filtered_words else ""
    
    def _extract_app_name(self, command: str) -> str:
        """Extract application name from command"""
        apps = ['notepad', 'calculator', 'browser', 'terminal', 'chrome', 'firefox', 'safari']
        command_lower = command.lower()
        for app in apps:
            if app in command_lower:
                return app
        return ""
    
    def _extract_coordinates(self, command: str) -> Optional[Tuple[int, int]]:
        """Extract coordinates from command"""
        import re
        pattern = r'(\d+)[\s,]+(\d+)'
        match = re.search(pattern, command)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        return None
    
    def _extract_text_to_type(self, command: str) -> str:
        """Extract text to type from command"""
        # Look for text after 'type' keyword
        import re
        pattern = r'type\s+(.+)$'
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            return match.group(1).strip('\'"')
        return ""
    
    def _extract_keys(self, command: str) -> List[str]:
        """Extract key combination from command"""
        # Map common key names
        key_mapping = {
            'ctrl': 'ctrl',
            'control': 'ctrl', 
            'alt': 'alt',
            'shift': 'shift',
            'cmd': 'cmd',
            'win': 'win',
            'enter': 'enter',
            'space': 'space',
            'tab': 'tab',
            'esc': 'esc',
            'escape': 'esc'
        }
        
        # Extract keys from command
        words = command.lower().split()
        keys = []
        
        for word in words:
            # Remove punctuation
            clean_word = word.strip('.,!?')
            if clean_word in key_mapping:
                keys.append(key_mapping[clean_word])
            elif clean_word in 'abcdefghijklmnopqrstuvwxyz0123456789':
                keys.append(clean_word)
        
        return keys if keys else ['space']  # Default to space if no keys found
    
    def _extract_filename(self, command: str) -> Optional[str]:
        """Extract filename from command"""
        import re
        # Look for filename patterns
        patterns = [
            r'save as\s+([^\s]+)',
            r'filename\s+([^\s]+)',
            r'name\s+([^\s]+)',
            r'([^\s]+\.png)',
            r'([^\s]+\.jpg)',
            r'([^\s]+\.jpeg)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    async def _handle_ai_desktop_command(self, command: str, llm_manager) -> str:
        """Handle complex desktop commands using AI"""
        try:
            ai_prompt = f"""
            I am a desktop automation assistant. The user wants to: "{command}"
            
            Available desktop automation capabilities:
            - Window management (minimize, maximize, close, focus)
            - Mouse control (click, scroll)
            - Keyboard input (type text, press keys)
            - Application control (open apps)
            - Screen capture (screenshots)
            - System information
            
            Based on the command, provide step-by-step instructions for what desktop actions to perform.
            If the command is unclear or not possible, explain why and suggest alternatives.
            """
            
            response = await llm_manager.process(ai_prompt, {"command": command})
            return f"🤖 Desktop Assistant: {response}"
            
        except Exception as e:
            return f"❌ AI desktop command processing failed: {e}"
    
    async def _async_sleep(self, seconds: float):
        """Async sleep helper"""
        import asyncio
        await asyncio.sleep(seconds)