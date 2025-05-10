import openai
from .settings import OPENAI_API_KEY
from typing import List, Dict
import logging
import json

# Use the root logger
logger = logging.getLogger()

# Initialize OpenAI client
try:
    client = openai.OpenAI(
        api_key=OPENAI_API_KEY,
        timeout=30.0,  # Add timeout
        max_retries=3  # Add retries
    )
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    raise

def summarize_themes(texts: List[str], prompt: str = None, max_tokens: int = 2000) -> str:
    """
    Generate a summary of themes from review texts using GPT-4.
    
    Args:
        texts: List of review texts
        prompt: Optional custom prompt
        max_tokens: Maximum tokens for the response (increased from 1000 to 2000)
        
    Returns:
        str: Generated summary
    """
    try:
        # Log the number of texts being processed
        logger.info(f"Processing {len(texts)} texts for summarization")
        
        # Truncate long reviews and limit total text length
        MAX_REVIEW_LENGTH = 1000  # Increased from 500 to 1000 characters per review
        MAX_TOTAL_LENGTH = 20000  # Increased from 10000 to 20000 characters total
        
        processed_texts = []
        total_length = 0
        
        for text in texts:
            # Truncate long reviews
            if len(text) > MAX_REVIEW_LENGTH:
                text = text[:MAX_REVIEW_LENGTH] + "..."
            
            # Check if adding this review would exceed the total limit
            if total_length + len(text) + 2 > MAX_TOTAL_LENGTH:  # +2 for newlines
                break
                
            processed_texts.append(text)
            total_length += len(text) + 2  # +2 for newlines
        
        # Join all texts with newlines
        combined_text = "\n\n".join(processed_texts)
        
        # Use custom prompt if provided, otherwise use default
        if prompt is None:
            prompt = """Analyze the following app reviews and provide a comprehensive summary focusing on:
            1. Overall sentiment and user satisfaction
            2. Key features and functionality mentioned
            3. Common issues and pain points
            4. User suggestions and feature requests
            5. Notable trends or patterns in the feedback
            
            Format the response in clear sections with bullet points for easy reading."""
        
        # Create the full prompt
        full_prompt = f"{prompt}\n\nReviews:\n{combined_text}"
        
        # Make the API call
        logger.info("Making API call to OpenAI for summarization")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert app review analyst."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        # Extract and return the generated summary
        summary = response.choices[0].message.content
        logger.info("Successfully generated summary")
        return summary
        
    except Exception as e:
        logger.error(f"Error in summarize_themes: {str(e)}", exc_info=True)
        raise

def compare_apps(texts1: List[str], texts2: List[str], app_names: List[str], max_tokens: int = 1000) -> str:
    """
    Generate a comparative analysis of two apps' reviews using GPT-4.
    
    Args:
        texts1 (List[str]): Reviews for first app
        texts2 (List[str]): Reviews for second app
        app_names (List[str]): Names of the apps being compared
        max_tokens (int): Maximum tokens for the response
        
    Returns:
        str: Generated comparison
    """
    try:
        if not texts1 or not texts2:
            logger.warning("Missing review data for comparison")
            return "Insufficient review data for comparison."
            
        # Log the number of texts for each app
        logger.info(f"Number of texts for {app_names[0]}: {len(texts1)}")
        logger.info(f"Number of texts for {app_names[1]}: {len(texts2)}")
            
        # Join reviews with newlines
        joined1 = "\n".join(texts1)
        joined2 = "\n".join(texts2)
        logger.debug(f"Total text length for {app_names[0]}: {len(joined1)} characters")
        logger.debug(f"Total text length for {app_names[1]}: {len(joined2)} characters")
        
        # Create the prompt
        prompt = f"""Compare the reviews of {app_names[0]} and {app_names[1]} apps.
Focus on:
1. Overall satisfaction levels
2. Common issues and complaints
3. Unique strengths of each app
4. Feature comparison
5. Customer service quality
6. Areas for improvement

{app_names[0]} Reviews:
{joined1}

{app_names[1]} Reviews:
{joined2}

Please provide a structured comparison with these sections."""
        
        logger.info("Sending comparison request to OpenAI API")
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        # Get completion from OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a competitive analysis expert specializing in app reviews."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        logger.debug(f"OpenAI API response: {json.dumps(response, indent=2)}")
        
        if not response or 'choices' not in response or not response['choices']:
            logger.error("Invalid response from OpenAI API")
            return "Error: Invalid response from OpenAI API"
            
        comparison = response['choices'][0].message.content
        logger.info(f"Successfully generated comparison of length: {len(comparison)}")
        return comparison
        
    except openai.error.AuthenticationError:
        logger.error("OpenAI API authentication failed. Please check your API key.")
        return "Error: Invalid API key. Please check your configuration."
    except openai.error.RateLimitError:
        logger.error("OpenAI API rate limit exceeded")
        return "Error: API rate limit exceeded. Please try again later."
    except openai.error.APIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return f"Error: API error occurred. Please try again later. Details: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in compare_apps: {str(e)}", exc_info=True)
        return f"Error: An unexpected error occurred. Please try again later. Details: {str(e)}"

def analyze_competitors(tweets: List[str], competitors: List[str], max_tokens: int = 1000) -> str:
    """Analyze competitive positioning from tweets using GPT-4."""
    try:
        # Join tweets with newlines
        joined = "\n".join(tweets)
        
        # Create the prompt
        prompt = f"""Analyze the following tweets to understand competitive positioning for {', '.join(competitors)}.
Focus on:
1. Market positioning and differentiation
2. Product/service offerings
3. Customer engagement strategies
4. Competitive advantages
5. Areas of potential improvement

Tweets:
{joined}

Please provide a structured competitive analysis."""
        
        # Get completion from OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a competitive intelligence analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return response['choices'][0].message.content
    except Exception as e:
        print(f"Error generating competitive analysis: {str(e)}")
        return "Error generating competitive analysis. Please try again."

def analyze_period_changes(
    period1_data: Dict,
    period2_data: Dict,
    period1_name: str = "First Period",
    period2_name: str = "Second Period",
    max_tokens: int = 2500  # Increased from 1500 to 2500
) -> str:
    """
    Generate a comparison analysis between two periods using GPT-4.
    
    Args:
        period1_data: Data for first period
        period2_data: Data for second period
        period1_name: Name of first period
        period2_name: Name of second period
        max_tokens: Maximum tokens for the response
        
    Returns:
        str: Generated comparison analysis
    """
    try:
        # Format the data for the prompt
        metrics_changes = []
        for metric, values in period1_data['metrics'].items():
            if metric in period2_data['metrics']:
                delta = period2_data['metrics'][metric] - values
                metrics_changes.append(f"{metric}: {values:.2f} → {period2_data['metrics'][metric]:.2f} (Δ: {delta:+.2f})")

        # Format topic changes
        topic_changes = []
        for topic, data in period1_data['topics'].items():
            if topic in period2_data['topics']:
                delta = period2_data['topics'][topic] - data
                if abs(delta) > 0.05:  # Only include significant changes
                    topic_changes.append(f"{topic}: {data:.1%} → {period2_data['topics'][topic]:.1%} (Δ: {delta:+.1%})")

        # Format theme changes
        theme_changes = []
        for theme, data in period1_data['themes'].items():
            if theme in period2_data['themes']:
                delta = period2_data['themes'][theme] - data
                if abs(delta) > 0.1:  # Only include significant changes
                    theme_changes.append(f"{theme}: {data:.2f} → {period2_data['themes'][theme]:.2f} (Δ: {delta:+.2f})")

        # Create the prompt
        prompt = f"""Analyze the changes between {period1_name} and {period2_name} for this app's reviews.

Key Metrics Changes:
{chr(10).join(metrics_changes)}

Significant Topic Changes:
{chr(10).join(topic_changes)}

Theme Changes:
{chr(10).join(theme_changes)}

Please provide a comprehensive analysis that:
1. Highlights the most significant changes and their implications
2. Identifies emerging trends or issues
3. Suggests potential areas for improvement
4. Explains the impact of these changes on user satisfaction
5. Provides actionable insights for the development team

Format the response in clear sections with bullet points for easy reading."""

        # Get completion from OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert app analytics specialist who excels at identifying meaningful patterns and changes in user feedback."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )

        analysis = response.choices[0].message.content
        logger.info("Successfully generated period comparison analysis")
        return analysis

    except Exception as e:
        logger.error(f"Error in analyze_period_changes: {str(e)}", exc_info=True)
        return f"Error generating period comparison analysis: {str(e)}" 