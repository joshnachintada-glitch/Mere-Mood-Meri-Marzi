import os
import httpx
import asyncio

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN")
BASE_URL = "https://api.themoviedb.org/3"

LANGUAGE_MAP = {
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "en": "English",
    "ur": "Urdu",
    "as": "Assamese",
}

GENRE_MAP = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Sci-Fi",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western",
}

ALL_INDIAN_LANGUAGES = "hi|te|ta|kn|ml|pa|or|mr|bn|gu|en|ur|as"

async def get_movie_recommendations(mood_data: dict, region: str = "IN", explicit_language: str | None = None) -> list:
    if not TMDB_API_KEY and not TMDB_ACCESS_TOKEN:
        raise ValueError("TMDB API credentials are not set.")
    
    genre_ids = mood_data.get("primary_genre_ids", [])
    
    params = {
        "include_adult": "false",
        "include_video": "false",
        "language": "en-US",
        "page": 1,
        "sort_by": "popularity.desc",
        "vote_average.gte": 5.5,
        "vote_count.gte": 20
    }
    
    if genre_ids:
        params["with_genres"] = ",".join(map(str, genre_ids))
    
    # Determine language filter
    target_lang = explicit_language or mood_data.get("original_language")
    if target_lang and target_lang.lower() != "all":
        params["with_original_language"] = target_lang
    else:
        # Default to all Indian languages + English
        params["with_original_language"] = ALL_INDIAN_LANGUAGES
    
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
        results = data.get("results", [])[:12] # Top 12 movies
        
        # If no results with strict genre/vote count, try a broader fallback
        if not results and genre_ids:
            fallback_params = params.copy()
            fallback_params.pop("vote_count.gte", None)
            fallback_params["with_genres"] = str(genre_ids[0])
            fallback_resp = await client.get(url, params=fallback_params, headers=headers)
            if fallback_resp.status_code == 200:
                results = fallback_resp.json().get("results", [])[:12]
        
        async def fetch_movie_provider(movie):
            movie_id = movie["id"]
            lang_code = movie.get("original_language", "en")
            lang_name = LANGUAGE_MAP.get(lang_code, lang_code.upper())
            movie_genre_names = [GENRE_MAP.get(gid) for gid in movie.get("genre_ids", []) if gid in GENRE_MAP]
            
            # Fetch streaming providers
            providers_url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
            prov_params = {} if TMDB_ACCESS_TOKEN else {"api_key": TMDB_API_KEY}
            try:
                prov_resp = await client.get(providers_url, params=prov_params, headers=headers)
                prov_data = prov_resp.json() if prov_resp.status_code == 200 else {}
            except Exception:
                prov_data = {}
            
            providers = []
            watch_link = ""
            if "results" in prov_data and region in prov_data["results"]:
                region_data = prov_data["results"][region]
                if "flatrate" in region_data:
                    providers = region_data["flatrate"]
                elif "rent" in region_data:
                    providers = region_data["rent"]
                elif "buy" in region_data:
                    providers = region_data["buy"]
                watch_link = region_data.get("link", "")
            
            return {
                "id": movie_id,
                "title": movie.get("title") or movie.get("original_title"),
                "original_title": movie.get("original_title"),
                "release_year": (movie.get("release_date") or "")[:4],
                "rating": movie.get("vote_average", 0),
                "poster_path": movie.get("poster_path"),
                "overview": movie.get("overview") or "No overview available.",
                "language_code": lang_code,
                "language_name": lang_name,
                "genres": movie_genre_names[:3],
                "providers": providers,
                "watch_link": watch_link or f"https://www.themoviedb.org/movie/{movie_id}/watch",
                "ai_reason": mood_data.get("tone_summary", "This movie matches your desired mood perfectly!")
            }
            
        movies_enriched = await asyncio.gather(*(fetch_movie_provider(movie) for movie in results))
        return movies_enriched
