import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
from .topic_analyzer import extract_topics, tag_reviews_by_theme
import re

def extract_version_from_review(review_text: str) -> str:
    """
    Extract version number from review text using common patterns.
    """
    # Common version patterns
    patterns = [
        r'version\s+(\d+\.\d+(?:\.\d+)?)',  # version 1.2.3
        r'v(\d+\.\d+(?:\.\d+)?)',          # v1.2.3
        r'(\d+\.\d+(?:\.\d+)?)\s+version', # 1.2.3 version
        r'update\s+(\d+\.\d+(?:\.\d+)?)',  # update 1.2.3
    ]
    
    for pattern in patterns:
        match = re.search(pattern, review_text.lower())
        if match:
            return match.group(1)
    return None

def group_reviews_by_version(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Group reviews by version number.
    """
    # Extract versions from review texts
    df['version'] = df['text'].apply(extract_version_from_review)
    
    # Group by version
    version_groups = {}
    for version, group in df.groupby('version'):
        if version:  # Only include reviews with detected versions
            version_groups[version] = group
    
    return version_groups

def compare_versions(version1: pd.DataFrame, version2: pd.DataFrame) -> Dict[str, Dict]:
    """
    Compare two versions of the app based on reviews.
    """
    comparison = {
        'sentiment': {},
        'topics': {},
        'themes': {},
        'metrics': {}
    }
    
    # Compare sentiment
    comparison['sentiment'] = {
        'version1': version1['sentiment'].mean(),
        'version2': version2['sentiment'].mean(),
        'delta': version2['sentiment'].mean() - version1['sentiment'].mean()
    }
    
    # Compare topics
    topics1 = dict(extract_topics(version1['text'].tolist()))
    topics2 = dict(extract_topics(version2['text'].tolist()))
    
    all_topics = set(topics1.keys()) | set(topics2.keys())
    topic_changes = {}
    for topic in all_topics:
        freq1 = topics1.get(topic, 0)
        freq2 = topics2.get(topic, 0)
        topic_changes[topic] = {
            'version1': freq1,
            'version2': freq2,
            'delta': freq2 - freq1
        }
    comparison['topics'] = topic_changes
    
    # Compare themes
    themes1 = tag_reviews_by_theme(version1['text'].tolist())
    themes2 = tag_reviews_by_theme(version2['text'].tolist())
    
    theme_avgs1 = {}
    theme_avgs2 = {}
    for theme in ['UX', 'Performance', 'Features', 'Bugs', 'Content', 'Support']:
        scores1 = [score[theme] for score in themes1]
        scores2 = [score[theme] for score in themes2]
        theme_avgs1[theme] = sum(scores1) / len(scores1) if scores1 else 0
        theme_avgs2[theme] = sum(scores2) / len(scores2) if scores2 else 0
    
    theme_changes = {}
    for theme in theme_avgs1.keys():
        theme_changes[theme] = {
            'version1': theme_avgs1[theme],
            'version2': theme_avgs2[theme],
            'delta': theme_avgs2[theme] - theme_avgs1[theme]
        }
    comparison['themes'] = theme_changes
    
    # Compare metrics
    comparison['metrics'] = {
        'review_count': {
            'version1': len(version1),
            'version2': len(version2),
            'delta': len(version2) - len(version1)
        },
        'average_rating': {
            'version1': version1['rating'].mean(),
            'version2': version2['rating'].mean(),
            'delta': version2['rating'].mean() - version1['rating'].mean()
        }
    }
    
    return comparison

def get_version_timeline(df: pd.DataFrame) -> List[Dict]:
    """
    Create a timeline of version releases based on review dates.
    """
    # Extract versions and their first appearance dates
    version_dates = {}
    for _, row in df.iterrows():
        version = extract_version_from_review(row['text'])
        if version:
            if version not in version_dates or row['date'] < version_dates[version]:
                version_dates[version] = row['date']
    
    # Sort versions by date
    timeline = [
        {'version': version, 'date': date}
        for version, date in sorted(version_dates.items(), key=lambda x: x[1])
    ]
    
    return timeline 