"""
UI components for the AI Sentiment Scanner app.
"""
import streamlit as st
from core.settings import DEFAULT_URLS, REVIEW_COUNT_RANGE
from core.cache_manager import clear_cache

def setup_sidebar():
    """Setup the sidebar configuration."""
    st.sidebar.title("Configuration")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        default_app1 = st.selectbox("Choose first app:", list(DEFAULT_URLS.keys()), key="app1")
        url1 = st.text_input("Or enter first app's Google Play Store URL:", 
                           value=DEFAULT_URLS[default_app1], key="url1")
    with col2:
        default_app2 = st.selectbox("Choose second app:", list(DEFAULT_URLS.keys()), key="app2")
        url2 = st.text_input("Or enter second app's Google Play Store URL:", 
                           value=DEFAULT_URLS[default_app2], key="url2")
    
    review_count = st.sidebar.slider(
        "Number of recent reviews to analyze:",
        min_value=REVIEW_COUNT_RANGE["min"],
        max_value=REVIEW_COUNT_RANGE["max"],
        value=REVIEW_COUNT_RANGE["default"],
        step=REVIEW_COUNT_RANGE["step"]
    )
    
    # Add cache clearing button
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Clear Cache", help="Remove all cached review data"):
        try:
            clear_cache()
            st.sidebar.success("Cache cleared successfully!")
        except Exception as e:
            st.sidebar.error(f"Error clearing cache: {str(e)}")
    
    return url1, url2, review_count

def display_metric_card(title, value, help_text):
    """Display a metric card with consistent styling."""
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(title, value, help=help_text)
    st.markdown('</div>', unsafe_allow_html=True)

def display_summary_box(title, content):
    """Display a summary box with consistent styling."""
    st.markdown('<div class="summary-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="content-text">{content}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def display_section_header(title, icon=None):
    """Display a section header with optional icon."""
    if icon:
        st.subheader(f"{icon} {title}")
    else:
        st.subheader(title) 