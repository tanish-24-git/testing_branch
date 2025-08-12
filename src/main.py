import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import platform
import re
from src.config import config
from src.context_manager import ContextManager
from src.llm_manager import LLMManager
from src.voice_processor import VoiceProcessor
from src.text_search import TextSearch
from src.settings import settings
from src.pipelines.pipelines import CommandPipeline
from src.agents import AgenticAI
from src.logger_config import setup_logger  # Add import

# Configure logging
setup_logger()  # Initialize logging configuration
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="AI Assistant Backend")

# Configure CORS
origins = [
    "http://localhost:3000",  # Flutter web dev
    "http://localhost:8080",  # Flutter mobile dev
    "https://your-production-domain.com"  # Production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
context_manager = ContextManager()
llm_manager = LLMManager()
voice_processor = VoiceProcessor()
text_search = TextSearch()
agentic_ai = AgenticAI()

# Load platform-specific automation base, but handlers are dynamic
if platform.system() == "Windows":
    from src.automation.windows import WindowsAutomation
    automation_base = WindowsAutomation()
elif platform.system() == "Darwin":
    from src.automation.macos import MacOSAutomation
    automation_base = MacOSAutomation()
elif platform.system() == "Linux":
    from src.automation.linux import LinuxAutomation
    automation_base = LinuxAutomation()
else:
    raise NotImplementedError("Unsupported platform")

# Initialize CommandPipeline
pipeline = CommandPipeline()

# Define request model for text commands
class CommandRequest(BaseModel):
    command: str

# Health check endpoint
@app.get("/ping")
async def ping():
    """Check if the backend is running."""
    logger.info("Ping received")
    return {"message": "pong"}

# Text command processing endpoint
@app.post("/command")
async def process_command(request: CommandRequest):
    """Process text commands and return results."""
    try:
        command = request.command
        logger.info(f"Processing text command: {command}")
        return await pipeline.process(command)
    except Exception as e:
        logger.error(f"Error processing text command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Voice command processing endpoint
@app.post("/voice")
async def process_voice(file: UploadFile = File(...)):
    """Process voice commands from uploaded audio file."""
    try:
        if not file.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="Invalid file type; must be audio")
        audio_data = await file.read()
        command = voice_processor.process_audio(audio_data)
        if not command:
            raise HTTPException(status_code=400, detail="Could not transcribe audio")
        logger.info(f"Processing voice command: {command}")
        return await pipeline.process(command)
    except Exception as e:
        logger.error(f"Error processing voice command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Image upload endpoint
@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    """Process image upload."""
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type; must be image")
        image_data = await file.read()
        command = "analyze this image"
        context = {"image_data": image_data}
        logger.info("Processing image upload")
        return await pipeline.process(command, context=context)
    except Exception as e:
        logger.error(f"Error processing image upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for continuous text chatting
@app.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    """Handle continuous text-based chatting."""
    await websocket.accept()
    try:
        while True:
            command = await websocket.receive_text()
            result = await pipeline.process(command)
            await websocket.send_json({"result": result})
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

# Poll voice commands (for continuous listening)
@app.get("/voice_commands")
async def get_voice_commands():
    """Retrieve queued voice commands."""
    command = voice_processor.get_command()
    if command:
        return await pipeline.process(command)
    return {"result": "No voice command available"}

# Run the app locally
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server on localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)