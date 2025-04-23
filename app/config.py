"""
Configuration and constants for the AI Sentiment Scanner app.
"""

# Default app URLs
DEFAULT_URLS = {
    "Airtel Thanks": "https://play.google.com/store/apps/details?id=com.myairtelapp",
    "MyJio": "https://play.google.com/store/apps/details?id=com.jio.myjio",
    "Singtel (My Singtel App)": "https://play.google.com/store/apps/details?id=com.singtel.mysingtel",
    "StarHub": "https://play.google.com/store/apps/details?id=com.starhub.happy",
    "M1": "https://play.google.com/store/apps/details?id=com.m1.android.mym1plus",
    "TPG": "https://play.google.com/store/apps/details?id=sg.tpgmobile.app"
}

# Review analysis settings
REVIEW_COUNT_RANGE = {
    "min": 0,
    "max": 100,
    "default": 50,
    "step": 10
}

# Competitive analysis prompt template
COMPETITIVE_ANALYSIS_PROMPT = """Compare {app1} and {app2} based on their user reviews. 
Focus on:
1. Key differences in user satisfaction and sentiment
2. Feature comparisons and unique strengths
3. Common pain points and areas for improvement
4. Competitive advantages of each app
5. User engagement and review patterns

Format the response in clear sections with bullet points for easy reading."""

# Cache settings
CACHE_DIR = "data/summaries"
SNAPSHOT_DIR = "data/snapshots" 