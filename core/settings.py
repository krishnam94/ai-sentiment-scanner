"""
Configuration settings for the AI Sentiment Scanner app.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Cache settings
CACHE_DIR = "data/summaries"
SNAPSHOT_DIR = "data/snapshots"

# Review analysis settings
REVIEW_COUNT_RANGE = {
    "min": 0,
    "max": 100,
    "default": 50,
    "step": 10
}

# Default app URLs
DEFAULT_URLS = {
    "Airtel Thanks": "https://play.google.com/store/apps/details?id=com.myairtelapp",
    "MyJio": "https://play.google.com/store/apps/details?id=com.jio.myjio",
    "Singtel (My Singtel App)": "https://play.google.com/store/apps/details?id=com.singtel.mysingtel",
    "StarHub": "https://play.google.com/store/apps/details?id=com.starhub.happy",
    "M1": "https://play.google.com/store/apps/details?id=com.m1.android.mym1plus",
    "TPG": "https://play.google.com/store/apps/details?id=sg.tpgmobile.app"
}

# Competitive analysis prompt template
COMPETITIVE_ANALYSIS_PROMPT = """Compare {app1} and {app2} based on their user reviews. 

Focus on key differences in:
- User satisfaction
- Key features
- Main pain points
- Competitive advantages

Keep each point brief and impactful. Use bullet points.""" 