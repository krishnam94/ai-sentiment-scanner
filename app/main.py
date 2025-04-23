import os
import sys
import io
import re

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import streamlit as st
from core.review_fetcher import fetch_reviews
from core.analyzer import analyze_all
from core.utils import cached_summary, store_snapshot, load_snapshot
from components.ui import setup_sidebar, display_metric_card, display_summary_box, display_section_header
from components.analysis import (
    create_sentiment_dataframe,
    calculate_comparison_metrics,
    generate_competitive_summary,
    generate_app_summary
)
from components.competitive_viz import display_competitive_metrics
import pandas as pd
import logging

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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
load_css()

# Title and description
st.title("📱 AI Sentiment Scanner: App Review Analysis")
st.markdown("""
This tool analyzes and compares Google Play Store reviews for different apps.
Select two apps below to compare their reviews, sentiment trends, and get AI-powered summaries.
""", unsafe_allow_html=True)

# Setup sidebar and get inputs
url1, url2, review_count = setup_sidebar()

# Extract app IDs
app_id1 = extract_app_id(url1) if url1 else None
app_id2 = extract_app_id(url2) if url2 else None

# Main content
if st.sidebar.button("Compare Apps"):
    if not app_id1 or not app_id2:
        st.error("Please enter valid Google Play Store URLs for both apps")
        st.stop()
        
    with st.spinner("Fetching reviews or loading snapshots..."):
        # Clear previous logs
        log_stream.truncate(0)
        log_stream.seek(0)
        
        print("\n=== Starting App Comparison ===")
        
        # Fetch or load reviews for first app
        print(f"\nProcessing {app_id1}...")
        logger.info(f"Starting process for {app_id1}")
        reviews1 = load_snapshot(app_id1)
        if not reviews1:
            print(f"Fetching fresh reviews for {app_id1}")
            logger.info(f"Fetching fresh reviews for {app_id1}")
            try:
                reviews1 = fetch_reviews(app_id1, review_count)
                if reviews1:
                    print(f"Successfully fetched {len(reviews1)} reviews for {app_id1}")
                    logger.info(f"Successfully fetched {len(reviews1)} reviews for {app_id1}")
                    app_info1 = app(app_id1)
                    store_snapshot(app_info1['title'], reviews1, review_count)
                else:
                    st.error(f"Could not fetch reviews for {app_id1}. Please try again later.")
                    logger.error(f"No reviews returned for {app_id1}")
                    st.stop()
            except Exception as e:
                st.error(f"Error fetching reviews for {app_id1}: {str(e)}")
                logger.error(f"Error fetching reviews for {app_id1}: {str(e)}", exc_info=True)
                st.stop()

        # Fetch or load reviews for second app
        print(f"\nProcessing {app_id2}...")
        logger.info(f"Starting process for {app_id2}")
        reviews2 = load_snapshot(app_id2)
        if not reviews2:
            print(f"Fetching fresh reviews for {app_id2}")
            logger.info(f"Fetching fresh reviews for {app_id2}")
            try:
                reviews2 = fetch_reviews(app_id2, review_count)
                if reviews2:
                    print(f"Successfully fetched {len(reviews2)} reviews for {app_id2}")
                    logger.info(f"Successfully fetched {len(reviews2)} reviews for {app_id2}")
                    app_info2 = app(app_id2)
                    store_snapshot(app_info2['title'], reviews2, review_count)
                else:
                    st.error(f"Could not fetch reviews for {app_id2}. Please try again later.")
                    logger.error(f"No reviews returned for {app_id2}")
                    st.stop()
            except Exception as e:
                st.error(f"Error fetching reviews for {app_id2}: {str(e)}")
                logger.error(f"Error fetching reviews for {app_id2}: {str(e)}", exc_info=True)
                st.stop()

        # Analyze reviews
        try:
            print("\nAnalyzing reviews...")
            logger.info("Analyzing reviews for both apps")
            df1 = analyze_all(reviews1)
            df2 = analyze_all(reviews2)
            print(f"Analysis complete. df1 shape: {df1.shape}, df2 shape: {df2.shape}")
            logger.info(f"Analysis complete. df1 shape: {df1.shape}, df2 shape: {df2.shape}")
        except Exception as e:
            print(f"Error analyzing reviews: {str(e)}")
            logger.error(f"Error analyzing reviews: {str(e)}", exc_info=True)
            st.error(f"Error analyzing reviews: {str(e)}")
            st.stop()

    st.success("Analysis complete!")

    # Display logs
    with st.expander("Debug Information", expanded=False):
        st.text(log_stream.getvalue())

    # Create sentiment DataFrames
    sentiment_df1 = create_sentiment_dataframe(df1)
    sentiment_df2 = create_sentiment_dataframe(df2)

    # Competitive Analysis Summary
    display_section_header("Competitive Analysis Summary", "🏆")
    
    # Calculate and display key metrics
    metrics = calculate_comparison_metrics(df1, df2)
    
    # Display key metrics in a more concise format
    col1, col2, col3 = st.columns(3)
    with col1:
        display_metric_card(
            "Sentiment",
            f"{metrics['sentiment_diff']:+.2f}",
            "Higher is better"
        )
    with col2:
        display_metric_card(
            "Reviews",
            f"{metrics['review_count_diff']:+d}",
            "More reviews"
        )
    with col3:
        display_metric_card(
            "Engagement",
            f"{metrics['engagement_diff']:+.1f}",
            "Higher engagement"
        )
    
    # Display competitive metrics in a compact format
    with st.expander("Detailed Comparison", expanded=True):
        display_competitive_metrics(df1, df2)
        
        # Generate and display competitive summary
        try:
            competitive_summary = generate_competitive_summary(
                df1, df2, app_id1, app_id2, review_count,
                f"App ID: {app_id1}", f"App ID: {app_id2}"
            )
            display_summary_box("Key Competitive Insights", competitive_summary)
        except Exception as e:
            logger.error(f"Error generating competitive summary: {str(e)}", exc_info=True)
            st.error(f"Error generating competitive summary: {str(e)}")

    # Individual App Summaries
    display_section_header("AI-Powered Review Analysis", "🧠")
    st.markdown("""
    The summaries below are generated using GPT-4 and provide deeper insights into user feedback.
    Each analysis includes sentiment scoring and key highlights.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        display_section_header(f"App ID: {app_id1}")
        try:
            summary1 = generate_app_summary(df1, app_id1, review_count, f"App ID: {app_id1}")
            display_summary_box("Summary", summary1)
            
            # Display metrics
            display_section_header("📊 Key Metrics")
            col_metric1, col_metric2, col_metric3 = st.columns(3)
            with col_metric1:
                display_metric_card(
                    "Overall Sentiment",
                    f"{sentiment_df1['Average Sentiment'].mean():.2f}",
                    "Average sentiment score (-1 to 1)"
                )
            with col_metric2:
                display_metric_card(
                    "Review Count",
                    str(len(df1)),
                    "Total number of reviews analyzed"
                )
            with col_metric3:
                display_metric_card(
                    "Engagement",
                    f"{df1['engagement'].mean():.1f}",
                    "Average likes per review"
                )
        except Exception as e:
            logger.error(f"Error generating summary for {app_id1}: {str(e)}", exc_info=True)
            st.error(f"Error generating summary for {app_id1}: {str(e)}")
            
    with col2:
        display_section_header(f"App ID: {app_id2}")
        try:
            summary2 = generate_app_summary(df2, app_id2, review_count, f"App ID: {app_id2}")
            display_summary_box("Summary", summary2)
            
            # Display metrics
            display_section_header("📊 Key Metrics")
            col_metric1, col_metric2, col_metric3 = st.columns(3)
            with col_metric1:
                display_metric_card(
                    "Overall Sentiment",
                    f"{sentiment_df2['Average Sentiment'].mean():.2f}",
                    "Average sentiment score (-1 to 1)"
                )
            with col_metric2:
                display_metric_card(
                    "Review Count",
                    str(len(df2)),
                    "Total number of reviews analyzed"
                )
            with col_metric3:
                display_metric_card(
                    "Engagement",
                    f"{df2['engagement'].mean():.1f}",
                    "Average likes per review"
                )
        except Exception as e:
            logger.error(f"Error generating summary for {app_id2}: {str(e)}", exc_info=True)
            st.error(f"Error generating summary for {app_id2}: {str(e)}")

    # Sentiment Analysis Over Time
    display_section_header("Sentiment Analysis Over Time", "📊")
    st.markdown("""
    ### How Sentiment is Calculated
    
    The charts below show sentiment analysis using TextBlob, a natural language processing library that:
    - Analyzes the emotional tone of each review
    - Assigns scores from -1 (very negative) to 1 (very positive)
    - Calculates daily averages to show trends
    
    This is separate from the AI summaries above, which use GPT-4 to provide detailed insights.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### App ID: {app_id1}")
        st.line_chart(
            sentiment_df1.set_index("Date"),
            use_container_width=True,
            y="Average Sentiment"
        )
        st.markdown(f"""
        **TextBlob Analysis Results:**
        - **Average Sentiment**: {sentiment_df1['Average Sentiment'].mean():.2f}
        - **Most Positive Day**: {sentiment_df1.loc[sentiment_df1['Average Sentiment'].idxmax(), 'Date']} ({sentiment_df1['Average Sentiment'].max():.2f})
        - **Most Negative Day**: {sentiment_df1.loc[sentiment_df1['Average Sentiment'].idxmin(), 'Date']} ({sentiment_df1['Average Sentiment'].min():.2f})
        """)
    with col2:
        st.markdown(f"### App ID: {app_id2}")
        st.line_chart(
            sentiment_df2.set_index("Date"),
            use_container_width=True,
            y="Average Sentiment"
        )
        st.markdown(f"""
        **TextBlob Analysis Results:**
        - **Average Sentiment**: {sentiment_df2['Average Sentiment'].mean():.2f}
        - **Most Positive Day**: {sentiment_df2.loc[sentiment_df2['Average Sentiment'].idxmax(), 'Date']} ({sentiment_df2['Average Sentiment'].max():.2f})
        - **Most Negative Day**: {sentiment_df2.loc[sentiment_df2['Average Sentiment'].idxmin(), 'Date']} ({sentiment_df2['Average Sentiment'].min():.2f})
        """)

    # Raw Reviews
    display_section_header("Raw Reviews for Both Apps", "📄")
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(df1.sort_values("date", ascending=False))
    with col2:
        st.dataframe(df2.sort_values("date", ascending=False))

# Footer
st.markdown("---")
st.markdown("Powered by Streamlit | Data sourced from Google Play Store") 