import os
import sys
import io
import re
from datetime import datetime, timedelta
from google_play_scraper import app

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

import streamlit as st
from core.review_fetcher import fetch_reviews
from core.analyzer import analyze_all, get_review_stats
from core.utils import cached_summary, store_snapshot, load_snapshot
from core.summarizer import summarize_themes, analyze_period_changes
from core.topic_analyzer import extract_topics, analyze_topic_changes, tag_reviews_by_theme, get_period_texts
from components.ui import setup_sidebar, display_metric_card, display_summary_box, display_section_header, setup_comparison_sidebar, display_cache_management
from core.settings import DEFAULT_URLS
import pandas as pd
import logging
from components.version_ui import display_period_summary

# Clear any existing handlers
logging.getLogger().handlers = []

# Set up logging to capture in a string buffer
log_stream = io.StringIO()
handler = logging.StreamHandler(log_stream)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Get the root logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

# Add console handler for direct output
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Enable debug logging for all modules
logging.getLogger('core').setLevel(logging.DEBUG)
logging.getLogger('core.summarizer').setLevel(logging.DEBUG)
logging.getLogger('core.utils').setLevel(logging.DEBUG)

def extract_app_id(url: str) -> str:
    """
    Extract app ID from Google Play Store URL.
    
    Args:
        url: Google Play Store URL
        
    Returns:
        str: Extracted app ID or None if invalid URL
    """
    # Pattern to match Google Play Store URLs
    pattern = r'play\.google\.com/store/apps/details\?id=([a-zA-Z0-9._]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

# Load CSS
def load_css():
    css_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'styles.css')
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="AI Sentiment Scanner - Period Comparison",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
load_css()

# Navigation
st.sidebar.markdown("### Navigation")
if st.sidebar.button("Switch to Single Period Analysis"):
    st.switch_page("main.py")

# Title and description
st.title("📱 AI Sentiment Scanner: Period Comparison")
st.markdown("""
This tool compares Google Play Store reviews for apps across two time periods, providing insights into changes in user sentiment and feedback.
Select an app and two date ranges to analyze and compare reviews.
""", unsafe_allow_html=True)

# Setup sidebar and get inputs
url, period1_start, period1_end, period2_start, period2_end = setup_comparison_sidebar()

# Extract app ID
app_id = extract_app_id(url) if url else None

# Main content
if st.sidebar.button("Analyze App"):
    if not app_id:
        st.error("Please enter a valid Google Play Store URL")
        st.stop()
        
    with st.spinner("Fetching and analyzing reviews..."):
        # Clear previous logs
        log_stream.truncate(0)
        log_stream.seek(0)
        
        print("\n=== Starting Period Comparison Analysis ===")
        
        # Fetch or load reviews
        print(f"\nProcessing {app_id}...")
        logger.info(f"Starting process for {app_id}")
        reviews = load_snapshot(app_id)
        if not reviews:
            print(f"Fetching fresh reviews for {app_id}")
            logger.info(f"Fetching fresh reviews for {app_id}")
            try:
                reviews = fetch_reviews(app_id, count=200)  # Fetch 200 reviews by default
                if reviews:
                    print(f"Successfully fetched {len(reviews)} reviews for {app_id}")
                    logger.info(f"Successfully fetched {len(reviews)} reviews for {app_id}")
                    app_info = app(app_id)
                    store_snapshot(app_info['title'], reviews, len(reviews))
                else:
                    st.error(f"Could not fetch reviews for {app_id}. Please try again later.")
                    logger.error(f"No reviews returned for {app_id}")
                    st.stop()
            except Exception as e:
                st.error(f"Error fetching reviews for {app_id}: {str(e)}")
                logger.error(f"Error fetching reviews for {app_id}: {str(e)}", exc_info=True)
                st.stop()

        # Analyze reviews
        try:
            print("\nAnalyzing reviews...")
            logger.info("Analyzing reviews")
            df = analyze_all(reviews)
            
            # Convert dates to datetime
            df['date'] = pd.to_datetime(df['date'])
            
            # Filter for first period
            period1_df = df[(df['date'] >= pd.Timestamp(period1_start)) & 
                          (df['date'] <= pd.Timestamp(period1_end))]
            
            if len(period1_df) == 0:
                st.warning(f"No reviews found in the first period ({period1_start} to {period1_end})")
                st.stop()
            
            # Filter for second period
            period2_df = df[(df['date'] >= pd.Timestamp(period2_start)) & 
                          (df['date'] <= pd.Timestamp(period2_end))]
            
            if len(period2_df) == 0:
                st.warning(f"No reviews found in the second period ({period2_start} to {period2_end})")
                st.stop()
            
            # Display comparison
            display_section_header("Period Comparison", "⚖️")
            
            # Display individual period summaries side by side
            col1, col2 = st.columns(2)
            with col1:
                display_period_summary(df, pd.Timestamp(period1_start), pd.Timestamp(period1_end))
            with col2:
                display_period_summary(df, pd.Timestamp(period2_start), pd.Timestamp(period2_end))
            
            # Generate and display LLM analysis
            try:
                period1_name = f"{period1_start.strftime('%Y-%m-%d')} to {period1_end.strftime('%Y-%m-%d')}"
                period2_name = f"{period2_start.strftime('%Y-%m-%d')} to {period2_end.strftime('%Y-%m-%d')}"
                
                # Prepare data for LLM analysis
                period1_data = {
                    'metrics': {
                        'average_sentiment': period1_df['sentiment'].mean(),
                        'average_rating': period1_df['score'].mean(),
                        'review_count': len(period1_df)
                    },
                    'topics': dict(extract_topics(period1_df['text'].tolist())),
                    'themes': {
                        theme: sum(score[theme] for score in tag_reviews_by_theme(period1_df['text'].tolist())) / len(period1_df)
                        for theme in ['UX', 'Performance', 'Features', 'Bugs', 'Content', 'Support']
                    }
                }
                
                period2_data = {
                    'metrics': {
                        'average_sentiment': period2_df['sentiment'].mean(),
                        'average_rating': period2_df['score'].mean(),
                        'review_count': len(period2_df)
                    },
                    'topics': dict(extract_topics(period2_df['text'].tolist())),
                    'themes': {
                        theme: sum(score[theme] for score in tag_reviews_by_theme(period2_df['text'].tolist())) / len(period2_df)
                        for theme in ['UX', 'Performance', 'Features', 'Bugs', 'Content', 'Support']
                    }
                }
                
                analysis = analyze_period_changes(
                    period1_data,
                    period2_data,
                    period1_name,
                    period2_name
                )
                
                st.markdown("---")
                display_section_header("AI-Powered Comparison Analysis", "🧠")
                display_summary_box("Key Changes and Insights", analysis)
            except Exception as e:
                logger.error(f"Error generating period comparison analysis: {str(e)}", exc_info=True)
                st.error(f"Error generating period comparison analysis: {str(e)}")

        except Exception as e:
            print(f"Error analyzing reviews: {str(e)}")
            logger.error(f"Error analyzing reviews: {str(e)}", exc_info=True)
            st.error(f"Error analyzing reviews: {str(e)}")
            st.stop()

        st.success("Analysis complete!")

        # Display logs
        with st.expander("Debug Information", expanded=False):
            st.text(log_stream.getvalue())

        # Display raw reviews at the bottom
        display_section_header("Raw Reviews", "📄")
        st.markdown("### First Period Reviews")
        st.dataframe(period1_df.sort_values("date", ascending=False))
        st.markdown("### Second Period Reviews")
        st.dataframe(period2_df.sort_values("date", ascending=False))

# Footer
st.markdown("---")
st.markdown("Powered by Streamlit | Data sourced from Google Play Store") 