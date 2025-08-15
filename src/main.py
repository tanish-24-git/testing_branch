"""
Enhanced Main Server - AI Agent with Email Intelligence & Desktop Automation
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Import our modules
from src.llm_manager import LLMManager
from src.rag import RAG
from src.config import config
from src.logger_config import setup_logger

# Import agents
from src.agents.base_agent import AgentManager
from src.agents.email_agent import EmailAgent
from src.agents.automation_agent import AutomationAgent

# Import automation modules
from src.automation.browser_automation import browserAutomation
from src.automation.desktop_automation import DesktopAutomation
from src.automation.email_automation import EmailAutomation

# Setup logging
setup_logger()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced AI Agent",
    description="AI Agent with Email Intelligence & Desktop Automation",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class CommandRequest(BaseModel):
    command: str
    context: Optional[Dict[str, Any]] = None

class ImageRequest(BaseModel):
    image_data: str
    file_type: str

class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    auto_enhance: Optional[bool] = True

class DesktopRequest(BaseModel):
    command: str
    safety_check: Optional[bool] = True

# Global instances
llm_manager = None
rag = None
agent_manager = None
browser_automation = None
desktop_automation = None
email_automation = None

@app.on_event("startup")
async def startup_event():
    """Initialize all components on startup"""
    global llm_manager, rag, agent_manager, browser_automation, desktop_automation, email_automation
    
    try:
        logger.info("🚀 Starting Enhanced AI Agent System...")
        
        # Initialize core components
        logger.info("Initializing LLM Manager...")
        llm_manager = LLMManager()
        
        logger.info("Initializing RAG system...")
        rag = RAG()
        
        # Initialize automation modules
        logger.info("Initializing automation modules...")
        browser_automation = browserAutomation()
        desktop_automation = DesktopAutomation()
        email_automation = EmailAutomation()
        
        # Initialize agent manager
        logger.info("Initializing AI agents...")
        agent_manager = AgentManager(llm_manager)
        
        # Create and register agents
        email_agent = EmailAgent(llm_manager, config.get('agents', {}).get('email', {}))
        automation_agent = AutomationAgent(llm_manager, config.get('agents', {}).get('automation', {}))
        
        agent_manager.register_agent(email_agent)
        agent_manager.register_agent(automation_agent)
        
        # Start agents
        logger.info("Starting AI agents...")
        agent_results = await agent_manager.start_all_agents()
        
        for agent_name, started in agent_results.items():
            if started:
                logger.info(f"✅ {agent_name} started successfully")
            else:
                logger.warning(f"⚠️ {agent_name} failed to start")
        
        logger.info("🎉 Enhanced AI Agent System started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global agent_manager
    
    try:
        logger.info("🛑 Shutting down Enhanced AI Agent System...")
        
        if agent_manager:
            await agent_manager.stop_all_agents()
        
        logger.info("✅ Shutdown completed")
        
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")

@app.get("/")
async def root():
    """Root endpoint with system status"""
    try:
        status = {
            "name": "Enhanced AI Agent",
            "version": "2.0.0",
            "status": "running",
            "features": [
                "Multi-LLM Support (GPT-4, Gemini, Grok, Groq)",
                "Email Intelligence & Auto-Reply",
                "Browser Automation",
                "Desktop Automation", 
                "RAG Document Processing",
                "AI Agent System"
            ],
            "agents": agent_manager.get_all_status() if agent_manager else {},
            "automation": {
                "browser": browser_automation is not None,
                "desktop": desktop_automation.is_available() if desktop_automation else False,
                "email": email_automation is not None
            }
        }
        return status
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/command")
async def process_command(request: CommandRequest):
    """Process general commands using the best available agent"""
    try:
        logger.info(f"Processing command: {request.command}")
        
        if not agent_manager:
            # Fallback to direct LLM processing
            result = await llm_manager.process(request.command, request.context or {})
        else:
            # Route to appropriate agent
            result = await agent_manager.route_command(request.command)
        
        return {
            "command": request.command,
            "result": result,
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        logger.error(f"Command processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload_image")
async def upload_image(request: ImageRequest):
    """Process image uploads with vision-capable LLMs"""
    try:
        logger.info("Processing image upload")
        
        mime_type = f"image/{request.file_type}"
        context = {
            "image_data": request.image_data,
            "mime_type": mime_type
        }
        
        result = await llm_manager.process("Describe this image in detail", context)
        
        return {
            "result": result,
            "image_type": request.file_type,
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        logger.error(f"Image processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/automation")
async def run_automation(request: CommandRequest):
    """Run browser automation commands"""
    try:
        logger.info(f"Processing automation command: {request.command}")
        
        if agent_manager:
            automation_agent = agent_manager.get_agent('automation_agent')
            if automation_agent and automation_agent.is_active:
                result = await automation_agent.process_command(request.command, request.context)
            else:
                # Fallback to direct browser automation
                result = await browser_automation.execute_command(request.command, llm_manager, rag)
        else:
            result = await browser_automation.execute_command(request.command, llm_manager, rag)
        
        return {
            "command": request.command,
            "result": result,
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        logger.error(f"Automation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/desktop_automation")
async def run_desktop_automation(request: DesktopRequest):
    """Run desktop automation commands"""
    try:
        logger.info(f"Processing desktop automation: {request.command}")
        
        if not desktop_automation.is_available():
            raise HTTPException(
                status_code=503, 
                detail="Desktop automation not available. Install required packages: pip install pyautogui pygetwindow pynput psutil"
            )
        
        # Safety check for potentially dangerous commands
        if request.safety_check:
            dangerous_keywords = ['delete', 'format', 'rm -rf', 'shutdown', 'restart']
            if any(keyword in request.command.lower() for keyword in dangerous_keywords):
                raise HTTPException(
                    status_code=400,
                    detail="Potentially dangerous command blocked. Disable safety_check to override."
                )
        
        result = await desktop_automation.execute_command(request.command, llm_manager, rag)
        
        return {
            "command": request.command,
            "result": result,
            "safety_check": request.safety_check,
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Desktop automation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/email")
async def send_email(request: EmailRequest):
    """Send email via the email agent"""
    try:
        logger.info(f"Sending email to: {request.to}")
        
        if agent_manager:
            email_agent = agent_manager.get_agent('email_agent')
            if email_agent and email_agent.is_active:
                # Format command for email agent
                command = f"send email to {request.to} with subject {request.subject} and body {request.body}"
                result = await email_agent.process_command(command)
            else:
                # Fallback to direct email automation
                result = await email_automation.send_email(request.to, request.subject, request.body)
        else:
            result = await email_automation.send_email(request.to, request.subject, request.body)
        
        return {
            "to": request.to,
            "subject": request.subject,
            "result": result,
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/email/check")
async def check_emails():
    """Check for new emails"""
    try:
        logger.info("Checking emails")
        
        if agent_manager:
            email_agent = agent_manager.get_agent('email_agent')
            if email_agent and email_agent.is_active:
                result = await email_agent.process_command("check emails")
            else:
                result = "Email agent not available"
        else:
            result = await email_automation.check_emails()
        
        return {
            "result": result,
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        logger.error(f"Email check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/email/reply")
async def reply_to_email(request: CommandRequest):
    """Generate and send email reply"""
    try:
        logger.info("Generating email reply")
        
        if agent_manager:
            email_agent = agent_manager.get_agent('email_agent')
            if email_agent and email_agent.is_active:
                result = await email_agent.process_command(request.command)
            else:
                result = "Email agent not available"
        else:
            result = "Email agent not initialized"
        
        return {
            "command": request.command,
            "result": result,
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        logger.error(f"Email reply failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/status")
async def get_agents_status():
    """Get status of all AI agents"""
    try:
        if not agent_manager:
            return {"error": "Agent manager not initialized"}
        
        return {
            "agents": agent_manager.get_all_status(),
            "active_count": len(agent_manager.get_active_agents()),
            "total_count": len(agent_manager.agents),
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        logger.error(f"Agent status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/{agent_name}/command")
async def send_command_to_agent(agent_name: str, request: CommandRequest):
    """Send command to specific agent"""
    try:
        if not agent_manager:
            raise HTTPException(status_code=503, detail="Agent manager not available")
        
        agent = agent_manager.get_agent(agent_name)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        if not agent.is_active:
            raise HTTPException(status_code=503, detail=f"Agent '{agent_name}' is not active")
        
        result = await agent.process_command(request.command, request.context)
        
        return {
            "agent": agent_name,
            "command": request.command,
            "result": result,
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent command failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/health")
async def health_check():
    """System health check"""
    try:
        health_status = {
            "status": "healthy",
            "components": {
                "llm_manager": llm_manager is not None,
                "rag": rag is not None,
                "agent_manager": agent_manager is not None,
                "browser_automation": browser_automation is not None,
                "desktop_automation": desktop_automation.is_available() if desktop_automation else False,
                "email_automation": email_automation is not None
            },
            "agents": {},
            "timestamp": asyncio.get_event_loop().time()
        }
        
        if agent_manager:
            for name, agent in agent_manager.agents.items():
                health_status["agents"][name] = {
                    "active": agent.is_active,
                    "last_activity": agent.last_activity.isoformat() if agent.last_activity else None
                }
        
        # Determine overall health
        if not all(health_status["components"].values()):
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": asyncio.get_event_loop().time()
        }

@app.get("/system/config")
async def get_system_config():
    """Get system configuration (non-sensitive)"""
    try:
        return {
            "app": config.get('app', {}),
            "logging": {k: v for k, v in config.get('logging', {}).items() if k != 'file'},
            "rag": config.get('rag', {}),
            "automation": config.get('automation', {}),
            "agents": {k: v for k, v in config.get('agents', {}).items() if 'password' not in str(v).lower()},
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"Config retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background tasks
@app.post("/background/start_email_monitoring")
async def start_email_monitoring(background_tasks: BackgroundTasks):
    """Start background email monitoring"""
    try:
        if agent_manager:
            email_agent = agent_manager.get_agent('email_agent')
            if email_agent and email_agent.is_active:
                result = await email_agent.process_command("start monitoring")
                return {"result": result}
        
        return {"error": "Email agent not available"}
        
    except Exception as e:
        logger.error(f"Email monitoring start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/background/stop_email_monitoring")
async def stop_email_monitoring():
    """Stop background email monitoring"""
    try:
        if agent_manager:
            email_agent = agent_manager.get_agent('email_agent')
            if email_agent and email_agent.is_active:
                result = await email_agent.process_command("stop monitoring")
                return {"result": result}
        
        return {"error": "Email agent not available"}
        
    except Exception as e:
        logger.error(f"Email monitoring stop failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration
    host = config.get('server', {}).get('host', '127.0.0.1')
    port = config.get('server', {}).get('port', 8000)
    workers = config.get('server', {}).get('workers', 1)
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        workers=workers,
        reload=False,  # Set to True for development
        log_level="info"
    )