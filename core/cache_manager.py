"""
Cache management functions for the AI Sentiment Scanner app.
"""
import os
import logging

# Use the root logger
logger = logging.getLogger()

def clear_cache() -> None:
    """
    Clear all cached snapshot files.
    """
    try:
        snapshots_dir = "data/snapshots"
        if os.path.exists(snapshots_dir):
            for filename in os.listdir(snapshots_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(snapshots_dir, filename)
                    os.remove(file_path)
                    logger.info(f"Removed cache file: {filename}")
            logger.info("Cache cleared successfully")
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}", exc_info=True)
        raise 