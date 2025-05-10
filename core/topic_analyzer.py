import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter
from typing import List, Dict, Tuple
import numpy as np
from datetime import datetime, timedelta

def extract_topics(texts: List[str], n_topics: int = 5) -> List[Tuple[str, float]]:
    """
    Extract top N recurring topics from review texts using TF-IDF and clustering.
    
    Args:
        texts: List of review texts
        n_topics: Number of topics to extract
        
    Returns:
        List of tuples containing (topic, frequency)
    """
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2)
    )
    
    # Transform texts to TF-IDF matrix
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    # Perform clustering
    kmeans = KMeans(n_clusters=n_topics, random_state=42)
    clusters = kmeans.fit_predict(tfidf_matrix)
    
    # Get feature names
    feature_names = vectorizer.get_feature_names_out()
    
    # Extract top terms for each cluster
    topics = []
    for i in range(n_topics):
        # Get cluster center
        center = kmeans.cluster_centers_[i]
        
        # Get top terms for this cluster
        top_indices = center.argsort()[-5:][::-1]
        top_terms = [feature_names[idx] for idx in top_indices]
        
        # Calculate frequency
        cluster_size = np.sum(clusters == i)
        frequency = cluster_size / len(texts)
        
        topics.append((' '.join(top_terms), frequency))
    
    return sorted(topics, key=lambda x: x[1], reverse=True)

def analyze_topic_changes(current_texts: List[str], previous_texts: List[str], n_topics: int = 5) -> Dict[str, float]:
    """
    Analyze changes in topic frequency between current and previous periods.
    
    Args:
        current_texts: List of current period review texts
        previous_texts: List of previous period review texts
        n_topics: Number of topics to analyze
        
    Returns:
        Dictionary mapping topics to their frequency change
    """
    # Extract topics for both periods
    current_topics = dict(extract_topics(current_texts, n_topics))
    previous_topics = dict(extract_topics(previous_texts, n_topics))
    
    # Calculate changes
    changes = {}
    all_topics = set(current_topics.keys()) | set(previous_topics.keys())
    
    for topic in all_topics:
        current_freq = current_topics.get(topic, 0)
        previous_freq = previous_topics.get(topic, 0)
        changes[topic] = current_freq - previous_freq
    
    return changes

def tag_reviews_by_theme(texts: List[str]) -> List[Dict[str, float]]:
    """
    Tag reviews with themes using predefined categories.
    
    Args:
        texts: List of review texts
        
    Returns:
        List of dictionaries containing theme probabilities for each review
    """
    # Define theme keywords
    themes = {
        'UX': ['interface', 'design', 'layout', 'user experience', 'ui', 'navigation', 'menu'],
        'Performance': ['slow', 'lag', 'crash', 'freeze', 'speed', 'performance', 'battery'],
        'Features': ['feature', 'function', 'option', 'capability', 'tool'],
        'Bugs': ['bug', 'error', 'issue', 'problem', 'glitch', 'not working'],
        'Content': ['content', 'information', 'data', 'update', 'news'],
        'Support': ['support', 'help', 'customer service', 'response', 'contact']
    }
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2)
    )
    
    # Transform texts
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()
    
    # Calculate theme probabilities for each review
    theme_scores = []
    for i in range(len(texts)):
        review_scores = {}
        for theme, keywords in themes.items():
            # Calculate score based on keyword presence
            score = sum(1 for keyword in keywords if keyword in texts[i].lower())
            review_scores[theme] = score / len(keywords)  # Normalize by number of keywords
        
        theme_scores.append(review_scores)
    
    return theme_scores

def get_period_texts(df: pd.DataFrame, period_days: int) -> Tuple[List[str], List[str]]:
    """
    Split reviews into current and previous period texts.
    
    Args:
        df: DataFrame containing reviews
        period_days: Number of days in each period
        
    Returns:
        Tuple of (current_period_texts, previous_period_texts)
    """
    # Convert date column to datetime if it's not already
    df['date'] = pd.to_datetime(df['date'])
    
    # Get current period end date
    end_date = df['date'].max()
    current_start = end_date - timedelta(days=period_days)
    previous_start = current_start - timedelta(days=period_days)
    
    # Split into periods
    current_period = df[df['date'] >= current_start]
    previous_period = df[(df['date'] >= previous_start) & (df['date'] < current_start)]
    
    return current_period['text'].tolist(), previous_period['text'].tolist() 