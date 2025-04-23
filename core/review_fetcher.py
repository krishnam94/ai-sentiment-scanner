import os
import ssl
from typing import List, Dict
from google_play_scraper import app, reviews, Sort
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix SSL certificate verification for macOS
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def fetch_reviews(app_id: str, count: int = 200) -> List[Dict]:
    """
    Fetch reviews for a specific app from Google Play Store.
    
    Args:
        app_id: The app's package ID
        count: Number of reviews to fetch
        
    Returns:
        List[Dict]: List of review dictionaries
    """
    try:
        logger.info(f"Fetching reviews for app: {app_id}")
        
        # First, verify the app exists
        try:
            app_info = app(app_id)
            logger.info(f"Found app: {app_info['title']}")
        except Exception as e:
            logger.error(f"Error fetching app info for {app_id}: {str(e)}")
            return []

        # Fetch reviews
        result, continuation_token = reviews(
            app_id,
            lang='en',  # Language
            country='sg',  # Country
            count=count,  # Number of reviews
            sort=Sort.NEWEST,  # Sort by newest
            filter_score_with=None  # Get all scores
        )
        
        if not result:
            logger.warning(f"No reviews found for app: {app_id}")
            return []
            
        logger.info(f"Fetched {len(result)} reviews for {app_id}")
        
        # Process reviews into a consistent format
        processed_reviews = []
        for review in result:
            try:
                processed_review = {
                    'review': review.get('content', ''),
                    'score': review.get('score', 0),
                    'thumbsUpCount': review.get('thumbsUpCount', 0),
                    'at': review.get('at', ''),
                    'replyContent': review.get('replyContent', ''),
                    'repliedAt': review.get('repliedAt', '')
                }
                processed_reviews.append(processed_review)
            except Exception as e:
                logger.error(f"Error processing review: {str(e)}")
                continue
        
        if not processed_reviews:
            logger.warning(f"No valid reviews processed for app: {app_id}")
            return []
            
        logger.info(f"Successfully processed {len(processed_reviews)} reviews for {app_id}")
        return processed_reviews
    
    except Exception as e:
        logger.error(f"Error fetching reviews for {app_id}: {str(e)}")
        return []

def fetch_multiple_apps(app_ids: List[str], count: int = 200) -> Dict[str, List[Dict]]:
    """
    Fetch reviews for multiple apps.
    
    Args:
        app_ids: List of app package IDs
        count: Number of reviews to fetch per app
        
    Returns:
        Dict[str, List[Dict]]: Dictionary mapping app IDs to their reviews
    """
    all_reviews = {}
    for app_id in app_ids:
        reviews = fetch_reviews(app_id, count)
        if reviews:  # Only add if we got reviews
            all_reviews[app_id] = reviews
    return all_reviews 