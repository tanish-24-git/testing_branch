import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import logging
from src.llm_manager import LLMManager
from src.rag import RAG
from src.pipelines.comparison_pipeline import ComparisonPipeline
from src.pipelines.automation_pipeline import AutomationPipeline
from src.logger_config import setup_logger

setup_logger()
logger = logging.getLogger(__name__)

app = FastAPI(title="Chat Bot with Automation")

class CommandRequest(BaseModel):
    command: str

class ImageRequest(BaseModel):
    image_data: str
    file_type: str

llm_manager = LLMManager()
rag = RAG()
comparison_pipeline = ComparisonPipeline(llm_manager)
automation_pipeline = AutomationPipeline(llm_manager, rag)  # New: Automation pipeline

@app.post("/command")
async def process_command(request: CommandRequest):
    logger.info(f"Processing command: {request.command}")
    result = await comparison_pipeline.process(request.command)
    return {"command": request.command, "result": result}

@app.post("/upload_image")
async def upload_image(request: ImageRequest):
    logger.info("Processing image upload")
    mime_type = f"image/{request.file_type}"
    result = await comparison_pipeline.process("Describe this image", context={"image_data": request.image_data, "mime_type": mime_type})
    return {"result": result}

@app.post("/automation")
async def run_automation(request: CommandRequest):
    logger.info(f"Processing automation command: {request.command}")
    result = await automation_pipeline.process(request.command)
    return {"command": request.command, "result": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)