from dotenv import load_dotenv
import os

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        # Add other environment variables as needed
    }