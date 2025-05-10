"""
UI components for the AI Sentiment Scanner app.
"""
import streamlit as st
from core.settings import DEFAULT_URLS
from core.utils import clear_cache, get_snapshot_info, clear_snapshots
from datetime import datetime, timedelta

def setup_sidebar():
    """
    Setup the sidebar with app selection and date range inputs.
    """
    st.sidebar.markdown("### App Selection")
    
    # Pre-configured apps dropdown
    selected_app = st.sidebar.selectbox(
        "Select a pre-configured app",
        options=["Custom URL"] + list(DEFAULT_URLS.keys()),
        index=0,
        help="Choose from pre-configured apps or enter a custom URL"
    )
    
    # URL input (show only if custom URL is selected)
    if selected_app == "Custom URL":
        url = st.sidebar.text_input(
            "Google Play Store URL",
            placeholder="https://play.google.com/store/apps/details?id=...",
            help="Enter the Google Play Store URL of the app you want to analyze"
        )
    else:
        url = DEFAULT_URLS[selected_app]
        st.sidebar.info(f"Selected app: {selected_app}")
    
    # Date Range Selection
    st.sidebar.markdown("### Date Range Selection")
    
    # Date range inputs
    col1, col2 = st.sidebar.columns(2)
    with col1:
        period1_start = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30),
            key="period1_start",
            help="Select the start date for analysis"
        )
    with col2:
        period1_end = st.date_input(
            "End Date",
            value=datetime.now(),
            key="period1_end",
            help="Select the end date for analysis"
        )
    
    return url, period1_start, period1_end

def setup_comparison_sidebar():
    """
    Setup the sidebar with app selection and two date range inputs for comparison.
    """
    st.sidebar.markdown("### App Selection")
    
    # Pre-configured apps dropdown
    selected_app = st.sidebar.selectbox(
        "Select a pre-configured app",
        options=["Custom URL"] + list(DEFAULT_URLS.keys()),
        index=0,
        help="Choose from pre-configured apps or enter a custom URL"
    )
    
    # URL input (show only if custom URL is selected)
    if selected_app == "Custom URL":
        url = st.sidebar.text_input(
            "Google Play Store URL",
            placeholder="https://play.google.com/store/apps/details?id=...",
            help="Enter the Google Play Store URL of the app you want to analyze"
        )
    else:
        url = DEFAULT_URLS[selected_app]
        st.sidebar.info(f"Selected app: {selected_app}")
    
    # Date Range Selection
    st.sidebar.markdown("### First Period")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        period1_start = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30),
            key="period1_start",
            help="Select the start date for the first period"
        )
    with col2:
        period1_end = st.date_input(
            "End Date",
            value=datetime.now(),
            key="period1_end",
            help="Select the end date for the first period"
        )
    
    st.sidebar.markdown("### Second Period")
    col3, col4 = st.sidebar.columns(2)
    with col3:
        period2_start = st.date_input(
            "Start Date",
            value=period1_start - timedelta(days=30),
            key="period2_start",
            help="Select the start date for the second period"
        )
    with col4:
        period2_end = st.date_input(
            "End Date",
            value=period1_end - timedelta(days=30),
            key="period2_end",
            help="Select the end date for the second period"
        )
    
    return url, period1_start, period1_end, period2_start, period2_end

def display_metric_card(title: str, value: str, description: str):
    """
    Display a metric card with title, value, and description.
    """
    st.metric(
        label=title,
        value=value,
        help=description
    )

def display_summary_box(title: str, content: str):
    """
    Display a summary box with title and content.
    """
    st.markdown('<div class="summary-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="content-text">{content}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def display_section_header(title: str, icon: str):
    """
    Display a section header with an icon.
    """
    st.markdown(f"## {icon} {title}")
    st.markdown("---")

def display_cache_management() -> None:
    """
    Display cache and snapshot management UI in the sidebar.
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("Cache Management")
    
    # Display snapshot statistics
    snapshot_info = get_snapshot_info()
    st.sidebar.markdown(f"**Total Snapshots:** {snapshot_info['total_snapshots']}")
    st.sidebar.markdown(f"**Total Size:** {snapshot_info['total_size'] / 1024:.1f} KB")
    
    # Display app-specific snapshot info
    if snapshot_info['apps']:
        st.sidebar.markdown("**App Snapshots:**")
        for app_name, info in snapshot_info['apps'].items():
            latest_date = info['latest_date'].strftime("%Y-%m-%d") if info['latest_date'] else "N/A"
            st.sidebar.markdown(f"- {app_name}: {info['snapshots']} snapshots, latest: {latest_date}")
    
    # Cache management buttons
    col1, col2 = st.sidebar.columns(2)
    
    if col1.button("Clear Cache"):
        try:
            clear_cache()
            st.sidebar.success("Cache cleared successfully!")
        except Exception as e:
            st.sidebar.error(f"Error clearing cache: {str(e)}")
    
    if col2.button("Clear Old Snapshots"):
        try:
            clear_snapshots()
            st.sidebar.success("Old snapshots cleared successfully!")
        except Exception as e:
            st.sidebar.error(f"Error clearing snapshots: {str(e)}") 