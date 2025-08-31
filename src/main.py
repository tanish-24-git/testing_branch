import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import logging
from dotenv import load_dotenv
import asyncio
from datetime import datetime

from .config import config
from .settings import settings
from .llm_manager import LLMManager
from .agents.agent_manager import AgentManager

load_dotenv()
logging.basicConfig(level=config['logging']['level'], filename=config['logging']['file'])
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm_manager = LLMManager()
agent_manager = AgentManager(llm_manager)

@app.on_event("startup")
async def startup():
    agent_manager.register_agents()
    await agent_manager.start_all()
    logger.info("AI Agent started")

@app.on_event("shutdown")
async def shutdown():
    await agent_manager.stop_all()
    logger.info("AI Agent stopped")

class CommandRequest(BaseModel):
    command: str
    context: Optional[Dict] = None

class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str

class ScheduleRequest(EmailRequest):
    scheduled_time: str

class AutoReplyRequest(BaseModel):
    email_id: str

@app.post("/command")
async def process_command(req: CommandRequest):
    try:
        return {"result": await agent_manager.route_command(req.command, req.context)}
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, str(e))

@app.post("/email/send")
async def send_email(req: EmailRequest):
    try:
        email_agent = agent_manager.get_agent("email")
        command = f"send email to {req.to} with subject {req.subject} and body {req.body}"
        return {"result": await email_agent.process_command(command)}
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, str(e))

@app.get("/email/check")
async def check_emails(count: int = 10):
    try:
        email_agent = agent_manager.get_agent("email")
        return {"emails": await email_agent._receive_emails(count)}
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, str(e))

@app.post("/email/schedule")
async def schedule_email(req: ScheduleRequest):
    try:
        email_agent = agent_manager.get_agent("email")
        return {"result": await email_agent._schedule_email(req.to, req.subject, req.body, req.scheduled_time)}
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, str(e))

@app.post("/email/auto-reply")
async def auto_reply(req: AutoReplyRequest):
    try:
        email_agent = agent_manager.get_agent("email")
        return {"result": await email_agent._auto_reply(req.email_id)}
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, str(e))

if __name__ == "__main__":
    uvicorn.run(app, host=config['server']['host'], port=config['server']['port'])