import os
# pyrefly: ignore [missing-import]
import httpx
import asyncio

OMDB_API_KEY = os.getenv("OMDB_API_KEY")
BASE_URL = "http://www.omdbapi.com/"

async def fetch_movie_from_omdb(client, title: str):
    params = {
        "apikey": OMDB_API_KEY,
        "t": title
    }
    response = await client.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.json()

async def get_movie_recommendations(mood_data: dict, region: str = "IN") -> list:
    if not OMDB_API_KEY:
        raise ValueError("OMDB_API_KEY is not set.")
    
    titles = mood_data.get("movie_titles", [])
    
    movies_enriched = []
    
    async with httpx.AsyncClient() as client:
        # Fetch all movies concurrently
        tasks = [fetch_movie_from_omdb(client, title) for title in titles]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for data in results:
            if isinstance(data, Exception):
                continue
            if data.get("Response") == "False":
                continue # Movie not found
                
            try:
                rating = float(data.get("imdbRating", 0))
            except ValueError:
                rating = 0.0
                
            poster = data.get("Poster")
            if poster == "N/A":
                poster = None
                
            movies_enriched.append({
                "id": data.get("imdbID"),
                "title": data.get("Title"),
                "release_year": data.get("Year", "")[:4],
                "rating": rating,
                "poster_path": poster,
                "overview": data.get("Plot"),
                "providers": [], # OMDB doesn't provide this natively
                "ai_reason": mood_data.get("tone_summary", "This movie matches your desired mood perfectly!")
            })
            
    return movies_enriched
