from textblob import TextBlob
import pandas as pd
import numpy as np
from typing import List, Dict

def analyze_sentiment(text: str) -> float:
    """
    Analyze sentiment of a single text using TextBlob.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        float: Sentiment polarity (-1 to 1)
    """
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def analyze_all(reviews: List[Dict]) -> pd.DataFrame:
    """
    Analyze sentiment for all reviews and return a DataFrame with results.
    
    Args:
        reviews (List[Dict]): List of review dictionaries
        
    Returns:
        pd.DataFrame: DataFrame with analysis results
    """
    # Convert reviews to DataFrame
    df = pd.DataFrame(reviews)
    
    # Print the columns to debug
    print("Available columns:", df.columns.tolist())
    
    # Ensure we have the required columns
    if 'review' not in df.columns:
        raise ValueError("Reviews must contain 'review' field. Available fields: " + str(df.columns.tolist()))
    
    # Clean and analyze text
    df['text'] = df['review'].astype(str)
    df['sentiment'] = df['text'].apply(analyze_sentiment)
    
    # Calculate engagement score (using likes/helpful votes if available)
    if 'thumbsUpCount' in df.columns:
        df['engagement'] = df['thumbsUpCount'].fillna(0)
    else:
        df['engagement'] = 0
    
    # Format dates
    if 'at' in df.columns:
        df['date'] = pd.to_datetime(df['at']).dt.strftime('%Y-%m-%d')
    elif 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    else:
        df['date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
    
    # Add reply information if available
    if 'replyContent' in df.columns:
        df['has_reply'] = df['replyContent'].notna()
        if 'repliedAt' in df.columns:
            df['reply_date'] = pd.to_datetime(df['repliedAt']).dt.strftime('%Y-%m-%d')
    
    return df

def get_review_stats(df: pd.DataFrame) -> Dict:
    """
    Calculate review statistics.
    
    Args:
        df (pd.DataFrame): DataFrame with review data
        
    Returns:
        Dict: Dictionary of statistics
    """
    stats = {
        'total_reviews': len(df),
        'average_rating': df['score'].mean() if 'score' in df.columns else None,
        'average_sentiment': df['sentiment'].mean(),
        'average_engagement': df['engagement'].mean(),
        'reply_rate': df['has_reply'].mean() if 'has_reply' in df.columns else 0,
        'most_engaged_review': df.loc[df['engagement'].idxmax()]['text'] if 'engagement' in df.columns else None
    }
    return stats

def get_rating_distribution(df: pd.DataFrame) -> pd.Series:
    """
    Get the distribution of ratings.
    
    Args:
        df (pd.DataFrame): DataFrame with review data
        
    Returns:
        pd.Series: Series with rating counts
    """
    if 'score' in df.columns:
        return df['score'].value_counts().sort_index()
    return pd.Series()

def get_sentiment_by_rating(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get average sentiment by rating.
    
    Args:
        df (pd.DataFrame): DataFrame with review data
        
    Returns:
        pd.DataFrame: DataFrame with sentiment by rating
    """
    if 'score' in df.columns:
        return df.groupby('score')['sentiment'].mean().reset_index()
    return pd.DataFrame() 