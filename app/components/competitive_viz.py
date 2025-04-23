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
    """Display competitive metrics and visualizations focusing on key differentiators."""
    # Calculate key metrics for both apps
    metrics1 = {
        "Sentiment": df1['sentiment'].mean(),
        "Engagement": df1['engagement'].mean(),
        "Reviews": len(df1),
        "Satisfaction": (df1['sentiment'] > 0).mean(),
    }
    
    metrics2 = {
        "Sentiment": df2['sentiment'].mean(),
        "Engagement": df2['engagement'].mean(),
        "Reviews": len(df2),
        "Satisfaction": (df2['sentiment'] > 0).mean(),
    }
    
    # Calculate differences and identify key differentiators
    differences = {
        k: abs(metrics1[k] - metrics2[k]) for k in metrics1.keys()
    }
    significant_diffs = {k: v for k, v in differences.items() if v > 0.1}  # Threshold for significant difference
    
    # Display key differentiators
    st.markdown("### Key Differences")
    for metric in significant_diffs:
        value1 = metrics1[metric]
        value2 = metrics2[metric]
        diff = value1 - value2
        
        # Format the values based on metric type
        if metric in ["Sentiment", "Satisfaction"]:
            value1_str = f"{value1:.2f}"
            value2_str = f"{value2:.2f}"
            diff_str = f"{diff:+.2f}"
        elif metric == "Engagement":
            value1_str = f"{value1:.1f}"
            value2_str = f"{value2:.1f}"
            diff_str = f"{diff:+.1f}"
        else:  # Reviews
            value1_str = f"{value1:,}"
            value2_str = f"{value2:,}"
            diff_str = f"{diff:+,}"
        
        # Determine which app is leading
        leader = "App 1" if diff > 0 else "App 2"
        diff_percent = abs(diff / ((value1 + value2) / 2)) * 100
        
        st.markdown(f"""
        <div class="differentiator-card">
            <div class="metric-name">{metric}</div>
            <div class="metric-values">
                <span class="app1-value">{value1_str}</span>
                <span class="vs">vs</span>
                <span class="app2-value">{value2_str}</span>
            </div>
            <div class="metric-diff">
                <span class="diff-value">{diff_str}</span>
                <span class="leader">({leader} +{diff_percent:.0f}%)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add CSS for differentiator cards
    st.markdown("""
    <style>
    .differentiator-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .metric-name {
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        color: #333;
    }
    .metric-values {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0.5rem 0;
    }
    .app1-value {
        color: #1f77b4;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .app2-value {
        color: #ff7f0e;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .vs {
        color: #666;
        font-size: 0.9rem;
    }
    .metric-diff {
        text-align: center;
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .diff-value {
        font-weight: bold;
        color: #333;
    }
    .leader {
        margin-left: 0.5rem;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True) 