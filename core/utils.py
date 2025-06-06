from typing import List, Dict, Any, Callable
import pandas as pd
from datetime import datetime, timedelta
import re
import hashlib
import os
import json
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging

# Use the root logger
logger = logging.getLogger()

def merge_reviews(*review_lists: List[Dict]) -> List[Dict]:
    """Merge multiple lists of reviews into a single list."""
    from itertools import chain
    return list(chain(*review_lists))

def clean_review_text(text: str) -> str:
    """Clean review text by removing special characters and extra whitespace."""
    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()

def format_date(date_str: str) -> str:
    """Format date string to a consistent format."""
    try:
        date = pd.to_datetime(date_str)
        return date.strftime("%Y-%m-%d")
    except:
        return date_str

def cache_key(texts: List[str], app_name: str = None) -> str:
    """Generate a cache key for a list of texts with app name."""
    try:
        # Create a unique identifier using both app name and content
        identifier = f"{app_name}_{''.join(texts)}" if app_name else "".join(texts)
        cache_path = os.path.join("data/summaries", hashlib.md5(identifier.encode()).hexdigest() + ".json")
        
        # Ensure cache directory exists
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        return cache_path
    except Exception as e:
        logger.error(f"Error generating cache key: {str(e)}")
        return None

def cached_summary(texts: List[str], summarizer_func: Callable, app_name: str = None, **kwargs) -> str:
    """
    Get a cached summary or generate and cache a new one.
    
    Args:
        texts: List of texts to summarize
        summarizer_func: Function that generates the summary
        app_name: Name of the app (for cache key generation)
        **kwargs: Additional arguments to pass to the summarizer function
        
    Returns:
        str: The summary text
    """
    try:
        if not texts:
            logger.warning("No texts provided for summary")
            return "No reviews available for summary."
            
        logger.info(f"Starting summary generation for {len(texts)} texts from {app_name if app_name else 'unknown app'}")
        logger.debug(f"First text preview: {texts[0][:100]}...")
            
        # Generate cache key with app name and additional parameters
        cache_params = f"{app_name}_{json.dumps(kwargs, sort_keys=True)}" if app_name else json.dumps(kwargs, sort_keys=True)
        path = cache_key(texts, cache_params)
        if not path:
            logger.warning("Could not generate cache key, proceeding without cache")
            return summarizer_func(texts, **kwargs)
            
        logger.debug(f"Cache path: {path}")
            
        # Try to load from cache
        if os.path.exists(path):
            try:
                logger.info("Attempting to load from cache...")
                with open(path, 'r') as f:
                    cached = json.load(f)
                    if "summary" in cached:
                        logger.info("Loaded summary from cache")
                        return cached["summary"]
                    else:
                        logger.warning("Cache file exists but no summary found")
            except Exception as e:
                logger.error(f"Error reading cache file: {str(e)}")
                
        # Generate new summary
        logger.info("Generating new summary...")
        try:
            summary = summarizer_func(texts, **kwargs)
            if not summary:
                raise ValueError("Summarizer function returned empty result")
                
            # Cache the summary
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w') as f:
                    json.dump({"summary": summary}, f)
                logger.info("Summary cached successfully")
            except Exception as e:
                logger.error(f"Error caching summary: {str(e)}")
                
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise
    except Exception as e:
        logger.error(f"Error in cached_summary: {str(e)}")
        raise

def store_snapshot(app_name: str, reviews: List[Dict], requested_count: int) -> None:
    """
    Store a snapshot of reviews for an app.
    
    Args:
        app_name: Name of the app
        reviews: List of review dictionaries
        requested_count: Number of reviews that were requested
    """
    try:
        date = datetime.now().strftime("%Y-%m-%d")
        # Use the app_name directly as the safe_app since it's already a safe identifier
        safe_app = app_name
        path = f"data/snapshots/{safe_app}_{date}.json"
        
        # Ensure snapshots directory exists
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating snapshots directory: {str(e)}")
            raise
        
        # Check if we already have a snapshot
        if os.path.exists(path):
            with open(path, 'r') as f:
                existing_data = json.load(f)
                if "reviews" in existing_data:
                    existing_reviews = existing_data["reviews"]
                    # If we have more reviews than requested, keep the existing ones
                    if len(existing_reviews) >= len(reviews):
                        logger.info(f"Keeping existing snapshot with {len(existing_reviews)} reviews")
                        return
                    # If we have fewer reviews but more than requested, keep the existing ones
                    if len(existing_reviews) >= requested_count:
                        logger.info(f"Keeping existing snapshot with {len(existing_reviews)} reviews (meets requested count)")
                        return
        
        # Store the new snapshot
        try:
            with open(path, 'w') as f:
                json.dump({
                    "app_name": app_name,
                    "reviews": reviews,
                    "review_count": len(reviews),
                    "timestamp": datetime.now().isoformat(),
                    "requested_count": requested_count
                }, f, default=str)
            logger.info(f"Successfully stored snapshot for {app_name} with {len(reviews)} reviews")
        except Exception as e:
            logger.error(f"Error writing snapshot file: {str(e)}")
            raise
    except Exception as e:
        logger.error(f"Error storing snapshot for {app_name}: {str(e)}", exc_info=True)
        raise

def load_snapshot(app_name: str) -> List[Dict]:
    """
    Load a snapshot of reviews for an app.
    
    Args:
        app_name: Name or ID of the app
        
    Returns:
        List[Dict]: List of review dictionaries or None if no snapshot exists
    """
    try:
        date = datetime.now().strftime("%Y-%m-%d")
        # Use the app_name directly as the safe_app since it's already a safe identifier
        safe_app = app_name
        path = f"data/snapshots/{safe_app}_{date}.json"
        
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    if "reviews" in data:
                        cached_reviews = data["reviews"]
                        cached_count = len(cached_reviews)
                        logger.info(f"Loaded {cached_count} reviews for {app_name}")
                        return cached_reviews
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding snapshot JSON for {app_name}: {str(e)}")
                return None
            except Exception as e:
                logger.error(f"Error reading snapshot file for {app_name}: {str(e)}")
                return None
                
        logger.info(f"No snapshot found for {app_name}")
        return None
    except Exception as e:
        logger.error(f"Error loading snapshot for {app_name}: {str(e)}", exc_info=True)
        return None

def calculate_response_time(df: pd.DataFrame) -> pd.Series:
    """Calculate average response time for reviews with replies."""
    try:
        if 'reply_date' not in df.columns or 'date' not in df.columns:
            logger.warning("Missing date columns for response time calculation")
            return pd.Series()
        
        # Convert dates to datetime
        df['date'] = pd.to_datetime(df['date'])
        df['reply_date'] = pd.to_datetime(df['reply_date'])
        
        # Calculate response time in days
        response_times = (df['reply_date'] - df['date']).dt.days
        
        return response_times
    except Exception as e:
        logger.error(f"Error calculating response time: {str(e)}", exc_info=True)
        return pd.Series()

def get_top_keywords(texts: List[str], n: int = 10) -> List[str]:
    """Extract top keywords from review texts."""
    try:
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        # Get stopwords
        stop_words = set(stopwords.words('english'))
        
        # Tokenize and count words
        words = []
        for text in texts:
            words.extend(word_tokenize(text.lower()))
        
        # Filter out stopwords and non-alphabetic words
        words = [word for word in words if word.isalpha() and word not in stop_words]
        
        # Get most common words
        word_counts = Counter(words)
        return [word for word, _ in word_counts.most_common(n)]
    except Exception as e:
        logger.error(f"Error getting top keywords: {str(e)}", exc_info=True)
        return []

def clear_cache() -> None:
    """
    Clear all cached summary files.
    """
    try:
        if os.path.exists(CACHE_DIR):
            for filename in os.listdir(CACHE_DIR):
                if filename.endswith('.json'):
                    file_path = os.path.join(CACHE_DIR, filename)
                    os.remove(file_path)
                    logger.info(f"Removed cache file: {filename}")
            logger.info("Cache cleared successfully")
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}", exc_info=True)
        raise

def clear_snapshots(days_to_keep: int = 7) -> None:
    """
    Clear old snapshot files, keeping only those from the last N days.
    
    Args:
        days_to_keep: Number of days of snapshots to keep (default: 7)
    """
    try:
        if not os.path.exists(SNAPSHOT_DIR):
            return
            
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")
        
        for filename in os.listdir(SNAPSHOT_DIR):
            if not filename.endswith('.json'):
                continue
                
            # Extract date from filename (format: appname_YYYY-MM-DD.json)
            try:
                date_str = filename.split('_')[-1].replace('.json', '')
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date < cutoff_date:
                    file_path = os.path.join(SNAPSHOT_DIR, filename)
                    os.remove(file_path)
                    logger.info(f"Removed old snapshot: {filename}")
            except (ValueError, IndexError) as e:
                logger.warning(f"Could not parse date from filename {filename}: {str(e)}")
                continue
                
        logger.info(f"Successfully cleaned up snapshots older than {days_to_keep} days")
    except Exception as e:
        logger.error(f"Error clearing old snapshots: {str(e)}", exc_info=True)
        raise

def get_snapshot_info() -> Dict[str, Any]:
    """
    Get information about stored snapshots.
    
    Returns:
        Dict containing snapshot statistics
    """
    try:
        if not os.path.exists(SNAPSHOT_DIR):
            return {
                "total_snapshots": 0,
                "total_size": 0,
                "apps": {}
            }
            
        total_size = 0
        apps = {}
        
        for filename in os.listdir(SNAPSHOT_DIR):
            if not filename.endswith('.json'):
                continue
                
            file_path = os.path.join(SNAPSHOT_DIR, filename)
            file_size = os.path.getsize(file_path)
            total_size += file_size
            
            # Extract app name and date
            try:
                app_name = '_'.join(filename.split('_')[:-1])
                date_str = filename.split('_')[-1].replace('.json', '')
                
                if app_name not in apps:
                    apps[app_name] = {
                        "snapshots": 0,
                        "total_size": 0,
                        "latest_date": None
                    }
                    
                apps[app_name]["snapshots"] += 1
                apps[app_name]["total_size"] += file_size
                
                # Update latest date if this snapshot is newer
                snapshot_date = datetime.strptime(date_str, "%Y-%m-%d")
                if (apps[app_name]["latest_date"] is None or 
                    snapshot_date > apps[app_name]["latest_date"]):
                    apps[app_name]["latest_date"] = snapshot_date
                    
            except (ValueError, IndexError) as e:
                logger.warning(f"Could not parse filename {filename}: {str(e)}")
                continue
                
        return {
            "total_snapshots": len([f for f in os.listdir(SNAPSHOT_DIR) if f.endswith('.json')]),
            "total_size": total_size,
            "apps": apps
        }
    except Exception as e:
        logger.error(f"Error getting snapshot info: {str(e)}", exc_info=True)
        return {
            "total_snapshots": 0,
            "total_size": 0,
            "apps": {},
            "error": str(e)
        } 