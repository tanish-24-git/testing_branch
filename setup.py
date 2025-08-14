from setuptools import setup, find_packages

setup(
    name="chat-bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.112.0",
        "uvicorn==0.30.5",
        "pydantic==2.8.2",
        "httpx==0.27.0",
        "python-dotenv==0.21.0",
        "pyyaml==6.0.1",
        "requests==2.32.3",
        "langchain==0.2.10",
        "sentence-transformers==3.0.1",
        "faiss-cpu==1.8.0",
        "pillow==10.4.0",
        "groq==0.1.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="Simple Chat Bot with RAG and LLMs",
    python_requires=">=3.8"
)