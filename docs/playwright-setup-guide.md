# PLAYWRIGHT INSTALLATION AND SETUP GUIDE

## Issue: Import "playwright.async_api" could not be resolved

This error occurs because Playwright is not properly installed. Here's how to fix it:

## Step 1: Install Playwright Python Package
```bash
# Install the Python package
pip install playwright

# OR if you have a requirements.txt
pip install -r requirements.txt
```

## Step 2: Install Playwright Browsers (CRITICAL STEP)
```bash
# This step is REQUIRED - installs the actual browser binaries
playwright install

# OR install specific browsers only
playwright install chromium
playwright install firefox
playwright install webkit

# OR install with dependencies (recommended for Linux)
playwright install --with-deps
```

## Step 3: Verify Installation
```bash
# Test if playwright is working
python -c "from playwright.sync_api import sync_playwright; print('Playwright installed successfully!')"

# Or test async version
python -c "from playwright.async_api import async_playwright; print('Playwright async installed successfully!')"
```

## Step 4: Run Your Test Script
```bash
python test.py
```

## Common Issues and Solutions:

### Issue 1: "Executable doesn't exist" error
**Solution**: Run `playwright install` - this downloads the browser binaries

### Issue 2: Permission errors on Linux/Mac
**Solution**: 
```bash
sudo playwright install-deps  # Install system dependencies
playwright install           # Install browsers for user
```

### Issue 3: VS Code still showing import errors
**Solutions**:
1. Restart VS Code completely
2. Select correct Python interpreter (Ctrl+Shift+P > Python: Select Interpreter)
3. Reload VS Code window (Ctrl+Shift+P > Developer: Reload Window)

### Issue 4: Virtual environment issues
**Solution**:
```bash
# Activate your virtual environment first
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows

# Then install playwright
pip install playwright
playwright install
```

## Step 5: Update Your Requirements.txt (if needed)
Make sure your requirements.txt includes:
```
playwright==1.46.0
```

## Step 6: Alternative - Use System Browser Fallback
If Playwright still doesn't work, your browser automation will automatically fall back to:
1. System default browser (webbrowser module)
2. Command-line browser opening
3. This ensures automation still works even without Playwright

## Complete Installation Command Sequence:
```bash
# 1. Install Python package
pip install playwright==1.46.0

# 2. Install browser binaries (REQUIRED!)
playwright install chromium

# 3. Test installation
python -c "from playwright.async_api import async_playwright; print('Success!')"

# 4. Run your test
python test.py
```

## Environment-Specific Instructions:

### Windows:
```cmd
pip install playwright
playwright install chromium
```

### macOS:
```bash
pip install playwright
playwright install chromium
# If you get permission errors:
playwright install-deps
```

### Linux (Ubuntu/Debian):
```bash
pip install playwright
sudo playwright install-deps  # Install system dependencies
playwright install chromium
```

### Docker:
```dockerfile
FROM python:3.11
RUN pip install playwright
RUN playwright install chromium --with-deps
```

## Verification Script:
Create a file called `verify_playwright.py`:

```python
import asyncio
from playwright.async_api import async_playwright

async def test_playwright():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://example.com")
        title = await page.title()
        print(f"✅ Playwright working! Page title: {title}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_playwright())
```

Run with: `python verify_playwright.py`

## If ALL ELSE FAILS:
Your browser automation system has fallback methods that work without Playwright:
- System default browser opening
- Command-line browser control
- These will automatically activate if Playwright fails

The automation will still work, just with reduced capabilities.