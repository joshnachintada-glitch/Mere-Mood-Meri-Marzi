import os
import httpx
import asyncio
import random
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv(override=True)

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
    "ja": "Japanese / Anime",
    "ko": "Korean / K-Drama",
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

# Major language clusters for Pan-India & Global multi-language discovery (Total target: 24+)
MULTI_LANGUAGE_CLUSTERS = [
    {"lang": "hi", "name": "Hindi", "weight": 3},
    {"lang": "te", "name": "Telugu", "weight": 3},
    {"lang": "ta", "name": "Tamil", "weight": 3},
    {"lang": "ml", "name": "Malayalam", "weight": 3},
    {"lang": "kn", "name": "Kannada", "weight": 2},
    {"lang": "mr|bn|pa|gu|or|as|ur", "name": "Regional Cinema", "weight": 2},
    {"lang": "ja", "name": "Anime", "weight": 3},
    {"lang": "ko", "name": "Korean & K-Drama", "weight": 3},
    {"lang": "en", "name": "English", "weight": 2},
]

ALL_MAJOR_GENRES = [28, 35, 18, 27, 878, 10749, 53, 16, 80, 14, 9648, 12, 10751, 36, 10752]

# Complementary genres map for rich genre diversity
COMPLEMENTARY_GENRES = {
    28: [53, 12, 80, 878],       # Action -> Thriller, Adventure, Crime, Sci-Fi
    35: [10749, 10751, 18, 16],  # Comedy -> Romance, Family, Drama, Animation
    18: [10749, 80, 53, 36],     # Drama -> Romance, Crime, Thriller, History
    27: [53, 9648, 14, 28],      # Horror -> Thriller, Mystery, Fantasy, Action
    878: [12, 28, 53, 16],       # Sci-Fi -> Adventure, Action, Thriller, Animation
    10749: [35, 18, 10402],      # Romance -> Comedy, Drama, Music
    53: [80, 9648, 28, 27],      # Thriller -> Crime, Mystery, Action, Horror
    16: [14, 12, 35, 878],       # Anime/Animation -> Fantasy, Adventure, Comedy, Sci-Fi
    80: [53, 18, 28, 9648],      # Crime -> Thriller, Drama, Action, Mystery
    14: [12, 28, 878, 16],       # Fantasy -> Adventure, Action, Sci-Fi, Animation
    12: [28, 14, 878, 10751],    # Adventure -> Action, Fantasy, Sci-Fi, Family
    9648: [53, 80, 18],          # Mystery -> Thriller, Crime, Drama
    10751: [35, 16, 12, 14],     # Family -> Comedy, Animation, Adventure, Fantasy
    36: [18, 10752, 28],         # History -> Drama, War, Action
    10752: [36, 18, 28, 53],     # War -> History, Drama, Action, Thriller
}

MAX_RECOMMENDED_MOVIES = 24

# In-memory cache for TMDB movie watch providers
PROVIDER_CACHE: Dict[int, dict] = {}
MAX_PROVIDER_CACHE = 2000

_httpx_client: Optional[httpx.AsyncClient] = None

def get_httpx_client() -> httpx.AsyncClient:
    global _httpx_client
    if _httpx_client is None or _httpx_client.is_closed:
        _httpx_client = httpx.AsyncClient(
            timeout=httpx.Timeout(6.0, connect=2.0),
            limits=httpx.Limits(max_keepalive_connections=100, max_connections=200)
        )
    return _httpx_client

# Comprehensive multi-language and multi-genre static fallback catalog (50+ masterpieces)
STATIC_FALLBACK_MOVIES: List[dict] = [
    # --- TELUGU ---
    {"id": 579974, "title": "RRR", "original_title": "RRR", "release_year": "2022", "rating": 8.0, "poster_path": "/wE0I6efAW4cDDmZQWtwZMOW44EJ.jpg", "overview": "A fictional history of two legendary revolutionaries and their journey away from home before they began fighting for their country in the 1920s.", "language_code": "te", "language_name": "Telugu", "genres": ["Action", "Drama", "War"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com/title/81476453", "ai_reason": "Epic Indian masterpiece with electrifying thrills and emotion."},
    {"id": 341013, "title": "Baahubali: The Beginning", "original_title": "Baahubali: The Beginning", "release_year": "2015", "rating": 7.6, "poster_path": "/9ptcfQJ1oU0z2yE6e5hQp0L2n8H.jpg", "overview": "In the kingdom of Mahishmati, a young man learns about his royal heritage and the kingdom's epic battle for the throne.", "language_code": "te", "language_name": "Telugu", "genres": ["Action", "Adventure", "Fantasy"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Magnificent Indian fantasy war epic that reshaped Indian cinema."},
    {"id": 350312, "title": "Baahubali 2: The Conclusion", "original_title": "Baahubali 2: The Conclusion", "release_year": "2017", "rating": 7.8, "poster_path": "/tA1qV3x7bM1pP3k8p5pY6q8w3kL.jpg", "overview": "Amarendra Baahubali must protect the rightful heir to the throne from a conniving brother.", "language_code": "te", "language_name": "Telugu", "genres": ["Action", "Drama", "Fantasy"], "providers": [{"provider_id": 122, "provider_name": "Disney+ Hotstar", "logo_path": "/7Fl8ylPD73btB8g3p5nQZz4c7vY.jpg"}], "watch_link": "https://www.hotstar.com", "ai_reason": "Triumphant, emotional resolution to the greatest Indian cinematic saga."},
    {"id": 624860, "title": "Pushpa: The Rise", "original_title": "Pushpa: The Rise", "release_year": "2021", "rating": 7.6, "poster_path": "/v1V8Gf9v89fHjL6w1Q6y6q8w3kL.jpg", "overview": "Pushpa Raj, a coolie, rises in the world of red sandalwood smuggling, making enemies along the way.", "language_code": "te", "language_name": "Telugu", "genres": ["Action", "Crime", "Thriller"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "High-octane mass action thriller with iconic swag."},
    {"id": 554230, "title": "Jersey", "original_title": "Jersey", "release_year": "2019", "rating": 8.3, "poster_path": "/k9Y7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "A failed cricketer decides to revive his cricketing career in his late thirties to fulfill his son's wish.", "language_code": "te", "language_name": "Telugu", "genres": ["Drama", "Family"], "providers": [{"provider_id": 122, "provider_name": "Disney+ Hotstar", "logo_path": "/7Fl8ylPD73btB8g3p5nQZz4c7vY.jpg"}], "watch_link": "https://www.hotstar.com", "ai_reason": "Deeply inspirational and emotional Telugu sports drama."},
    {"id": 851644, "title": "Sita Ramam", "original_title": "Sita Ramam", "release_year": "2022", "rating": 8.4, "poster_path": "/1kP4Y9qM9k7Y1q9m7k7Y1q9m7k7.jpg", "overview": "An orphan soldier's life changes after he gets a letter from a girl named Sita.", "language_code": "te", "language_name": "Telugu", "genres": ["Romance", "Drama", "Mystery"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Poetic and timeless Telugu romantic masterpiece."},
    {"id": 801335, "title": "Jathi Ratnalu", "original_title": "Jathi Ratnalu", "release_year": "2021", "rating": 7.4, "poster_path": "/8bQ7y1n6pP0lM9k2w4yP6q8w3kL.jpg", "overview": "Three happy-go-lucky men arrive in the city and get entangled in a crazy criminal conspiracy.", "language_code": "te", "language_name": "Telugu", "genres": ["Comedy"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Non-stop hilarious comedy of errors with lovable characters."},
    {"id": 980489, "title": "Masooda", "original_title": "Masooda", "release_year": "2022", "rating": 7.4, "poster_path": "/6N97u42qG1cE6n4X4Bq2N8g9s.jpg", "overview": "A timid software engineer helps his neighbor single mother rescue her possessed young daughter.", "language_code": "te", "language_name": "Telugu", "genres": ["Horror", "Mystery", "Thriller"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Authentic, atmospheric Telugu supernatural horror thriller."},
    {"id": 1051891, "title": "Kalki 2898 AD", "original_title": "Kalki 2898 AD", "release_year": "2024", "rating": 7.4, "poster_path": "/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg", "overview": "A modern avatar of Vishnu descends on Earth to protect the world from evil forces in a dystopian future.", "language_code": "te", "language_name": "Telugu", "genres": ["Sci-Fi", "Action", "Fantasy"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Groundbreaking Indian mythological Sci-Fi spectacle."},

    # --- HINDI ---
    {"id": 26022, "title": "3 Idiots", "original_title": "3 Idiots", "release_year": "2009", "rating": 8.0, "poster_path": "/66A9MqXOyVFCssoloscw79z8swE.jpg", "overview": "Two friends embark on a quest for a lost buddy while revisiting their college days and recalling the memories of their friend who inspired them to think differently.", "language_code": "hi", "language_name": "Hindi", "genres": ["Comedy", "Drama"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Timeless feel-good comedy and inspiring life lessons."},
    {"id": 850165, "title": "Jawan", "original_title": "Jawan", "release_year": "2023", "rating": 7.3, "poster_path": "/jYWmVxRjZt75sBvU7Q29J2yVq8D.jpg", "overview": "A high-octane action thriller which outlines the emotional journey of a man who is set to rectify the wrongs in the society.", "language_code": "hi", "language_name": "Hindi", "genres": ["Action", "Thriller"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "High energy action thriller with memorable mass cinematic moments."},
    {"id": 20453, "title": "Taare Zameen Par", "original_title": "Taare Zameen Par", "release_year": "2007", "rating": 8.0, "poster_path": "/8bQ7y1n6pP0lM9k2w4yP6q8w3kL.jpg", "overview": "An eight-year-old boy is thought to be a lazy trouble-maker, until the new art teacher discovers his real issue.", "language_code": "hi", "language_name": "Hindi", "genres": ["Drama", "Family"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Deeply moving family masterpiece that warms the soul."},
    {"id": 19404, "title": "Dilwale Dulhania Le Jayenge", "original_title": "Dilwale Dulhania Le Jayenge", "release_year": "1995", "rating": 8.5, "poster_path": "/lfR2v835SpHjuNWL5H2b9k8q7W7.jpg", "overview": "Raj and Simran meet on a trip across Europe and fall in love, but Simran is promised to another.", "language_code": "hi", "language_name": "Hindi", "genres": ["Romance", "Drama", "Comedy"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "The quintessential Indian romantic love story."},
    {"id": 361743, "title": "Tumbbad", "original_title": "Tumbbad", "release_year": "2018", "rating": 8.2, "poster_path": "/6N97u42qG1cE6n4X4Bq2N8g9s.jpg", "overview": "A mythological story about a goddess who created the entire universe and a demon of greed.", "language_code": "hi", "language_name": "Hindi", "genres": ["Horror", "Fantasy", "Drama"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Atmospheric, visually stunning horror fantasy masterpiece."},
    {"id": 534780, "title": "Andhadhun", "original_title": "Andhadhun", "release_year": "2018", "rating": 8.2, "poster_path": "/7Lq84Yj5QoM1dY3rP8tZ3mN7bQ8.jpg", "overview": "A series of mysterious events changes the life of a blind pianist who must now report a crime he never witnessed.", "language_code": "hi", "language_name": "Hindi", "genres": ["Mystery", "Thriller", "Comedy"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Masterclass dark comedy and suspenseful murder mystery."},
    {"id": 533444, "title": "Stree", "original_title": "Stree", "release_year": "2018", "rating": 7.6, "poster_path": "/m1Y7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "In the small town of Chanderi, men live in fear of an evil spirit named Stree who abducts men in the night.", "language_code": "hi", "language_name": "Hindi", "genres": ["Horror", "Comedy"], "providers": [{"provider_id": 122, "provider_name": "Disney+ Hotstar", "logo_path": "/7Fl8ylPD73btB8g3p5nQZz4c7vY.jpg"}], "watch_link": "https://www.hotstar.com", "ai_reason": "Hilarious and spooky horror comedy with unforgettable punchlines."},

    # --- TAMIL ---
    {"id": 974036, "title": "Jailer", "original_title": "Jailer", "release_year": "2023", "rating": 7.2, "poster_path": "/7Lq84Yj5QoM1dY3rP8tZ3mN7bQ8.jpg", "overview": "A retired jailer goes on a manhunt to find his son's killers. But the road leads him to a familiar, darker world.", "language_code": "ta", "language_name": "Tamil", "genres": ["Action", "Crime", "Thriller"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Stylish swagger and unstoppable heroic screen presence."},
    {"id": 842675, "title": "Vikram", "original_title": "Vikram", "release_year": "2022", "rating": 8.1, "poster_path": "/n2Y7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "A special agent investigates a murder committed by a masked group of serial killers.", "language_code": "ta", "language_name": "Tamil", "genres": ["Action", "Thriller", "Crime"], "providers": [{"provider_id": 122, "provider_name": "Disney+ Hotstar", "logo_path": "/7Fl8ylPD73btB8g3p5nQZz4c7vY.jpg"}], "watch_link": "https://www.hotstar.com", "ai_reason": "Adrenaline-fueled cinematic universe action thriller with Kamal Haasan."},
    {"id": 551804, "title": "Ratsasan", "original_title": "Ratsasan", "release_year": "2018", "rating": 8.3, "poster_path": "/j4K7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "An aspiring film director turned sub-inspector tracks down a psychotic serial killer targeting schoolgirls.", "language_code": "ta", "language_name": "Tamil", "genres": ["Mystery", "Thriller", "Crime"], "providers": [{"provider_id": 122, "provider_name": "Disney+ Hotstar", "logo_path": "/7Fl8ylPD73btB8g3p5nQZz4c7vY.jpg"}], "watch_link": "https://www.hotstar.com", "ai_reason": "Edge-of-the-seat psychological mystery crime thriller."},
    {"id": 546416, "title": "96", "original_title": "96", "release_year": "2018", "rating": 8.5, "poster_path": "/k9Y7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "Two high school sweethearts meet at a reunion after 22 years and reminisce about their past.", "language_code": "ta", "language_name": "Tamil", "genres": ["Romance", "Drama"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Soulful, nostalgic Tamil romantic classic."},

    # --- MALAYALAM ---
    {"id": 490132, "title": "Manjummel Boys", "original_title": "Manjummel Boys", "release_year": "2024", "rating": 8.1, "poster_path": "/bW3mB3b1g7HkFfLgZ2nB9mK1jQ8.jpg", "overview": "A group of friends from a small town embark on a vacation to Kodaikanal, where an unexpected mishap tests their bond.", "language_code": "ml", "language_name": "Malayalam", "genres": ["Adventure", "Drama", "Thriller"], "providers": [{"provider_id": 122, "provider_name": "Disney+ Hotstar", "logo_path": "/7Fl8ylPD73btB8g3p5nQZz4c7vY.jpg"}], "watch_link": "https://www.hotstar.com", "ai_reason": "Gripping survival drama celebrating the power of true friendship."},
    {"id": 986056, "title": "Premalu", "original_title": "Premalu", "release_year": "2024", "rating": 7.9, "poster_path": "/p1K7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "Sachin's quest for love takes unexpected turns, leading to a hilarious romantic triangle in Hyderabad.", "language_code": "ml", "language_name": "Malayalam", "genres": ["Comedy", "Romance"], "providers": [{"provider_id": 122, "provider_name": "Disney+ Hotstar", "logo_path": "/7Fl8ylPD73btB8g3p5nQZz4c7vY.jpg"}], "watch_link": "https://www.hotstar.com", "ai_reason": "Delightful romantic comedy packed with laughs and lovable vibes."},
    {"id": 1184918, "title": "Aavesham", "original_title": "Aavesham", "release_year": "2024", "rating": 8.0, "poster_path": "/q3K7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "Three college students in Bangalore seek the help of a local eccentric gangster named Ranga to get back at their bullies.", "language_code": "ml", "language_name": "Malayalam", "genres": ["Action", "Comedy"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Wildly energetic mass entertainer with an iconic Fahadh Faasil performance."},
    {"id": 269149, "title": "Drishyam", "original_title": "Drishyam", "release_year": "2013", "rating": 8.3, "poster_path": "/j4K7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "A man goes to extreme lengths to save his family from punishment after the family commits an accidental crime.", "language_code": "ml", "language_name": "Malayalam", "genres": ["Thriller", "Crime", "Mystery", "Drama"], "providers": [{"provider_id": 122, "provider_name": "Disney+ Hotstar", "logo_path": "/7Fl8ylPD73btB8g3p5nQZz4c7vY.jpg"}], "watch_link": "https://www.hotstar.com", "ai_reason": "Masterclass thriller with legendary suspense and storytelling."},
    {"id": 1198422, "title": "Bramayugam", "original_title": "Bramayugam", "release_year": "2024", "rating": 7.9, "poster_path": "/6N97u42qG1cE6n4X4Bq2N8g9s.jpg", "overview": "A folk singer in 17th century Kerala stumbles into a mysterious, crumbling mansion ruled by an enigmatic sorcerer.", "language_code": "ml", "language_name": "Malayalam", "genres": ["Horror", "Mystery", "Thriller"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Monochrome folk horror marvel with Mammootty in a career-defining role."},

    # --- KANNADA ---
    {"id": 843241, "title": "Kantara", "original_title": "Kantara", "release_year": "2022", "rating": 7.8, "poster_path": "/p7u44p8c0ZJ53x1f5U2s31D79.jpg", "overview": "When greed paves the way for betrayal, scheming and murder, a young tribal man reluctantly embraces the tradition of his ancestors to seek justice.", "language_code": "kn", "language_name": "Kannada", "genres": ["Action", "Drama", "Fantasy"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Folkloric visual spectacle with breathtaking divine climax."},
    {"id": 940551, "title": "Sapta Sagaradaache Ello - Side A", "original_title": "Sapta Sagaradaache Ello - Side A", "release_year": "2023", "rating": 8.1, "poster_path": "/8lK7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "Manu and Priya are deeply in love, but their dream of building a life together faces an insurmountable trial.", "language_code": "kn", "language_name": "Kannada", "genres": ["Romance", "Drama"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Poetic and deeply touching romance with soul-stirring music."},
    {"id": 585268, "title": "K.G.F: Chapter 1", "original_title": "K.G.F: Chapter 1", "release_year": "2018", "rating": 8.2, "poster_path": "/7Lq84Yj5QoM1dY3rP8tZ3mN7bQ8.jpg", "overview": "In the 1970s, a fierce rebel rises against brutal oppression in the Kolar Gold Fields.", "language_code": "kn", "language_name": "Kannada", "genres": ["Action", "Crime", "Drama"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Massive elevation, gritty style, and ground-breaking action."},

    # --- ANIME / JAPANESE ---
    {"id": 372058, "title": "Your Name.", "original_title": "君の名は。", "release_year": "2016", "rating": 8.5, "poster_path": "/q719qXXEzOoYaps6qFsR65qW3iS.jpg", "overview": "Two high schoolers spark a connection after discovering they are magically swapping bodies.", "language_code": "ja", "language_name": "Japanese / Anime", "genres": ["Animation", "Romance", "Drama", "Fantasy"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Gorgeous anime masterpiece full of heart, mystery, and soul."},
    {"id": 129, "title": "Spirited Away", "original_title": "千と千尋の神隠し", "release_year": "2001", "rating": 8.5, "poster_path": "/393t37SN0Bidfrki2q7V6uESJ7C.jpg", "overview": "A young girl enters a world ruled by gods, witches, and spirits, where humans are changed into beasts.", "language_code": "ja", "language_name": "Japanese / Anime", "genres": ["Animation", "Family", "Fantasy", "Adventure"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Studio Ghibli's Oscar-winning fantasy marvel."},
    {"id": 635302, "title": "Demon Slayer: Mugen Train", "original_title": "劇場版「鬼滅の刃」無限列車編", "release_year": "2020", "rating": 8.3, "poster_path": "/h8Rb9gBr48ODigDrng1Pz2Stafq.jpg", "overview": "Tanjiro and the Flame Hashira Kyojuro Rengoku board the Infinity Train to battle a powerful demon.", "language_code": "ja", "language_name": "Japanese / Anime", "genres": ["Animation", "Action", "Fantasy"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Unrivaled animation action with breathtaking emotional resonance."},
    {"id": 568332, "title": "Weathering with You", "original_title": "天気の子", "release_year": "2019", "rating": 8.0, "poster_path": "/qgrk7r1fUmgoi0LqV77r5rV5K3f.jpg", "overview": "A high-school runaway finds friendship with an orphan girl who has the uncanny ability to stop the rain and clear the sky.", "language_code": "ja", "language_name": "Japanese / Anime", "genres": ["Animation", "Romance", "Fantasy"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Visually arresting romantic fantasy anime on weather and love."},

    # --- ENGLISH / GLOBAL ---
    {"id": 157336, "title": "Interstellar", "original_title": "Interstellar", "release_year": "2014", "rating": 8.4, "poster_path": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg", "overview": "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel.", "language_code": "en", "language_name": "English", "genres": ["Sci-Fi", "Drama", "Adventure"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Mind-expanding cinematic exploration of love and spacetime."},
    {"id": 872585, "title": "Oppenheimer", "original_title": "Oppenheimer", "release_year": "2023", "rating": 8.1, "poster_path": "/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg", "overview": "The story of J. Robert Oppenheimer's role in the development of the atomic bomb during World War II.", "language_code": "en", "language_name": "English", "genres": ["Drama", "History", "War"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Oscar-winning cinematic tour de force with gripping intensity."},
    {"id": 693134, "title": "Dune: Part Two", "original_title": "Dune: Part Two", "release_year": "2024", "rating": 8.2, "poster_path": "/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg", "overview": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.", "language_code": "en", "language_name": "English", "genres": ["Sci-Fi", "Adventure", "Action"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Epic visionary science fiction on a monumental scale."},
    {"id": 569094, "title": "Spider-Man: Across the Spider-Verse", "original_title": "Spider-Man: Across the Spider-Verse", "release_year": "2023", "rating": 8.4, "poster_path": "/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg", "overview": "Miles Morales catapults across the Multiverse, where he encounters a team of Spider-People charged with protecting its very existence.", "language_code": "en", "language_name": "English", "genres": ["Animation", "Action", "Adventure", "Sci-Fi"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Revolutionary visual animation and multiverse adventure."},
    {"id": 49026, "title": "The Dark Knight Rises", "original_title": "The Dark Knight Rises", "release_year": "2012", "rating": 7.8, "poster_path": "/hrJ0cqR2t6bZ75rR2t4w3qT4yYp.jpg", "overview": "Batman returns to save Gotham from the ruthless terrorist Bane.", "language_code": "en", "language_name": "English", "genres": ["Action", "Crime", "Drama", "Thriller"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Grand superhero climax with towering stakes and heroic scale."},
    {"id": 138843, "title": "The Conjuring", "original_title": "The Conjuring", "release_year": "2013", "rating": 7.5, "poster_path": "/wE0I6efAW4cDDmZQWtwZMOW44EJ.jpg", "overview": "Paranormal investigators Ed and Lorraine Warren work to help a family terrorized by a dark presence in their farmhouse.", "language_code": "en", "language_name": "English", "genres": ["Horror", "Mystery", "Thriller"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Iconic modern supernatural horror masterpiece."},

    # --- KOREAN & K-DRAMAS ---
    {"id": 496243, "title": "Parasite", "original_title": "기생충", "release_year": "2019", "rating": 8.5, "poster_path": "/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg", "overview": "All unemployed, Ki-taek's family takes peculiar interest in the wealthy and glamorous Parks for their livelihood.", "language_code": "ko", "language_name": "Korean / K-Drama", "genres": ["Comedy", "Thriller", "Drama"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Historic Oscar Best Picture winner, brilliant dark comedy thriller."},
    {"id": 396535, "title": "Train to Busan", "original_title": "부산행", "release_year": "2016", "rating": 7.8, "poster_path": "/vNVFt6dtcqnScNZZv51nL33aWk0.jpg", "overview": "A zombie virus breaks out in South Korea, and passengers struggle to survive on the bullet train from Seoul to Busan.", "language_code": "ko", "language_name": "Korean / K-Drama", "genres": ["Action", "Horror", "Thriller"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Pulse-pounding emotional zombie survival thriller."},
    {"id": 666277, "title": "Past Lives", "original_title": "Past Lives", "release_year": "2023", "rating": 7.9, "poster_path": "/k3waqVXSnvCZWfJYNtdamTgTtTA.jpg", "overview": "Nora and Hae Sung, two deeply connected childhood friends, are wrested apart after Nora's family emigrates from South Korea.", "language_code": "ko", "language_name": "Korean / K-Drama", "genres": ["Romance", "Drama"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Soulful, poignant modern romance capturing inyeon and destiny."},
    {"id": 290098, "title": "The Handmaiden", "original_title": "아가씨", "release_year": "2016", "rating": 8.3, "poster_path": "/8MnFfT9LqM7k7Y1q9m7k7Y1q9m7.jpg", "overview": "A woman is hired as a handmaiden to a Japanese heiress, but secretly she is involved in a plot to defraud her.", "language_code": "ko", "language_name": "Korean / K-Drama", "genres": ["Thriller", "Drama", "Romance", "Mystery"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Visually stunning erotic psychological thriller with jaw-dropping twists."},
    {"id": 705996, "title": "Decision to Leave", "original_title": "헤어질 결심", "release_year": "2022", "rating": 7.3, "poster_path": "/6n741c9fV67Y1q9m7k7Y1q9m7k.jpg", "overview": "A polite detective investigates a man's death in the mountains, but finds himself falling for the dead man's mysterious wife.", "language_code": "ko", "language_name": "Korean / K-Drama", "genres": ["Mystery", "Romance", "Crime", "Thriller"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Cannes Best Director winner, a masterclass romantic mystery."}
]

def get_static_fallback_movies(preferred_lang: Optional[str] = None, preferred_genres: Optional[List[int]] = None) -> List[dict]:
    """Returns exactly 24 guaranteed top movies strictly prioritizing requested genres and language."""
    pool = list(STATIC_FALLBACK_MOVIES)
    
    preferred_genre_names = []
    if preferred_genres:
        preferred_genre_names = [GENRE_MAP[g] for g in preferred_genres if g in GENRE_MAP]

    def sort_score(m: dict) -> float:
        score = 0.0
        movie_genres = m.get("genres", [])
        
        # 1. Highest Priority: Match requested genres (+100 per matching genre)
        if preferred_genre_names:
            matched_g_count = sum(1 for g in movie_genres if g in preferred_genre_names)
            score += matched_g_count * 100.0
            
        # 2. Match requested language (+30)
        if preferred_lang and preferred_lang != "all":
            if m.get("language_code") == preferred_lang:
                score += 30.0
                
        # 3. Add rating as tiebreaker
        score += float(m.get("rating") or 0.0)
        return score

    sorted_pool = sorted(pool, key=sort_score, reverse=True)
    
    seen_ids = set()
    result = []
    for m in sorted_pool:
        if m["id"] not in seen_ids:
            seen_ids.add(m["id"])
            result.append(m)
        if len(result) == MAX_RECOMMENDED_MOVIES:
            break
            
    if len(result) < MAX_RECOMMENDED_MOVIES:
        for m in pool:
            if m["id"] not in seen_ids:
                seen_ids.add(m["id"])
                result.append(m)
            if len(result) == MAX_RECOMMENDED_MOVIES:
                break
                
    return result[:MAX_RECOMMENDED_MOVIES]

def format_fallback_movie(movie: dict, mood_tone: str, target_genre_ids: Optional[set] = None) -> dict:
    movie_id = movie["id"]
    lang_code = movie.get("original_language") or movie.get("language_code", "en")
    lang_name = movie.get("language_name") or LANGUAGE_MAP.get(lang_code, lang_code.upper())
    
    # Standardize genre names
    movie_genre_names = []
    if "genres" in movie and isinstance(movie["genres"], list):
        for g in movie["genres"]:
            if isinstance(g, str) and g in GENRE_MAP.values():
                movie_genre_names.append(g)
            elif isinstance(g, str):
                movie_genre_names.append(g)
            elif isinstance(g, dict) and "name" in g:
                movie_genre_names.append(g["name"])
    if not movie_genre_names and "genre_ids" in movie:
        movie_genre_names = [GENRE_MAP.get(gid) for gid in movie.get("genre_ids", []) if gid in GENRE_MAP]
    if not movie_genre_names:
        movie_genre_names = ["Drama", "Feature"]

    if target_genre_ids:
        target_names = [GENRE_MAP[gid] for gid in target_genre_ids if gid in GENRE_MAP]
        matching = [g for g in movie_genre_names if g in target_names]
        non_matching = [g for g in movie_genre_names if g not in target_names]
        movie_genre_names = matching + non_matching

    return {
        "id": movie_id,
        "title": movie.get("title") or movie.get("original_title"),
        "original_title": movie.get("original_title"),
        "release_year": (movie.get("release_date") or movie.get("release_year") or "")[:4],
        "rating": float(movie.get("vote_average") or movie.get("rating") or 0.0),
        "poster_path": movie.get("poster_path"),
        "overview": movie.get("overview") or "No overview available.",
        "language_code": lang_code,
        "language_name": lang_name,
        "genres": movie_genre_names[:3],
        "providers": movie.get("providers", []),
        "watch_link": movie.get("watch_link") or f"https://www.themoviedb.org/movie/{movie_id}/watch",
        "ai_reason": movie.get("ai_reason") or mood_tone or "This movie matches your desired mood perfectly!",
        "is_direct_search_match": bool(movie.get("is_direct_search_match"))
    }

async def fetch_movie_provider(client: httpx.AsyncClient, movie: dict, region: str, headers: dict, mood_tone: str, target_genre_ids: Optional[set] = None) -> dict:
    movie_id = movie["id"]
    lang_code = movie.get("original_language") or movie.get("language_code", "en")
    lang_name = movie.get("language_name") or LANGUAGE_MAP.get(lang_code, lang_code.upper())
    
    movie_genre_names = []
    if "genres" in movie and isinstance(movie["genres"], list):
        for g in movie["genres"]:
            if isinstance(g, str):
                movie_genre_names.append(g)
            elif isinstance(g, dict) and "name" in g:
                movie_genre_names.append(g["name"])
    if not movie_genre_names and "genre_ids" in movie:
        movie_genre_names = [GENRE_MAP.get(gid) for gid in movie.get("genre_ids", []) if gid in GENRE_MAP]
    if not movie_genre_names:
        movie_genre_names = ["Drama", "Feature"]

    if target_genre_ids:
        target_names = [GENRE_MAP[gid] for gid in target_genre_ids if gid in GENRE_MAP]
        matching = [g for g in movie_genre_names if g in target_names]
        non_matching = [g for g in movie_genre_names if g not in target_names]
        movie_genre_names = matching + non_matching
    
    # Check cache for provider (< 0.01ms)
    providers = []
    watch_link = ""
    
    if movie_id in PROVIDER_CACHE:
        cached_prov = PROVIDER_CACHE[movie_id]
        providers = cached_prov.get("providers", [])
        watch_link = cached_prov.get("watch_link", "")
    else:
        providers_url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
        prov_params = {} if TMDB_ACCESS_TOKEN else {"api_key": TMDB_API_KEY}
        try:
            prov_resp = await asyncio.wait_for(
                client.get(providers_url, params=prov_params, headers=headers),
                timeout=2.5
            )
            if prov_resp.status_code == 200:
                prov_data = prov_resp.json()
                results_dict = prov_data.get("results", {})
                
                # Check user region (e.g. IN), fallback to US / Global
                region_data = results_dict.get(region) or results_dict.get("IN") or results_dict.get("US")
                if not region_data and results_dict:
                    region_data = next(iter(results_dict.values()))
                    
                if region_data:
                    seen_provider_ids = set()
                    # Aggregate across all OTT channels: Subscription (flatrate), Free, Ad-supported, Rent & Buy
                    for channel in ["flatrate", "free", "ads", "rent", "buy"]:
                        for p in region_data.get(channel, []):
                            pid = p.get("provider_id")
                            if pid and pid not in seen_provider_ids:
                                seen_provider_ids.add(pid)
                                providers.append(p)
                    watch_link = region_data.get("link", "")
            
            if len(PROVIDER_CACHE) < MAX_PROVIDER_CACHE:
                PROVIDER_CACHE[movie_id] = {"providers": providers, "watch_link": watch_link}
        except Exception:
            providers = []
            watch_link = ""
    
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
        "ai_reason": movie.get("ai_reason") or mood_tone or "This movie matches your desired mood perfectly!",
        "is_direct_search_match": bool(movie.get("is_direct_search_match"))
    }

async def fetch_cluster_movies(client: httpx.AsyncClient, url: str, base_params: dict, headers: dict, lang_code: str, genre_filter: Optional[str], target_count: int, target_genre_ids: Optional[set] = None) -> list:
    """Fetch movies for a specific language and genre cluster with verification."""
    random_page = random.randint(1, 3)
    params = {
        **base_params,
        "with_original_language": lang_code,
        "page": random_page
    }
    if genre_filter:
        params["with_genres"] = genre_filter
        
    try:
        resp = await client.get(url, params=params, headers=headers)
        if resp.status_code == 200:
            movies = resp.json().get("results", [])
            if target_genre_ids:
                movies = [m for m in movies if bool(set(m.get("genre_ids", [])) & target_genre_ids)]
            random.shuffle(movies)
            if len(movies) >= target_count:
                return movies[:target_count]
            elif movies:
                return movies
        if random_page > 1:
            params["page"] = 1
            fallback_resp = await client.get(url, params=params, headers=headers)
            if fallback_resp.status_code == 200:
                movies = fallback_resp.json().get("results", [])
                if target_genre_ids:
                    movies = [m for m in movies if bool(set(m.get("genre_ids", [])) & target_genre_ids)]
                random.shuffle(movies)
                return movies[:target_count]
    except Exception:
        pass
    return []

async def get_movie_recommendations(mood_data: dict, region: str = "IN", explicit_language: str | None = None, query_text: str | None = None) -> list:
    if not TMDB_API_KEY and not TMDB_ACCESS_TOKEN:
        raise ValueError("TMDB API credentials are not set.")
    
    genre_ids = mood_data.get("primary_genre_ids", [])
    is_general_explore = not genre_ids or len(genre_ids) >= 6
    target_genre_ids = set(genre_ids) if (genre_ids and not is_general_explore) else set()
    
    # Format TMDB with_genres filter string: pipe '|' matches ANY of the target genres
    genre_filter_str = "|".join(str(g) for g in genre_ids) if target_genre_ids else None

    base_params = {
        "include_adult": "false",
        "include_video": "false",
        "language": "en-US",
        "sort_by": "popularity.desc",
        "vote_average.gte": 4.0,
        "vote_count.gte": 5
    }
    
    headers = {}
    if TMDB_ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {TMDB_ACCESS_TOKEN}"
        headers["accept"] = "application/json"
    else:
        base_params["api_key"] = TMDB_API_KEY
    
    client = get_httpx_client()
    url = f"{BASE_URL}/discover/movie"
    
    target_lang = explicit_language or mood_data.get("original_language")
    
    results = []
    seen_ids = set()

    # 🔎 STEP 1: Direct TMDB Search if user entered a specific movie title, franchise, or keyword
    search_query = (query_text or "").strip()
    is_preset_or_generic = (
        not search_query 
        or search_query.lower() in [
            "explore", "explore films", "explore movies", "all", "all movies", 
            "top rated movies across all genres and industries"
        ]
    )

    if not is_preset_or_generic:
        try:
            search_url = f"{BASE_URL}/search/movie"
            search_params = {
                "include_adult": "false",
                "language": "en-US",
                "query": search_query,
                "page": 1
            }
            if not TMDB_ACCESS_TOKEN:
                search_params["api_key"] = TMDB_API_KEY

            search_task1 = client.get(search_url, params=search_params, headers=headers)
            search_task2 = client.get(search_url, params={**search_params, "page": 2}, headers=headers)
            search_resps = await asyncio.gather(search_task1, search_task2, return_exceptions=True)

            raw_searched = []
            for s_resp in search_resps:
                if hasattr(s_resp, "status_code") and s_resp.status_code == 200:
                    for m in s_resp.json().get("results", []):
                        if m.get("id") and m.get("title") and m.get("poster_path"):
                            raw_searched.append(m)

            if raw_searched:
                q_lower = search_query.lower()
                
                # Rank search matches: exact title match > starts with > popularity/votes
                def search_rank(m):
                    title = (m.get("title") or "").lower()
                    orig_title = (m.get("original_title") or "").lower()
                    exact_match = 1000 if (q_lower == title or q_lower == orig_title) else 0
                    starts_with = 300 if (title.startswith(q_lower) or orig_title.startswith(q_lower)) else 0
                    contains_match = 100 if (q_lower in title or q_lower in orig_title) else 0
                    lang_boost = 150 if (target_lang and target_lang != "all" and m.get("original_language") == target_lang) else 0
                    pop = float(m.get("popularity") or 0.0)
                    votes = float(m.get("vote_count") or 0.0)
                    rating = float(m.get("vote_average") or 0.0)
                    return exact_match + starts_with + contains_match + lang_boost + min(pop, 100.0) + min(votes / 20.0, 100.0) + rating

                raw_searched.sort(key=search_rank, reverse=True)

                # Filter for quality: official franchise / notable vote counts / title containment
                for m in raw_searched:
                    title = (m.get("title") or "").lower()
                    orig_title = (m.get("original_title") or "").lower()
                    votes = int(m.get("vote_count") or 0)
                    pop = float(m.get("popularity") or 0)
                    is_exact = bool(q_lower == title or q_lower == orig_title or (q_lower in title and (votes >= 10 or pop >= 5.0)))
                    if is_exact or votes >= 50 or pop >= 15.0:
                        if m["id"] not in seen_ids:
                            seen_ids.add(m["id"])
                            m["is_direct_search_match"] = is_exact
                            if is_exact:
                                m["ai_reason"] = f"Official '{search_query}' release matching your search."
                            results.append(m)

                # Enrich with TMDB recommendations for top matched films
                if len(results) < MAX_RECOMMENDED_MOVIES and results:
                    top_ids = [m["id"] for m in results[:3]]
                    rec_params = {"include_adult": "false", "language": "en-US"}
                    if not TMDB_ACCESS_TOKEN:
                        rec_params["api_key"] = TMDB_API_KEY
                    rec_tasks = [
                        client.get(f"{BASE_URL}/movie/{mid}/recommendations", params=rec_params, headers=headers)
                        for mid in top_ids
                    ]
                    rec_resps = await asyncio.gather(*rec_tasks, return_exceptions=True)
                    for r_resp in rec_resps:
                        if hasattr(r_resp, "status_code") and r_resp.status_code == 200:
                            for rec_m in r_resp.json().get("results", []):
                                if rec_m.get("id") and rec_m.get("id") not in seen_ids and rec_m.get("poster_path"):
                                    if int(rec_m.get("vote_count") or 0) >= 20:
                                        seen_ids.add(rec_m["id"])
                                        results.append(rec_m)
                                        if len(results) >= MAX_RECOMMENDED_MOVIES:
                                            break
                        if len(results) >= MAX_RECOMMENDED_MOVIES:
                            break
        except Exception:
            pass

    # 🌟 STEP 2: If we still need more movies (or search was a general mood), run Discover pipeline
    if len(results) < MAX_RECOMMENDED_MOVIES:
        if not target_lang or target_lang.lower() == "all":
            # ALL LANGUAGES MODE (Strict Genre Recommendation across all industries):
            tasks = []
            for cluster in MULTI_LANGUAGE_CLUSTERS:
                cluster_genre = "16" if (cluster["lang"] == "ja" and not target_genre_ids) else genre_filter_str
                cluster_target_gids = {16} if (cluster["lang"] == "ja" and not target_genre_ids) else target_genre_ids
                tasks.append(
                    fetch_cluster_movies(client, url, base_params, headers, cluster["lang"], cluster_genre, cluster["weight"] + 2, cluster_target_gids)
                )
                
            cluster_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            valid_clusters = [cr for cr in cluster_results if isinstance(cr, list) and len(cr) > 0]
            max_len = max((len(c) for c in valid_clusters), default=0)
            for idx in range(max_len):
                for cluster_movies in valid_clusters:
                    if idx < len(cluster_movies):
                        movie = cluster_movies[idx]
                        if movie.get("id") not in seen_ids:
                            if not target_genre_ids or bool(set(movie.get("genre_ids", [])) & target_genre_ids):
                                seen_ids.add(movie.get("id"))
                                results.append(movie)
                                if len(results) >= MAX_RECOMMENDED_MOVIES:
                                    break
                if len(results) >= MAX_RECOMMENDED_MOVIES:
                    break
                            
            if len(results) < MAX_RECOMMENDED_MOVIES:
                extra_tasks = []
                for p in [1, 2, 3, 4]:
                    extra_params = {**base_params, "page": p}
                    if genre_filter_str:
                        extra_params["with_genres"] = genre_filter_str
                    extra_tasks.append(client.get(url, params=extra_params, headers=headers))
                    
                extra_res = await asyncio.gather(*extra_tasks, return_exceptions=True)
                for cr in extra_res:
                    if hasattr(cr, "status_code") and cr.status_code == 200:
                        for movie in cr.json().get("results", []):
                            if movie.get("id") not in seen_ids:
                                if not target_genre_ids or bool(set(movie.get("genre_ids", [])) & target_genre_ids):
                                    seen_ids.add(movie.get("id"))
                                    results.append(movie)
                                    if len(results) >= MAX_RECOMMENDED_MOVIES:
                                        break
                    if len(results) >= MAX_RECOMMENDED_MOVIES:
                        break
        else:
            # SPECIFIC REGIONAL / GLOBAL LANGUAGE MODE (Strict Genre + Language):
            is_indian_regional = target_lang in ["te", "ta", "ml", "kn", "pa", "mr", "bn", "gu", "or", "as", "ur"]
            lang_base_params = dict(base_params)
            if is_indian_regional:
                lang_base_params.pop("vote_count.gte", None)
                lang_base_params.pop("vote_average.gte", None)

            tasks = []
            for p in [1, 2, 3, 4, 5]:
                req_params = {**lang_base_params, "with_original_language": target_lang, "page": p}
                if genre_filter_str:
                    req_params["with_genres"] = genre_filter_str
                tasks.append(client.get(url, params=req_params, headers=headers))
                
            genre_resps = await asyncio.gather(*tasks, return_exceptions=True)
            for resp in genre_resps:
                if hasattr(resp, "status_code") and resp.status_code == 200:
                    for movie in resp.json().get("results", []):
                        if movie.get("id") not in seen_ids:
                            if not target_genre_ids or bool(set(movie.get("genre_ids", [])) & target_genre_ids):
                                seen_ids.add(movie.get("id"))
                                results.append(movie)
                                if len(results) >= MAX_RECOMMENDED_MOVIES:
                                    break
                if len(results) >= MAX_RECOMMENDED_MOVIES:
                    break

    # Take candidate pool (up to 36) to maximize streaming provider coverage
    candidate_pool = results[:36] if len(results) >= MAX_RECOMMENDED_MOVIES else results
    
    mood_tone = mood_data.get("tone_summary", "This movie matches your desired mood perfectly!")
    
    # Fetch streaming providers concurrently for candidate movies
    provider_tasks = [
        fetch_movie_provider(client, movie, region, headers, mood_tone, target_genre_ids)
        for movie in candidate_pool
    ]
    
    try:
        movies_enriched = await asyncio.wait_for(
            asyncio.gather(*provider_tasks, return_exceptions=True),
            timeout=3.5
        )
        valid_movies = []
        for i, m in enumerate(movies_enriched):
            if isinstance(m, dict) and "title" in m:
                valid_movies.append(m)
            elif i < len(candidate_pool):
                valid_movies.append(format_fallback_movie(candidate_pool[i], mood_tone, target_genre_ids))
        
        # Prioritize direct title search match first, then OTT streaming availability, then rating
        valid_movies.sort(
            key=lambda m: (
                1000 if m.get("is_direct_search_match") else 0,
                len(m.get("providers", [])) > 0,
                len(m.get("providers", [])),
                float(m.get("rating") or 0)
            ),
            reverse=True
        )
        
        # Absolute guarantee: if fewer than 24, backfill strictly with matching genres
        if len(valid_movies) < MAX_RECOMMENDED_MOVIES:
            existing_ids = {m.get("id") for m in valid_movies}
            for fallback_mov in get_static_fallback_movies(target_lang, genre_ids):
                if fallback_mov["id"] not in existing_ids:
                    existing_ids.add(fallback_mov["id"])
                    valid_movies.append(fallback_mov)
                if len(valid_movies) == MAX_RECOMMENDED_MOVIES:
                    break
                    
        return valid_movies[:MAX_RECOMMENDED_MOVIES]
    except Exception:
        # Fallback to base formatted movies + static fallback strictly prioritising genre
        fallback_list = [format_fallback_movie(m, mood_tone, target_genre_ids) for m in candidate_pool]
        existing_ids = {m.get("id") for m in fallback_list}
        for fallback_mov in get_static_fallback_movies(target_lang, genre_ids):
            if fallback_mov["id"] not in existing_ids:
                existing_ids.add(fallback_mov["id"])
                fallback_list.append(fallback_mov)
            if len(fallback_list) == MAX_RECOMMENDED_MOVIES:
                break
        return fallback_list[:MAX_RECOMMENDED_MOVIES]



