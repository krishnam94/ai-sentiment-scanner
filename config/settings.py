import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI API credentials
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# App settings
DEFAULT_REVIEW_COUNT = 200
MAX_REVIEW_COUNT = 500
MIN_REVIEW_COUNT = 50

# App IDs for telecom companies in Singapore
APP_IDS = {
    "Singtel (My Singtel App)": "com.singtel.mysingtel",
    "StarHub": "com.starhub.prepaid",
    "M1": "com.m1.android.mym1",
    "TPG": "sg.tpgmobile.app"
} 