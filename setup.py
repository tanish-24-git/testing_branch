from setuptools import setup, find_packages

setup(
    name="ai-agent",
    version="3.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.112.0",
        "uvicorn==0.30.5",
        "pydantic==2.8.2",
        "httpx==0.27.0",
        "python-dotenv==0.21.0",
        "pyyaml==6.0.1",
        "google-api-python-client==2.111.0",
        "google-auth-httplib2==0.2.0",
        "google-auth-oauthlib==1.2.0",
        "google-generativeai==0.5.0",
        "groq==0.1.0",
    ],
    author="Your Name",
    description="AI Agent for Gmail Automation",
    python_requires=">=3.8"
)