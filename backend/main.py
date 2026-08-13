# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv(override=True)

from mood_parser import parse_mood
# pyrefly: ignore [missing-import]
from tmdb_service import get_movie_recommendations

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
    try:
        # Step 1: Parse mood using AI
        mood_data = parse_mood(request.mood)
        
        # Step 2 & 3: Get movie recommendations from TMDB based on parsed mood, region, and language
        recommendations = await get_movie_recommendations(mood_data, request.region, request.language)
        
        return {"movies": recommendations, "mood_analysis": mood_data}
    except Exception as e:
        return {"error": str(e)}
