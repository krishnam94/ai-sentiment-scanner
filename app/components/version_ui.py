import streamlit as st
import pandas as pd
from typing import Dict, List, Tuple
from core.version_analyzer import get_version_timeline, compare_versions
from core.topic_analyzer import extract_topics, tag_reviews_by_theme
from datetime import datetime, timedelta

def display_date_range_selector() -> Tuple[datetime, datetime, datetime, datetime]:
    """
    Display date range selection UI for comparison.
    """
    st.markdown("### Select Date Ranges for Comparison")
    
    # Default to last 30 days and previous 30 days
    today = datetime.now()
    default_end = today
    default_start = today - timedelta(days=30)
    default_prev_end = default_start
    default_prev_start = default_prev_end - timedelta(days=30)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Current Period")
        current_start = st.date_input(
            "Start Date",
            value=default_start,
            key="current_start"
        )
        current_end = st.date_input(
            "End Date",
            value=default_end,
            key="current_end"
        )
    
    with col2:
        st.markdown("#### Previous Period")
        prev_start = st.date_input(
            "Start Date",
            value=default_prev_start,
            key="prev_start"
        )
        prev_end = st.date_input(
            "End Date",
            value=default_prev_end,
            key="prev_end"
        )
    
    return (
        datetime.combine(current_start, datetime.min.time()),
        datetime.combine(current_end, datetime.max.time()),
        datetime.combine(prev_start, datetime.min.time()),
        datetime.combine(prev_end, datetime.max.time())
    )

def display_period_comparison(comparison: Dict) -> None:
    """
    Display period comparison results.
    """
    # Sentiment Comparison
    st.subheader("📊 Sentiment Analysis")
    sentiment = comparison['sentiment']
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Previous Period", f"{sentiment['version1']:.2f}")
    with col2:
        st.metric("Current Period", f"{sentiment['version2']:.2f}")
    with col3:
        st.metric("Change", f"{sentiment['delta']:.2f}", 
                 delta=f"{sentiment['delta']:.2f}")
    
    # Theme Comparison
    st.subheader("🎯 Theme Analysis")
    themes = comparison['themes']
    theme_data = []
    for theme, data in themes.items():
        theme_data.append({
            'Theme': theme,
            'Previous Period': data['version1'],
            'Current Period': data['version2'],
            'Change': data['delta']
        })
    theme_df = pd.DataFrame(theme_data)
    st.dataframe(theme_df.style.background_gradient(subset=['Change'], cmap='RdYlGn'))
    
    # Topic Comparison
    st.subheader("📝 Topic Analysis")
    topics = comparison['topics']
    topic_data = []
    for topic, data in topics.items():
        topic_data.append({
            'Topic': topic,
            'Previous Period': data['version1'],
            'Current Period': data['version2'],
            'Change': data['delta']
        })
    topic_df = pd.DataFrame(topic_data)
    st.dataframe(topic_df.style.background_gradient(subset=['Change'], cmap='RdYlGn'))
    
    # Metrics Comparison
    st.subheader("📈 Key Metrics")
    metrics = comparison['metrics']
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Review Count",
            f"{metrics['review_count']['version2']:.0f}",
            f"{metrics['review_count']['delta']:+.0f}"
        )
    
    with col2:
        st.metric(
            "Average Rating",
            f"{metrics['average_rating']['version2']:.1f}",
            f"{metrics['average_rating']['delta']:+.2f}"
        )

def display_period_summary(df: pd.DataFrame, start_date: datetime, end_date: datetime) -> None:
    """
    Display summary for a single period.
    """
    period_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    st.markdown(f"### Period Summary ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})")
    
    # Key Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Reviews", f"{len(period_df):.0f}")
    with col2:
        st.metric("Average Sentiment", f"{period_df['sentiment'].mean():.2f}")
    with col3:
        st.metric("Average Rating", f"{period_df['score'].mean():.1f}" if 'score' in period_df.columns else "N/A")
    
    # Theme Distribution
    st.subheader("🎯 Theme Distribution")
    themes = tag_reviews_by_theme(period_df['text'].tolist())
    theme_avgs = {}
    for theme in ['UX', 'Performance', 'Features', 'Bugs', 'Content', 'Support']:
        scores = [score[theme] for score in themes]
        theme_avgs[theme] = sum(scores) / len(scores) if scores else 0
    
    theme_df = pd.DataFrame([
        {'Theme': theme, 'Score': score}
        for theme, score in theme_avgs.items()
    ])
    st.bar_chart(theme_df.set_index('Theme'))
    
    # Top Topics
    st.subheader("📝 Top Topics")
    topics = extract_topics(period_df['text'].tolist(), n_topics=5)
    for topic, frequency in topics:
        st.markdown(f"- **{topic}** ({frequency:.1%} of reviews)")

def display_version_selector(version_groups: Dict[str, pd.DataFrame]) -> tuple:
    """
    Display version selection UI.
    """
    versions = list(version_groups.keys())
    versions.sort(key=lambda x: [int(n) for n in x.split('.')], reverse=True)
    
    col1, col2 = st.columns(2)
    with col1:
        version1 = st.selectbox(
            "Select First Version",
            versions,
            index=0
        )
    with col2:
        version2 = st.selectbox(
            "Select Second Version",
            versions,
            index=min(1, len(versions)-1)
        )
    
    return version1, version2

def display_version_comparison(comparison: Dict) -> None:
    """
    Display version comparison results.
    """
    # Sentiment Comparison
    st.subheader("📊 Sentiment Analysis")
    sentiment = comparison['sentiment']
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Version 1", f"{sentiment['version1']:.2f}")
    with col2:
        st.metric("Version 2", f"{sentiment['version2']:.2f}")
    with col3:
        st.metric("Change", f"{sentiment['delta']:.2f}", 
                 delta=f"{sentiment['delta']:.2f}")
    
    # Theme Comparison
    st.subheader("🎯 Theme Analysis")
    themes = comparison['themes']
    theme_data = []
    for theme, data in themes.items():
        theme_data.append({
            'Theme': theme,
            'Version 1': data['version1'],
            'Version 2': data['version2'],
            'Change': data['delta']
        })
    theme_df = pd.DataFrame(theme_data)
    st.dataframe(theme_df.style.background_gradient(subset=['Change'], cmap='RdYlGn'))
    
    # Topic Comparison
    st.subheader("📝 Topic Analysis")
    topics = comparison['topics']
    topic_data = []
    for topic, data in topics.items():
        topic_data.append({
            'Topic': topic,
            'Version 1': data['version1'],
            'Version 2': data['version2'],
            'Change': data['delta']
        })
    topic_df = pd.DataFrame(topic_data)
    st.dataframe(topic_df.style.background_gradient(subset=['Change'], cmap='RdYlGn'))
    
    # Metrics Comparison
    st.subheader("📈 Key Metrics")
    metrics = comparison['metrics']
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Review Count",
            f"{metrics['review_count']['version2']:.0f}",
            f"{metrics['review_count']['delta']:+.0f}"
        )
    
    with col2:
        st.metric(
            "Average Rating",
            f"{metrics['average_rating']['version2']:.1f}",
            f"{metrics['average_rating']['delta']:+.2f}"
        )

def display_version_timeline(timeline: List[Dict]) -> None:
    """
    Display version release timeline.
    """
    st.subheader("📅 Version Timeline")
    timeline_df = pd.DataFrame(timeline)
    timeline_df['date'] = pd.to_datetime(timeline_df['date'])
    timeline_df = timeline_df.sort_values('date')
    
    # Display timeline
    for _, row in timeline_df.iterrows():
        st.markdown(f"**Version {row['version']}** - {row['date'].strftime('%Y-%m-%d')}") 