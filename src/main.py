import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import logging
from src.llm_manager import LLMManager
from src.rag import RAG
from src.settings import settings
from src.logger_config import setup_logger

setup_logger()
logger = logging.getLogger(__name__)

app = FastAPI(title="Chat Bot Backend")

class CommandRequest(BaseModel):
    command: str

llm_manager = LLMManager()
rag = RAG()

@app.post("/command")
async def process_command(request: CommandRequest):
    command = request.command
    logger.info(f"Processing command: {command}")
    rag_response = rag.retrieve(command)
    result = await llm_manager.process(command, {"rag": rag_response})
    return {"command": command, "result": result}

@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    logger.info("Processing image upload")
    image_data = await file.read()
    mime_type = file.content_type or "image/jpeg"
    # Placeholder for image processing (e.g., captioning)
    command = "Describe this image"
    result = await llm_manager.process(command, {"image_data": image_data, "mime_type": mime_type})
    return {"result": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)