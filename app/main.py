import os
import sys
import io
import re
from datetime import datetime, timedelta
from google_play_scraper import app

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import streamlit as st
from core.review_fetcher import fetch_reviews
from core.analyzer import analyze_all, get_review_stats
from core.utils import cached_summary, store_snapshot, load_snapshot
from core.summarizer import summarize_themes
from core.topic_analyzer import extract_topics, analyze_topic_changes, tag_reviews_by_theme, get_period_texts
from components.ui import setup_sidebar, display_metric_card, display_summary_box, display_section_header, display_cache_management
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
    css_file = os.path.join(os.path.dirname(__file__), 'static', 'styles.css')
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="AI Sentiment Scanner",
    page_icon="📱",
    layout="wide"
)

# Load CSS
load_css()

# Navigation
st.sidebar.markdown("### Navigation")
if st.sidebar.button("Switch to Period Comparison"):
    st.switch_page("pages/period_comparison.py")

# Title and description
st.title("📱 AI Sentiment Scanner: Single Period Analysis")
st.markdown("""
This tool analyzes Google Play Store reviews for apps in a single time period, providing insights into user sentiment and feedback.
Select an app and date range to analyze reviews and get AI-powered summaries.
""", unsafe_allow_html=True)

# Setup sidebar and get inputs
url, period1_start, period1_end = setup_sidebar()

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
        
        print("\n=== Starting App Analysis ===")
        
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
            
            # Filter for period
            period_df = df[(df['date'] >= pd.Timestamp(period1_start)) & 
                          (df['date'] <= pd.Timestamp(period1_end))]
            
            if len(period_df) == 0:
                st.warning(f"No reviews found in the selected date range ({period1_start} to {period1_end})")
                st.stop()
            
            # Display period analysis
            display_section_header("Period Analysis", "📊")
            display_period_summary(df, pd.Timestamp(period1_start), pd.Timestamp(period1_end))
                
        except Exception as e:
            print(f"Error analyzing reviews: {str(e)}")
            logger.error(f"Error analyzing reviews: {str(e)}", exc_info=True)
            st.error(f"Error analyzing reviews: {str(e)}")
            st.stop()

        st.success("Analysis complete!")

        # Display logs
        with st.expander("Debug Information", expanded=False):
            st.text(log_stream.getvalue())

        # AI-Powered Review Analysis
        display_section_header("AI-Powered Review Analysis", "🧠")
        st.markdown("""
        The summary below is generated using GPT-4 and provides deeper insights into user feedback.
        The analysis includes sentiment scoring and key highlights.
        """)
        
        try:
            # Limit the number of reviews to prevent token limit issues
            max_reviews = 200  # Increased from 100 to 200 for more comprehensive analysis
            reviews_to_analyze = period_df["text"].tolist()[:max_reviews]
            
            if len(period_df) > max_reviews:
                st.info(f"Note: AI analysis is based on the {max_reviews} most recent reviews to ensure quality insights. All {len(period_df)} reviews are still used for metrics and visualizations.")
            
            summary = cached_summary(
                reviews_to_analyze,
                summarize_themes,
                f"{app_id}_{period1_start.strftime('%Y%m%d')}_{period1_end.strftime('%Y%m%d')}"
            )
            display_summary_box("Key Insights", summary)
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}", exc_info=True)
            st.error(f"Error generating summary: {str(e)}")

        # Sentiment Analysis Over Time
        display_section_header("Sentiment Analysis Over Time", "📊")
        st.markdown("""
        ### How Sentiment is Calculated
        
        The chart below shows sentiment analysis using TextBlob, a natural language processing library that:
        - Analyzes the emotional tone of each review
        - Assigns scores from -1 (very negative) to 1 (very positive)
        - Calculates daily averages to show trends
        """)
        
        # Create sentiment DataFrame
        sentiment_df = period_df.groupby('date')['sentiment'].mean().reset_index()
        sentiment_df.columns = ["Date", "Average Sentiment"]
        
        # Display sentiment chart
        st.line_chart(
            sentiment_df.set_index("Date"),
            use_container_width=True,
            y="Average Sentiment"
        )
        
        # Display sentiment statistics
        st.markdown(f"""
        **TextBlob Analysis Results:**
        - **Average Sentiment**: {sentiment_df['Average Sentiment'].mean():.2f}
        - **Most Positive Day**: {sentiment_df.loc[sentiment_df['Average Sentiment'].idxmax(), 'Date']} ({sentiment_df['Average Sentiment'].max():.2f})
        - **Most Negative Day**: {sentiment_df.loc[sentiment_df['Average Sentiment'].idxmin(), 'Date']} ({sentiment_df['Average Sentiment'].min():.2f})
        """)

        # Display raw reviews at the bottom
        display_section_header("Raw Reviews", "📄")
        st.dataframe(period_df.sort_values("date", ascending=False))

# Footer
st.markdown("---")
st.markdown("Powered by Streamlit | Data sourced from Google Play Store")

def display_period_summary(df: pd.DataFrame, start_date: datetime, end_date: datetime) -> None:
    """
    Display summary for a single period.
    """
    period_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    st.markdown(f"### Period Summary ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Reviews", f"{len(period_df):.0f}")
    with col2:
        st.metric("Average Sentiment", f"{period_df['sentiment'].mean():.2f}")
    with col3:
        st.metric("Average Rating", f"{period_df['score'].mean():.1f}" if 'score' in period_df.columns else "N/A")
    with col4:
        st.metric("Response Rate", f"{period_df['has_reply'].mean():.1%}" if 'has_reply' in period_df.columns else "N/A")
    
    # Topic Analysis
    st.markdown("#### Top Recurring Topics")
    topics = extract_topics(period_df["text"].tolist(), n_topics=5)
    for topic, frequency in topics:
        st.markdown(f"- **{topic}** ({frequency:.1%} of reviews)")
    
    # Theme Analysis
    st.markdown("#### Review Themes")
    theme_scores = tag_reviews_by_theme(period_df["text"].tolist())
    
    # Calculate average theme scores
    theme_avgs = {}
    for theme in ['UX', 'Performance', 'Features', 'Bugs', 'Content', 'Support']:
        scores = [score[theme] for score in theme_scores]
        theme_avgs[theme] = sum(scores) / len(scores)
    
    # Display theme distribution
    theme_df = pd.DataFrame([
        {"Theme": theme, "Score": score}
        for theme, score in theme_avgs.items()
    ])
    st.bar_chart(theme_df.set_index("Theme"))
    
    # Add theme tags to the reviews table
    period_df['themes'] = [
        ', '.join([theme for theme, score in scores.items() if score > 0.3])
        for scores in theme_scores
    ]

# ... existing code ... 