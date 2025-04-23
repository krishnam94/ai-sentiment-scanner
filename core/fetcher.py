import tweepy
from datetime import datetime, timedelta
from config.settings import TWITTER_BEARER_TOKEN, MAX_TWEETS_PER_REQUEST

# Initialize Twitter client
client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

def fetch_by_handle(handle, days=7, max_results=MAX_TWEETS_PER_REQUEST):
    """Fetch tweets from a specific Twitter handle."""
    try:
        # Get user ID from handle
        user = client.get_user(username=handle).data
        if not user:
            raise ValueError(f"User {handle} not found")
        
        # Calculate time range
        end = datetime.utcnow()
        start = end - timedelta(days=days)
        
        # Fetch tweets
        tweets = client.get_users_tweets(
            id=user.id,
            start_time=start.isoformat("T") + "Z",
            end_time=end.isoformat("T") + "Z",
            max_results=max_results,
            tweet_fields=["created_at", "public_metrics", "text"]
        )
        
        return [
            {
                "text": t.text,
                "created_at": t.created_at,
                "likes": t.public_metrics["like_count"],
                "retweets": t.public_metrics["retweet_count"],
                "source": handle
            } for t in tweets.data or []
        ]
    except Exception as e:
        print(f"Error fetching tweets for {handle}: {str(e)}")
        return []

def fetch_by_hashtag(query, max_results=MAX_TWEETS_PER_REQUEST):
    """Fetch tweets containing a specific hashtag or keyword."""
    try:
        # Add hashtag if not present
        if not query.startswith("#"):
            query = f"#{query}"
        
        # Fetch tweets
        tweets = client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=["created_at", "public_metrics", "text"]
        )
        
        return [
            {
                "text": t.text,
                "created_at": t.created_at,
                "likes": t.public_metrics["like_count"],
                "retweets": t.public_metrics["retweet_count"],
                "source": query
            } for t in tweets.data or []
        ]
    except Exception as e:
        print(f"Error fetching tweets for {query}: {str(e)}")
        return [] 