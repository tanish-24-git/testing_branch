# Automation Package
from .browser.browser_automation import browserAutomation
from .desktop.desktop_automation import DesktopAutomation
from .email_automation import EmailAutomation

__all__ = ['browserAutomation', 'DesktopAutomation', 'EmailAutomation']