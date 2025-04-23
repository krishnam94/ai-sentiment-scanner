"""
Competitive analysis visualization components for the AI Sentiment Scanner app.
"""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_radar_chart(metrics1, metrics2, labels):
    """Create a radar chart comparing two apps across multiple metrics."""
    fig = go.Figure()
    
    # Add traces for both apps
    fig.add_trace(go.Scatterpolar(
        r=metrics1,
        theta=labels,
        fill='toself',
        name='App 1',
        line_color='#1f77b4'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=metrics2,
        theta=labels,
        fill='toself',
        name='App 2',
        line_color='#ff7f0e'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        title="App Comparison Radar Chart",
        height=400
    )
    
    return fig

def create_score_cards(metrics1, metrics2, labels):
    """Create score cards showing the comparison between two apps."""
    col1, col2, col3 = st.columns(3)
    
    for i, (label, score1, score2) in enumerate(zip(labels, metrics1, metrics2)):
        col = [col1, col2, col3][i % 3]
        with col:
            st.markdown(f"**{label}**")
            st.markdown(f"""
            <div class="score-card">
                <div class="score-value">{score1:.2f}</div>
                <div class="score-value">{score2:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<div class='score-label'>App 1 vs App 2</div>", unsafe_allow_html=True)

def display_competitive_metrics(df1, df2):
    """Display competitive metrics and visualizations."""
    # Calculate metrics for both apps
    metrics1 = {
        "Sentiment": df1['sentiment'].mean(),
        "Engagement": df1['engagement'].mean(),
        "Review Count": len(df1),
        "Positive Reviews": (df1['sentiment'] > 0).mean(),
        "Response Rate": df1['response'].notna().mean() if 'response' in df1.columns else 0
    }
    
    metrics2 = {
        "Sentiment": df2['sentiment'].mean(),
        "Engagement": df2['engagement'].mean(),
        "Review Count": len(df2),
        "Positive Reviews": (df2['sentiment'] > 0).mean(),
        "Response Rate": df2['response'].notna().mean() if 'response' in df2.columns else 0
    }
    
    # Normalize metrics for radar chart
    max_values = {
        "Sentiment": 1.0,
        "Engagement": max(metrics1["Engagement"], metrics2["Engagement"]),
        "Review Count": max(metrics1["Review Count"], metrics2["Review Count"]),
        "Positive Reviews": 1.0,
        "Response Rate": 1.0
    }
    
    normalized_metrics1 = [metrics1[k] / max_values[k] for k in metrics1.keys()]
    normalized_metrics2 = [metrics2[k] / max_values[k] for k in metrics2.keys()]
    
    # Create and display radar chart
    st.plotly_chart(
        create_radar_chart(
            normalized_metrics1,
            normalized_metrics2,
            list(metrics1.keys())
        ),
        use_container_width=True
    )
    
    # Display score cards
    st.markdown("### Detailed Metrics Comparison")
    create_score_cards(
        list(metrics1.values()),
        list(metrics2.values()),
        list(metrics1.keys())
    )
    
    # Add CSS for score cards
    st.markdown("""
    <style>
    .score-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        text-align: center;
    }
    .score-value {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .score-label {
        font-size: 0.8rem;
        color: #666;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True) 