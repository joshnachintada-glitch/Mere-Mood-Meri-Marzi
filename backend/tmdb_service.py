import os
import httpx
import asyncio

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN")
BASE_URL = "https://api.themoviedb.org/3"

async def get_movie_recommendations(mood_data: dict, region: str = "IN") -> list:
    if not TMDB_API_KEY and not TMDB_ACCESS_TOKEN:
        raise ValueError("TMDB API credentials are not set.")
    
    genre_ids = mood_data.get("primary_genre_ids", [])
    
    params = {
        "include_adult": "false",
        "include_video": "false",
        "language": "en-US",
        "page": 1,
        "sort_by": "popularity.desc",
        "vote_average.gte": 6.0,
        "vote_count.gte": 100
    }
    
    if genre_ids:
        params["with_genres"] = ",".join(map(str, genre_ids))
    
    if mood_data.get("original_language"):
        params["with_original_language"] = mood_data.get("original_language")
    
    headers = {}
    if TMDB_ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {TMDB_ACCESS_TOKEN}"
        headers["accept"] = "application/json"
    else:
        params["api_key"] = TMDB_API_KEY
    
    async with httpx.AsyncClient() as client:
        url = f"{BASE_URL}/discover/movie"
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])[:6] # Top 6 movies
        
        async def fetch_movie_provider(movie):
            movie_id = movie["id"]
            # Fetch providers
            providers_url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
            prov_params = {} if TMDB_ACCESS_TOKEN else {"api_key": TMDB_API_KEY}
            prov_resp = await client.get(providers_url, params=prov_params, headers=headers)
            prov_data = prov_resp.json()
            
            providers = []
            watch_link = ""
            if "results" in prov_data and region in prov_data["results"]:
                region_data = prov_data["results"][region]
                if "flatrate" in region_data:
                    providers = region_data["flatrate"]
                watch_link = region_data.get("link", "")
            
            return {
                "id": movie_id,
                "title": movie["title"],
                "release_year": (movie.get("release_date") or "")[:4],
                "rating": movie.get("vote_average", 0),
                "poster_path": movie.get("poster_path"),
                "overview": movie.get("overview"),
                "providers": providers,
                "watch_link": watch_link or f"https://www.themoviedb.org/movie/{movie_id}/watch",
                "ai_reason": mood_data.get("tone_summary", "This movie matches your desired mood perfectly!")
            }
            
        movies_enriched = await asyncio.gather(*(fetch_movie_provider(movie) for movie in results))
        return movies_enriched
