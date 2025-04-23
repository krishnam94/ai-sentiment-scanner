"""
Analysis components for the AI Sentiment Scanner app.
"""
import pandas as pd
from core.summarizer import summarize_themes
from core.utils import cached_summary
from core.settings import COMPETITIVE_ANALYSIS_PROMPT

def create_sentiment_dataframe(df):
    """Create a sentiment DataFrame with date and average sentiment."""
    sentiment_df = df.groupby("date")["sentiment"].mean().reset_index()
    sentiment_df.columns = ["Date", "Average Sentiment"]
    return sentiment_df

def calculate_comparison_metrics(df1, df2):
    """Calculate comparison metrics between two apps."""
    avg_sentiment1 = df1.groupby("date")["sentiment"].mean().mean()
    avg_sentiment2 = df2.groupby("date")["sentiment"].mean().mean()
    review_count1 = len(df1)
    review_count2 = len(df2)
    engagement1 = df1['engagement'].mean()
    engagement2 = df2['engagement'].mean()
    
    return {
        "sentiment_diff": avg_sentiment2 - avg_sentiment1,
        "review_count_diff": review_count2 - review_count1,
        "engagement_diff": engagement2 - engagement1
    }

def generate_competitive_summary(df1, df2, app_id1, app_id2, review_count, display_name1, display_name2):
    """Generate a competitive analysis summary."""
    try:
        # Get individual app summaries
        summary1 = cached_summary(
            df1["text"].tolist(),
            summarize_themes,
            f"{app_id1}_{review_count}"
        )
        
        summary2 = cached_summary(
            df2["text"].tolist(),
            summarize_themes,
            f"{app_id2}_{review_count}"
        )
        
        # Create the prompt
        prompt = COMPETITIVE_ANALYSIS_PROMPT.format(
            app1=display_name1,
            app2=display_name2
        )
        
        # Create a wrapper function that includes the prompt
        def summarize_with_prompt(texts):
            return summarize_themes(texts, prompt=prompt, max_tokens=1000)
        
        # Generate competitive summary
        cache_key = f"competitive_{app_id1}_{app_id2}_{review_count}"
        competitive_summary = cached_summary(
            [summary1, summary2],
            summarize_with_prompt,
            cache_key
        )
        
        return competitive_summary
    except Exception as e:
        raise Exception(f"Error generating competitive summary: {str(e)}")

def generate_app_summary(df, app_id, review_count, display_name):
    """Generate a summary for a single app."""
    try:
        summary = cached_summary(
            df["text"].tolist(),
            summarize_themes,
            f"{app_id}_{review_count}"
        )
        return summary
    except Exception as e:
        raise Exception(f"Error generating summary for {display_name}: {str(e)}") 