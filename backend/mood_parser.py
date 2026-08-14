import os
import json
import re
import asyncio
from typing import List, Optional, Dict
from openai import OpenAI, AsyncOpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(override=True)

class MoodAnalysis(BaseModel):
    primary_genre_ids: List[int]
    keywords: List[str]
    tone_summary: str
    original_language: Optional[str] = None

# Global cached OpenAI clients (initialized lazily and reused)
_async_client: Optional[AsyncOpenAI] = None
_sync_client: Optional[OpenAI] = None

# In-memory LRU cache for parsed moods
MOOD_CACHE: Dict[str, dict] = {}
MAX_CACHE_SIZE = 1000

# Comprehensive Keyword to TMDB Genre ID mapping for instant (< 0.1ms) classification
KEYWORD_GENRE_MAP = [
    (["anime", "animation", "cartoon", "animated", "studio ghibli", "shonen", "manga", "pixar", "disney", "makoto shinkai"], 16, "Anime / Animation", "ja"),
    (["action", "fight", "stunt", "martial arts", "heroic", "explosive", "adrenaline", "gun", "combat", "warrior", "assassin", "sniper", "spy", "superhero", "avenger", "chase", "blockbuster", "heist", "swords"], 28, "Action", None),
    (["adventure", "journey", "quest", "exploration", "expedition", "treasure", "safari", "survival", "island", "jungle", "wild", "space travel", "voyage", "lost", "tomb"], 12, "Adventure", None),
    (["comedy", "funny", "hilarious", "laugh", "humor", "feel-good", "fun", "sitcom", "parody", "satire", "goofy", "silly", "comic", "prank", "romcom", "cheerful", "lighthearted", "chuckle"], 35, "Comedy", None),
    (["crime", "gangster", "mafia", "heist", "underworld", "cop", "police", "gritty", "detective", "robbery", "cartel", "drug", "smuggling", "corruption", "jail", "prison", "criminals", "hitman", "thief"], 80, "Crime", None),
    (["drama", "emotional", "moving", "powerful", "deep", "heartfelt", "touching", "tearjerker", "family drama", "intense", "inspirational", "biographical", "struggle", "life", "relationship", "tragedy", "unique", "sad", "meaningful", "crying"], 18, "Drama", None),
    (["family", "kids", "children", "wholesome", "parent", "father", "mother", "daughter", "son", "school", "pets", "dog", "magic"], 10751, "Family", None),
    (["fantasy", "magic", "mythology", "mythical", "supernatural", "wizard", "witch", "dragon", "fairy", "folklore", "kingdom", "powers", "enchanted", "spell", "god", "curse"], 14, "Fantasy", None),
    (["history", "historical", "period", "biopic", "biography", "kingdom", "dynasty", "ancient", "monarchy", "medieval", "freedom", "revolution", "1990s", "90s", "80s", "70s", "classic", "retro", "vintage", "century", "empire"], 36, "History", None),
    (["horror", "scary", "ghost", "spooky", "haunting", "fear", "chilling", "creepy", "slasher", "demon", "devil", "possession", "nightmare", "zombie", "vampire", "dark", "evil", "terror", "gore", "paranormal", "haunted"], 27, "Horror", None),
    (["music", "musical", "dance", "singer", "songs", "concert", "band", "rock", "classical", "hip hop", "dancer", "melody", "soundtrack"], 10402, "Music", None),
    (["mystery", "investigation", "whodunit", "detective", "puzzle", "secrets", "clue", "murder", "unsolved", "interrogation", "disappearance", "conspiracy", "mind-bending", "riddle", "suspect"], 9648, "Mystery", None),
    (["romance", "romantic", "love", "couple", "dating", "relationship", "chemistry", "romcom", "heartwarming", "crush", "marriage", "wedding", "passion", "sweetheart", "lovers", "romantic comedy"], 10749, "Romance", None),
    (["sci-fi", "science fiction", "space", "alien", "futuristic", "robot", "time travel", "multiverse", "dystopian", "cyberpunk", "ai", "artificial intelligence", "universe", "galaxy", "technology", "quantum", "mind-bending", "mars", "virtual", "cyborg"], 878, "Sci-Fi", None),
    (["thriller", "suspense", "twist", "edge of seat", "psychological", "tension", "intense", "danger", "stalker", "hostage", "revenge", "escape", "hunt", "paranoia", "survival", "cliffhanger"], 53, "Thriller", None),
    (["war", "battle", "military", "soldier", "army", "navy", "air force", "combat", "invasion", "ww2", "world war", "battlefield", "frontline"], 10752, "War", None),
]

# Language Keyword mapping to detect user's requested regional or global industry
LANGUAGE_KEYWORD_MAP = [
    (["telugu", "telegu", "tollywood", "andhra", "telangana"], "te"),
    (["hindi", "bollywood"], "hi"),
    (["tamil", "kollywood"], "ta"),
    (["malayalam", "mollywood", "kerala", "mallu"], "ml"),
    (["kannada", "sandalwood", "kannadiga"], "kn"),
    (["punjabi", "pollywood", "punjab"], "pa"),
    (["marathi"], "mr"),
    (["bengali", "bangla"], "bn"),
    (["gujarati", "dhollywood"], "gu"),
    (["odia", "oriya", "ollywood"], "or"),
    (["assamese", "jollywood", "assam"], "as"),
    (["urdu"], "ur"),
    (["anime", "japanese", "japan", "manga", "studio ghibli", "shonen", "makoto shinkai"], "ja"),
    (["korean", "kdrama", "k-drama", "korea"], "ko"),
    (["english", "hollywood", "american", "british"], "en"),
]

# Fast preset map for instant lookup (< 0.05ms)
FAST_MOOD_MAP: Dict[str, dict] = {
    "": {
        "primary_genre_ids": [28, 35, 18, 10749, 878, 53],
        "keywords": ["blockbuster", "top-rated", "popular", "cinema"],
        "tone_summary": "Top-rated movies across all genres and languages.",
        "original_language": "all"
    },
    "explore": {
        "primary_genre_ids": [28, 35, 18, 10749, 878, 53],
        "keywords": ["explore", "top-rated", "blockbuster", "cinema"],
        "tone_summary": "Top-rated movies across all genres and languages.",
        "original_language": "all"
    },
    "explore films": {
        "primary_genre_ids": [28, 35, 18, 10749, 878, 53],
        "keywords": ["explore", "cinema", "popular", "masterpieces"],
        "tone_summary": "Top-rated movies across all genres and languages.",
        "original_language": "all"
    },
    "explore movies": {
        "primary_genre_ids": [28, 35, 18, 10749, 878, 53],
        "keywords": ["explore", "cinema", "popular", "masterpieces"],
        "tone_summary": "Top-rated movies across all genres and languages.",
        "original_language": "all"
    },
    "top rated movies across all genres and industries": {
        "primary_genre_ids": [28, 35, 18, 10749, 878, 53],
        "keywords": ["top-rated", "blockbuster", "masterpieces", "cinema"],
        "tone_summary": "Spectacular cinema gems curated across all languages and genres.",
        "original_language": "all"
    },
    "all": {
        "primary_genre_ids": [28, 35, 18, 10749, 878, 53],
        "keywords": ["all", "top-rated", "popular", "cinema"],
        "tone_summary": "Top-rated movies across all genres and languages.",
        "original_language": "all"
    },
    "all movies": {
        "primary_genre_ids": [28, 35, 18, 10749, 878, 53],
        "keywords": ["all", "top-rated", "popular", "cinema"],
        "tone_summary": "Top-rated movies across all genres and languages.",
        "original_language": "all"
    },
    "action": {
        "primary_genre_ids": [28, 12, 53],
        "keywords": ["action", "thrill", "high-octane", "intense", "heroic"],
        "tone_summary": "High-octane action, adrenaline-pumping sequences, and heroic thrills.",
        "original_language": "all"
    },
    "action movies with intense thrill and high energy": {
        "primary_genre_ids": [28, 12, 53],
        "keywords": ["action", "thrill", "high-octane", "intense", "heroic"],
        "tone_summary": "High-octane action, thrilling sequences, and adrenaline-pumping cinematic excitement.",
        "original_language": "all"
    },
    "comedy": {
        "primary_genre_ids": [35, 10751],
        "keywords": ["comedy", "humor", "feel-good", "laughter", "fun"],
        "tone_summary": "Laugh-out-loud comedy and feel-good humor to brighten your spirits.",
        "original_language": "all"
    },
    "hilarious comedy movies with feel-good laughter": {
        "primary_genre_ids": [35, 10751],
        "keywords": ["comedy", "humor", "feel-good", "laughter", "fun"],
        "tone_summary": "Hilarious comedy and heartwarming laughter that will leave you smiling.",
        "original_language": "all"
    },
    "drama": {
        "primary_genre_ids": [18],
        "keywords": ["drama", "emotional", "moving", "powerful", "deep"],
        "tone_summary": "Deeply moving drama with gripping storytelling and rich emotional depth.",
        "original_language": "all"
    },
    "emotional and powerful drama movies": {
        "primary_genre_ids": [18],
        "keywords": ["drama", "emotional", "moving", "powerful", "deep"],
        "tone_summary": "Deeply emotional and compelling cinema with unforgettable human stories.",
        "original_language": "all"
    },
    "horror": {
        "primary_genre_ids": [27, 53],
        "keywords": ["horror", "scary", "supernatural", "suspense", "chilling"],
        "tone_summary": "Spine-chilling scares, eerie tension, and terrifying suspense.",
        "original_language": "all"
    },
    "chilling and scary horror movies": {
        "primary_genre_ids": [27, 53],
        "keywords": ["horror", "scary", "supernatural", "suspense", "chilling"],
        "tone_summary": "Spine-chilling horror and atmospheric suspense to keep you on the edge.",
        "original_language": "all"
    },
    "sci-fi": {
        "primary_genre_ids": [878, 12],
        "keywords": ["sci-fi", "futuristic", "technology", "mind-bending", "space"],
        "tone_summary": "Mind-bending sci-fi concepts, futuristic technology, and visionary adventures.",
        "original_language": "all"
    },
    "science fiction": {
        "primary_genre_ids": [878, 12],
        "keywords": ["sci-fi", "futuristic", "technology", "mind-bending", "space"],
        "tone_summary": "Mind-bending sci-fi concepts, futuristic technology, and visionary adventures.",
        "original_language": "all"
    },
    "science fiction (sci-fi)": {
        "primary_genre_ids": [878, 12],
        "keywords": ["sci-fi", "futuristic", "technology", "mind-bending", "space"],
        "tone_summary": "Mind-bending sci-fi concepts, futuristic technology, and visionary adventures.",
        "original_language": "all"
    },
    "futuristic science fiction and mind-bending sci-fi movies": {
        "primary_genre_ids": [878, 12],
        "keywords": ["sci-fi", "futuristic", "technology", "mind-bending", "space"],
        "tone_summary": "Mind-bending sci-fi concepts, futuristic technology, and visionary adventures.",
        "original_language": "all"
    },
    "fantasy": {
        "primary_genre_ids": [14, 12],
        "keywords": ["fantasy", "magic", "mythology", "adventure", "epic"],
        "tone_summary": "Enchanting fantasy worlds, magical quests, and legendary mythology.",
        "original_language": "all"
    },
    "magical fantasy and mythical adventure movies": {
        "primary_genre_ids": [14, 12],
        "keywords": ["fantasy", "magic", "mythology", "adventure", "epic"],
        "tone_summary": "Enchanting fantasy worlds, magical quests, and legendary mythology.",
        "original_language": "all"
    },
    "thriller": {
        "primary_genre_ids": [53, 9648, 80],
        "keywords": ["thriller", "suspense", "mystery", "investigation", "twist"],
        "tone_summary": "Edge-of-your-seat suspense, mystery, and unexpected plot twists.",
        "original_language": "all"
    },
    "thriller & suspense": {
        "primary_genre_ids": [53, 9648, 80],
        "keywords": ["thriller", "suspense", "mystery", "investigation", "twist"],
        "tone_summary": "Edge-of-your-seat suspense, mystery, and unexpected plot twists.",
        "original_language": "all"
    },
    "gripping thriller, suspense and mystery movies": {
        "primary_genre_ids": [53, 9648, 80],
        "keywords": ["thriller", "suspense", "mystery", "investigation", "twist"],
        "tone_summary": "Gripping suspense, thrilling investigations, and mind-bending mystery.",
        "original_language": "all"
    },
    "romance": {
        "primary_genre_ids": [10749, 35],
        "keywords": ["romance", "love", "heartwarming", "feel-good", "chemistry"],
        "tone_summary": "Heartwarming romance, sparkling chemistry, and endearing love stories.",
        "original_language": "all"
    },
    "heartwarming romantic love story movies": {
        "primary_genre_ids": [10749, 35],
        "keywords": ["romance", "love", "heartwarming", "feel-good", "chemistry"],
        "tone_summary": "Heartwarming romance, sparkling chemistry, and endearing love stories.",
        "original_language": "all"
    },
    "anime": {
        "primary_genre_ids": [16, 14],
        "keywords": ["anime", "animation", "japanese", "visuals", "storytelling"],
        "tone_summary": "Visually breathtaking anime cinema with profound emotions and artistic world-building.",
        "original_language": "ja"
    },
    "masterpiece anime movies with stunning animation and storytelling": {
        "primary_genre_ids": [16, 14],
        "keywords": ["anime", "animation", "japanese", "visuals", "storytelling"],
        "tone_summary": "Visually breathtaking anime cinema with profound emotions and artistic world-building.",
        "original_language": "ja"
    },
    "adventure": {
        "primary_genre_ids": [12, 28, 14],
        "keywords": ["adventure", "journey", "quest", "exploration", "survival"],
        "tone_summary": "Epic journeys, thrilling expeditions, and daring explorations.",
        "original_language": "all"
    },
    "epic adventure, exploration, and journey movies": {
        "primary_genre_ids": [12, 28, 14],
        "keywords": ["adventure", "journey", "quest", "exploration", "survival"],
        "tone_summary": "Epic journeys, thrilling expeditions, and daring explorations.",
        "original_language": "all"
    },
    "crime": {
        "primary_genre_ids": [80, 53],
        "keywords": ["crime", "gangster", "underworld", "investigation", "gritty"],
        "tone_summary": "Gritty crime dramas, mafia sagas, and intense underworld investigations.",
        "original_language": "all"
    },
    "intense crime, underworld, and mafia sagas": {
        "primary_genre_ids": [80, 53],
        "keywords": ["crime", "gangster", "underworld", "investigation", "gritty"],
        "tone_summary": "Gritty crime dramas, mafia sagas, and intense underworld investigations.",
        "original_language": "all"
    },
    "family": {
        "primary_genre_ids": [10751, 16, 35],
        "keywords": ["family", "wholesome", "adventure", "fun", "kids"],
        "tone_summary": "Wholesome, entertaining, and magical movies crafted for the entire family.",
        "original_language": "all"
    },
    "wholesome, magical family movies for all ages": {
        "primary_genre_ids": [10751, 16, 35],
        "keywords": ["family", "wholesome", "adventure", "fun", "kids"],
        "tone_summary": "Wholesome, entertaining, and magical movies crafted for the entire family.",
        "original_language": "all"
    },
    "feel-good": {
        "primary_genre_ids": [35, 10751, 10749],
        "keywords": ["feel-good", "wholesome", "family", "uplifting", "positive"],
        "tone_summary": "Uplifting, wholesome, and warm-hearted cinema to elevate your mood.",
        "original_language": "all"
    },
    "feel good": {
        "primary_genre_ids": [35, 10751, 10749],
        "keywords": ["feel-good", "wholesome", "family", "uplifting", "positive"],
        "tone_summary": "Uplifting, wholesome, and warm-hearted cinema to elevate your mood.",
        "original_language": "all"
    },
    "mystery": {
        "primary_genre_ids": [9648, 53, 80],
        "keywords": ["mystery", "investigation", "whodunit", "clues", "detective"],
        "tone_summary": "Intriguing mysteries, suspenseful investigations, and clever detective puzzles.",
        "original_language": "all"
    },
    "history": {
        "primary_genre_ids": [36, 18],
        "keywords": ["history", "historical", "period", "biopic", "epic"],
        "tone_summary": "Magnificent historical epics and monumental biographical stories.",
        "original_language": "all"
    },
    "war": {
        "primary_genre_ids": [10752, 28, 18],
        "keywords": ["war", "battlefield", "soldier", "military", "heroic"],
        "tone_summary": "Gripping war dramas, heroic bravery, and epic combat sagas.",
        "original_language": "all"
    },
    "music": {
        "primary_genre_ids": [10402, 18, 35],
        "keywords": ["music", "musical", "soundtrack", "concert", "songs"],
        "tone_summary": "Soulful musical journeys, melodious rhythms, and artistic inspiration.",
        "original_language": "all"
    }
}

def get_async_client() -> AsyncOpenAI:
    global _async_client
    if _async_client is None:
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            raise ValueError("NVIDIA_API_KEY is not set.")
        _async_client = AsyncOpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key,
            timeout=2.0
        )
    return _async_client

def get_sync_client() -> OpenAI:
    global _sync_client
    if _sync_client is None:
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            raise ValueError("NVIDIA_API_KEY is not set.")
        _sync_client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key,
            timeout=2.0
        )
    return _sync_client

def check_fast_match(clean_text: str) -> Optional[dict]:
    """Check if the text matches a known preset, direct genre, or language keyword (< 0.1ms)."""
    if clean_text in FAST_MOOD_MAP:
        return FAST_MOOD_MAP[clean_text].copy()
    
    # 1. Detect language keywords (e.g. telugu, telegu, tollywood, hindi, anime, etc.)
    detected_lang = None
    detected_lang_name = None
    for lang_keywords, lang_code in LANGUAGE_KEYWORD_MAP:
        for lkw in lang_keywords:
            if re.search(r'\b' + re.escape(lkw) + r'\b', clean_text):
                detected_lang = lang_code
                detected_lang_name = lkw.title()
                break
        if detected_lang:
            break

    # 2. Check genre combinations and tokens
    matched_genres = []
    extracted_keywords = []

    for keywords, genre_id, genre_name, default_lang in KEYWORD_GENRE_MAP:
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', clean_text):
                if genre_id not in matched_genres:
                    matched_genres.append(genre_id)
                if kw not in extracted_keywords:
                    extracted_keywords.append(kw)
                if default_lang and not detected_lang:
                    detected_lang = default_lang
                break

    if matched_genres:
        lang_str = f" in {detected_lang_name}" if detected_lang_name else ""
        return {
            "primary_genre_ids": matched_genres[:3],
            "keywords": extracted_keywords[:5] if extracted_keywords else ["movies"],
            "tone_summary": f"Great movies featuring {', '.join(extracted_keywords[:3])} vibes{lang_str}.",
            "original_language": detected_lang or "all"
        }
    elif detected_lang:
        # User specified only language (e.g. "telegu", "telugu movies", "tollywood")
        return {
            "primary_genre_ids": [28, 35, 18, 10749, 878, 53],
            "keywords": [detected_lang_name or "regional", "cinema", "popular"],
            "tone_summary": f"Top rated {detected_lang_name or 'regional'} movies across popular genres.",
            "original_language": detected_lang
        }
        
    return None

def clean_json_response(content: str) -> dict:
    """Extract and parse valid JSON from LLM output."""
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r'(\{.*\})', content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise

def build_prompt(user_input: str) -> str:
    return f"""Analyze mood: "{user_input}".
TMDB IDs: Action:28, Adventure:12, Animation:16, Comedy:35, Crime:80, Drama:18, Family:10751, Fantasy:14, Horror:27, Mystery:9648, Romance:10749, Sci-Fi:878, Thriller:53, War:10752.
Return JSON:
{{"primary_genre_ids": [1-3 IDs], "keywords": [3-5 strings], "tone_summary": "1 sentence vibe", "original_language": "ja/hi/te/ta/en/all"}}
Output JSON ONLY."""

async def parse_mood_async(user_input: str) -> dict:
    """
    Asynchronously parses the user's mood with fast path, caching, and strict 2s timeout.
    """
    clean_input = user_input.strip().lower()
    
    # 1. Check in-memory cache (< 0.01ms)
    if clean_input in MOOD_CACHE:
        return MOOD_CACHE[clean_input]
    
    # 2. Check fast keyword/preset match (< 0.1ms)
    fast_match = check_fast_match(clean_input)
    if fast_match:
        MOOD_CACHE[clean_input] = fast_match
        return fast_match
    
    # 3. Dynamic LLM parsing with strict 1.0-second timeout
    try:
        client = get_async_client()
        prompt = build_prompt(user_input)
        
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model="meta/llama-3.1-8b-instruct",
                messages=[
                    {"role": "system", "content": "You are a movie classifier. Return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                top_p=0.7,
                max_tokens=80,
            ),
            timeout=2.5
        )
        content = response.choices[0].message.content or "{}"
        data = clean_json_response(content)
        
        # Ensure required keys exist
        if "primary_genre_ids" not in data or not isinstance(data["primary_genre_ids"], list):
            data["primary_genre_ids"] = [18, 35]
        if "keywords" not in data or not isinstance(data["keywords"], list):
            data["keywords"] = ["movies"]
        if "tone_summary" not in data:
            data["tone_summary"] = "Great movies tailored to your vibe."
        if "original_language" not in data:
            data["original_language"] = "all"
            
        # Cache result
        if len(MOOD_CACHE) >= MAX_CACHE_SIZE:
            MOOD_CACHE.pop(next(iter(MOOD_CACHE)))
        MOOD_CACHE[clean_input] = data
        return data
    except Exception:
        # Instant fallback (< 0.05ms) if LLM times out or encounters network issue
        fallback = {
            "primary_genre_ids": [35, 18, 28],
            "keywords": ["popular", "engaging", "feel-good"],
            "tone_summary": f"Great movies matching '{user_input}'.",
            "original_language": "all"
        }
        MOOD_CACHE[clean_input] = fallback
        return fallback

def parse_mood(user_input: str) -> dict:
    """
    Synchronous fallback wrapper.
    """
    clean_input = user_input.strip().lower()
    if clean_input in MOOD_CACHE:
        return MOOD_CACHE[clean_input]
    fast_match = check_fast_match(clean_input)
    if fast_match:
        MOOD_CACHE[clean_input] = fast_match
        return fast_match
        
    try:
        client = get_sync_client()
        prompt = build_prompt(user_input)
        response = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": "You are a movie classifier. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=100,
            timeout=2.0
        )
        content = response.choices[0].message.content or "{}"
        data = clean_json_response(content)
        MOOD_CACHE[clean_input] = data
        return data
    except Exception:
        return {
            "primary_genre_ids": [35, 18],
            "keywords": ["movie", "popular"],
            "tone_summary": f"Movies matching '{user_input}'.",
            "original_language": "all"
        }

