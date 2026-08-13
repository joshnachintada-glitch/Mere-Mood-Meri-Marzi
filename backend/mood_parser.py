import os
import json
import time
from openai import OpenAI
from pydantic import BaseModel
from typing import List

class MoodAnalysis(BaseModel):
    primary_genre_ids: List[int]
    keywords: List[str]
    tone_summary: str
    original_language: str | None = None

def parse_mood(user_input: str) -> dict:
    """
    Uses Nvidia API to parse user's mood description into structured data for TMDB.
    """
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY is not set.")
    print(f"DEBUG: Loaded API KEY: '{api_key[:10]}...{api_key[-5:]}'")
    
    # Initialize the OpenAI client for Nvidia API
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )
    
    prompt = f"""
    You are an expert Indian & global cinema recommender with deep knowledge of Indian film industries:
    - Bollywood (Hindi - 'hi')
    - Tollywood (Telugu - 'te')
    - Kollywood (Tamil - 'ta')
    - Sandalwood (Kannada - 'kn')
    - Mollywood (Malayalam - 'ml')
    - Pollywood (Punjabi - 'pa')
    - Ollywood (Odia - 'or')
    - Marathi Cinema ('mr')
    - Bengali Cinema ('bn')
    - Gujarati Cinema ('gu')
    - Indian English / Global ('en')
    - Assamese ('as'), Urdu ('ur')
    - Anime & Japanese Animation ('ja')

    Analyze the user's mood, vibe, genre, or language preference (including Anime, Indian regional cinema, and global films) and determine the best TMDB movie genres and keywords to search for.

    User Mood/Input: "{user_input}"

    Return a JSON object matching this schema:
    {{
      "primary_genre_ids": [array of integers representing TMDB genre IDs, e.g. Animation is 16],
      "keywords": [array of string keywords to search for, e.g. "anime", "shonen", "feel-good", "mass", "emotional", "wholesome", "plot-twist"],
      "tone_summary": "A 1-2 sentence lively summary of the emotional vibe the user is looking for and what makes these films great for this mood.",
      "original_language": "ISO 639-1 code if specific language requested/implied (e.g., 'ja' for anime/Japanese, 'hi', 'te', 'ta', 'kn', 'ml', 'pa', 'or', 'mr', 'bn', 'gu', 'en', 'as', 'ur'), or 'all' if not specified or all Indian languages requested."
    }}

    Valid TMDB Genre IDs:
    - Action: 28
    - Adventure: 12
    - Animation: 16
    - Comedy: 35
    - Crime: 80
    - Documentary: 99
    - Drama: 18
    - Family: 10751
    - Fantasy: 14
    - History: 36
    - Horror: 27
    - Music: 10402
    - Mystery: 9648
    - Romance: 10749
    - Science Fiction: 878
    - Thriller: 53
    - War: 10752
    - Western: 37

    Choose 1 to 3 most relevant genre IDs. Provide 3-5 keywords.
    Output ONLY valid JSON without any markdown formatting.
    """
    
    max_retries = 3
    base_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="meta/llama-3.1-8b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                top_p=0.7,
                max_tokens=1024,
            )
            content = response.choices[0].message.content
            
            # Clean up potential markdown formatting (e.g., ```json ... ```)
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
                
            return json.loads(content.strip())
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Error occurred: {e}. Retrying in {base_delay} seconds...")
                time.sleep(base_delay)
                base_delay *= 2
            else:
                raise e
    raise Exception("Failed to get mood analysis from AI after multiple retries.")
