import openai
from .settings import OPENAI_API_KEY
from typing import List
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

def summarize_themes(texts: List[str], prompt: str = None, max_tokens: int = 1000) -> str:
    """
    Generate a summary of themes from a list of texts using OpenAI's GPT-4.
    
    Args:
        texts (list): List of text strings to summarize
        prompt (str, optional): Custom prompt to use for summarization
        max_tokens (int): Maximum number of tokens to generate
        
    Returns:
        str: Generated summary
    """
    try:
        # Log the number of texts being processed
        logger.info(f"Processing {len(texts)} texts for summarization")
        
        # Join all texts with newlines
        combined_text = "\n\n".join(texts)
        
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
        response = openai.ChatCompletion.create(
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
            
        comparison = response['choices'][0]['message']['content']
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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a competitive intelligence analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error generating competitive analysis: {str(e)}")
        return "Error generating competitive analysis. Please try again." 