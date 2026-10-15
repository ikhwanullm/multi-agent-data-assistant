"""Configuration settings for Multi-Agent Data Assistant."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "sample.db"

# Groq settings (Primary - Free & Fast)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "openai/gpt-oss-20b"  # Fast, affordable, 131K context

# OpenAI settings (Fallback)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o-mini"

# LLM Provider selection
# Priority: Groq -> OpenAI -> Demo Mode
if GROQ_API_KEY:
    LLM_PROVIDER = "groq"
    DEMO_MODE = False
elif OPENAI_API_KEY:
    LLM_PROVIDER = "openai"
    DEMO_MODE = False
else:
    LLM_PROVIDER = "demo"
    DEMO_MODE = True

# Agent settings
MAX_SQL_RESULTS = 100
QUERY_TIMEOUT = 30  # seconds
