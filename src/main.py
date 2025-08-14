import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from src.llm_manager import LLMManager
from src.rag import RAG
from src.settings import settings
from src.logger_config import setup_logger

setup_logger()
logger = logging.getLogger(__name__)

app = FastAPI(title="Chat Bot Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CommandRequest(BaseModel):
    command: str

# Global instances (unchanged)
llm_manager = LLMManager()
rag = RAG()

# Dependency getters for injection and reusability
def get_rag() -> RAG:
    return rag

def get_llm_manager() -> LLMManager:
    return llm_manager

@app.post("/command")
async def process_command(request: CommandRequest, rag_inst: RAG = Depends(get_rag), llm_inst: LLMManager = Depends(get_llm_manager)):
    command = request.command
    logger.info(f"Processing command: {command}")
    rag_response = rag_inst.retrieve(command)
    result = await llm_inst.process(command, {"rag": rag_response})
    return {"command": command, "result": result}

@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...), llm_inst: LLMManager = Depends(get_llm_manager)):
    logger.info("Processing image upload")
    image_data = await file.read()
    mime_type = file.content_type or "image/jpeg"
    command = "Describe this image"
    result = await llm_inst.process(command, {"image_data": image_data, "mime_type": mime_type})
    return {"result": result}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, rag_inst: RAG = Depends(get_rag), llm_inst: LLMManager = Depends(get_llm_manager)):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            command = data.strip()
            if not command:
                await websocket.send_text("Error: Empty command")
                continue
            logger.info(f"WebSocket received command: {command}")
            rag_response = rag_inst.retrieve(command)
            result = await llm_inst.process(command, {"rag": rag_response})
            await websocket.send_text(result)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_text(f"Error: {str(e)}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)