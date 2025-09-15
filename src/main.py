import os
import sys
import json
import warnings
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, __version__ as pydantic_version
from crew import AiAgent
import traceback
from uvicorn import Config, Server
import asyncio
from common_functions.Find_project_root import find_project_root
from firebase_client import get_user_profile, set_user_profile
from common_functions.User_preference import collect_preferences
from utils.logger import setup_logger

PROJECT_ROOT = find_project_root()
logger = setup_logger()

# Suppress Pydantic warnings
if pydantic_version.startswith("2"):
    from pydantic import PydanticDeprecatedSince20
    warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)

# FastAPI app setup
app = FastAPI(title="AI Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for query input
class QueryRequest(BaseModel):
    query: str

# API endpoint for processing queries
@app.post("/process_query")
async def process_query(request: QueryRequest):
    logger.info(f"Received API query: {request.query}")
    if not request.query:
        logger.error("No query provided in API request")
        raise HTTPException(status_code=400, detail="No query provided")
    try:
        crew_instance = AiAgent()
        final_response = crew_instance.run_workflow(request.query)
        logger.debug(f"API response for query '{request.query}': {final_response}")
        return {"result": final_response}
    except Exception as e:
        logger.error(f"Error processing query '{request.query}': {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# CLI-related functions
REQUIRED_PROFILE_KEYS = [
    "Name", "Role", "Location", "Productive Time", "Reminder Type",
    "Top Task Type", "Missed Task Handling", "Top Motivation",
    "AI Tone", "Break Reminder", "Mood Check", "Current Focus"
]

def display_welcome():
    message = "=" * 60 + "\n🤖 AI ASSISTANT - Firebase-Integrated CrewAI\n" + "=" * 60 + \
              "\nNow using Firestore for profiles, tasks, and memory!\n" + \
              "Use 'help' or 'h' for commands, 'quit' or 'q' to exit.\n" + "=" * 60
    print(message)
    logger.info("Displayed welcome message")

def display_help():
    message = "\nAvailable Commands:\n" + \
              "- help, h: Show this help message\n" + \
              "- quit, q: Exit the assistant\n" + \
              "- Any other input: Process as a query (e.g., 'List tasks', 'Create snapshot')\n" + \
              "\nExamples:\n" + \
              "- 'List files in /tmp' → Lists files using file.list operation\n" + \
              "- 'Create task Buy groceries' → Creates task in Firestore\n" + \
              "- 'Start focus session for 25 min' → Starts focus session"
    print(message)
    logger.info("Displayed help message")

def get_user_input(prompt="💬 What can I help you with? "):
    try:
        user_input = input(prompt).strip()
        logger.debug(f"Received CLI input: {user_input}")
        return user_input
    except KeyboardInterrupt:
        logger.info("CLI input interrupted by user")
        return "quit"

def load_or_create_profile():
    """Load or create user profile in Firestore."""
    logger.info("Loading or creating user profile")
    profile = get_user_profile()
    if not profile:
        logger.warning("No profile found in Firestore. Setting up...")
        print("No profile found in Firestore. Setting up...")
        name = get_user_input("Your name: ")
        email = get_user_input("Your email: ")
        set_user_profile(name, email)
        profile = get_user_profile()
        logger.info("Profile created in Firestore")
        print("✅ Profile created in Firestore.")
    missing = [k for k in REQUIRED_PROFILE_KEYS if k not in profile or not profile[k]]
    if missing:
        logger.warning(f"Missing profile fields: {missing}. Collecting...")
        print(f"Missing profile fields: {missing}. Collecting...")
        collect_preferences(None, get_user_input)  # Uses Firestore
        profile = get_user_profile()
    logger.debug(f"User profile loaded: {json.dumps(profile, default=str)}")
    return profile

def validate_environment():
    """Check Firebase connectivity."""
    logger.info("Validating Firebase connectivity")
    try:
        _ = get_user_profile()
        logger.info("Firebase connected successfully")
        print("✅ Firebase connected.")
        return True
    except Exception as e:
        logger.error(f"Firebase error: {str(e)}")
        print(f"❌ Firebase error: {str(e)}")
        return False

def run_single_query(user_query=None):
    logger.info(f"Processing single query: {user_query}")
    if not validate_environment():
        logger.error("Environment validation failed")
        return False
    profile = load_or_create_profile()
    if not user_query:
        user_query = get_user_input()
    if user_query.lower() in ["quit", "exit", "q"]:
        logger.info("User requested to quit")
        return False
    if user_query.lower() in ["help", "h"]:
        display_help()
        return True
    if not user_query:
        logger.debug("Empty query provided")
        return True
    print(f"\n🔍 Processing: '{user_query}' (Profile: {profile.get('Name', 'Unknown')})")
    logger.info(f"Processing query: {user_query} for user {profile.get('Name', 'Unknown')}")
    try:
        crew_instance = AiAgent()
        final_response = crew_instance.run_workflow(user_query)
        print(final_response)
        logger.debug(f"Query response: {final_response}")
        return True
    except Exception as e:
        logger.error(f"Error processing query '{user_query}': {str(e)}")
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return True

async def run_server():
    """Run the FastAPI server."""
    logger.info("Starting FastAPI server on http://127.0.0.1:8000")
    config = Config(app=app, host="127.0.0.1", port=8000, log_level="info")
    server = Server(config)
    await server.serve()

def run_interactive():
    display_welcome()
    try:
        while True:
            if not run_single_query():
                break
    except KeyboardInterrupt:
        logger.info("Interactive mode terminated by user")
        print("\n👋 Goodbye!")

def run():
    logger.info("Starting AI Assistant")
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        logger.info("Running in server mode")
        asyncio.run(run_server())
    elif len(sys.argv) > 1:
        query = " ".join(sys.argv[1:]).strip('"')
        logger.info(f"Running single query mode with: {query}")
        run_single_query(query)
    else:
        logger.info("Running in interactive CLI mode")
        run_interactive()

def train():
    logger.info("Train function called (not implemented)")
    pass

def replay():
    logger.info("Replay function called (not implemented)")
    pass

def test():
    logger.info("Test function called (not implemented)")
    pass

if __name__ == "__main__":
    run()