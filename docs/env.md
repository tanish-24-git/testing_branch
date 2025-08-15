# Environment Configuration Template (.env)
# Copy this template and fill in your actual API keys and settings

# ==============================================
# LLM API KEYS
# ==============================================

# OpenAI API Key (for GPT-4, GPT-3.5-turbo)
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini API Key  
# Get from: https://ai.google.dev/
GEMINI_API_KEY=your_gemini_api_key_here

# X.AI Grok API Key
# Get from: https://console.x.ai/
GROK_API_KEY=your_grok_api_key_here

# Groq API Key (Fast inference)
# Get from: https://console.groq.com/
GROQ_API_KEY=your_groq_api_key_here

# ==============================================
# LLM MODEL CONFIGURATIONS (Optional)
# ==============================================

# Model names (use defaults if not specified)
GEMINI_MODEL=gemini-1.5-flash
GPT_MODEL=gpt-4o
GROK_MODEL=grok-beta  
GROQ_MODEL=llama3-70b-8192

# ==============================================
# EMAIL AUTOMATION SETTINGS
# ==============================================

# SMTP Server Configuration for Email Automation
# For Gmail, you need to:
# 1. Enable 2-factor authentication
# 2. Generate an "App Password" (not your regular password)
# 3. Use the app password below

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here

# Alternative SMTP providers:
# - Outlook: smtp-mail.outlook.com:587
# - Yahoo: smtp.mail.yahoo.com:587
# - Custom SMTP: your.smtp.server.com:587

# ==============================================
# BROWSER AUTOMATION SETTINGS
# ==============================================

# Browser type (chrome, firefox, webkit)
AUTOMATION_BROWSER=chrome

# Run browser in headless mode (true/false)
AUTOMATION_HEADLESS=true

# Browser timeout in milliseconds
AUTOMATION_TIMEOUT=30000

# ==============================================
# INSTRUCTIONS FOR SETUP
# ==============================================

# 1. Copy this file to .env in your project root
# 2. Fill in your actual API keys and settings
# 3. Never commit .env to version control
# 4. For Gmail SMTP:
#    - Enable 2FA on your Google account
#    - Go to Google Account settings > Security > App passwords
#    - Generate an app password for "Mail"
#    - Use that password in SMTP_PASSWORD (not your regular password)
# 5. For browser automation:
#    - Run: playwright install chromium
#    - Or: playwright install (for all browsers)
# 6. Test your configuration:
#    - Run: python test.py
#    - Check logs for any configuration errors