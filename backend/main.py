import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(override=True)

from mood_parser import parse_mood_async
from tmdb_service import get_movie_recommendations, get_static_fallback_movies

app = FastAPI(title="Mere Mood Meri Marzi API")

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend URL
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendRequest(BaseModel):
    mood: str
    region: str = "IN"
    language: str | None = None

@app.get("/")
def read_root():
    return {"message": "Welcome to Mere Mood Meri Marzi API"}

@app.post("/api/recommend")
async def recommend_movies(request: RecommendRequest):
    fallback_mood = {
        "primary_genre_ids": [28, 35, 18, 10749, 878, 53],
        "keywords": ["popular", "trending", "blockbuster"],
        "tone_summary": f"Top movies matching '{request.mood or 'your mood'}'.",
        "original_language": request.language or "all"
    }

    mood_data = fallback_mood
    try:
        async def process_recommendation():
            # Step 1: Parse mood using AI asynchronously (< 0.05ms for keywords/presets)
            m_data = await parse_mood_async(request.mood or "Explore")
            
            # Determine effective language: explicit dropdown language overrides, otherwise use detected prompt language
            effective_lang = None
            if request.language and request.language.lower() != "all":
                effective_lang = request.language
            elif m_data.get("original_language") and m_data.get("original_language").lower() != "all":
                effective_lang = m_data.get("original_language")
            
            # Step 2 & 3: Get 24 movie recommendations from TMDB
            recommendations = await get_movie_recommendations(m_data, request.region, effective_lang)
            
            return {"movies": recommendations, "mood_analysis": m_data, "effective_language": effective_lang}

        # Enforce maximum 12.0 seconds runtime so comprehensive multi-language queries complete
        result = await asyncio.wait_for(process_recommendation(), timeout=12.0)
        mood_data = result.get("mood_analysis", fallback_mood)
        effective_lang = result.get("effective_language")
        
        # Absolute guarantee: ensure exactly 24 movies in response
        movies = result.get("movies", [])
        if len(movies) < 24:
            existing_ids = {m.get("id") for m in movies}
            for fm in get_static_fallback_movies(effective_lang, mood_data.get("primary_genre_ids")):
                if fm["id"] not in existing_ids:
                    existing_ids.add(fm["id"])
                    movies.append(fm)
                if len(movies) == 24:
                    break
            result["movies"] = movies[:24]
            
        return result
    except asyncio.TimeoutError:
        effective_lang = request.language if (request.language and request.language.lower() != "all") else None
        try:
            recommendations = await get_movie_recommendations(fallback_mood, request.region, effective_lang)
        except Exception:
            recommendations = get_static_fallback_movies(effective_lang, fallback_mood.get("primary_genre_ids"))
            
        if len(recommendations) < 24:
            existing_ids = {m.get("id") for m in recommendations}
            for fm in get_static_fallback_movies(effective_lang, fallback_mood.get("primary_genre_ids")):
                if fm["id"] not in existing_ids:
                    existing_ids.add(fm["id"])
                    recommendations.append(fm)
                if len(recommendations) == 24:
                    break
                    
        return {"movies": recommendations[:24], "mood_analysis": fallback_mood}
    except Exception:
        effective_lang = request.language if (request.language and request.language.lower() != "all") else None
        static_movies = get_static_fallback_movies(effective_lang, fallback_mood.get("primary_genre_ids"))
        return {"movies": static_movies[:24], "mood_analysis": fallback_mood}

