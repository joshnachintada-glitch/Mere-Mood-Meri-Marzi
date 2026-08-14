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
    "ko": "Korean",
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
    {"lang": "hi", "name": "Hindi", "weight": 4},
    {"lang": "te", "name": "Telugu", "weight": 4},
    {"lang": "ta", "name": "Tamil", "weight": 4},
    {"lang": "ml", "name": "Malayalam", "weight": 4},
    {"lang": "kn", "name": "Kannada", "weight": 3},
    {"lang": "mr|bn|pa|gu|or|as|ur", "name": "Regional Cinema", "weight": 3},
    {"lang": "ja", "name": "Anime", "weight": 3},
    {"lang": "en", "name": "English", "weight": 3},
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

# Comprehensive multi-language and multi-genre static fallback catalog (35+ masterpieces)
STATIC_FALLBACK_MOVIES: List[dict] = [
    # --- TELUGU ---
    {"id": 579974, "title": "RRR", "original_title": "RRR", "release_year": "2022", "rating": 8.0, "poster_path": "/wE0I6efAW4cDDmZQWtwZMOW44EJ.jpg", "overview": "A fictional history of two legendary revolutionaries and their journey away from home before they began fighting for their country in the 1920s.", "language_code": "te", "language_name": "Telugu", "genres": ["Action", "Drama"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com/title/81476453", "ai_reason": "Epic Indian masterpiece with electrifying thrills and emotion."},
    {"id": 341013, "title": "Baahubali: The Beginning", "original_title": "Baahubali: The Beginning", "release_year": "2015", "rating": 7.6, "poster_path": "/9ptcfQJ1oU0z2yE6e5hQp0L2n8H.jpg", "overview": "In the kingdom of Mahishmati, a young man learns about his royal heritage and the kingdom's epic battle for the throne.", "language_code": "te", "language_name": "Telugu", "genres": ["Action", "Adventure", "Fantasy"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Magnificent Indian fantasy war epic that reshaped Indian cinema."},
    {"id": 350312, "title": "Baahubali 2: The Conclusion", "original_title": "Baahubali 2: The Conclusion", "release_year": "2017", "rating": 7.8, "poster_path": "/tA1qV3x7bM1pP3k8p5pY6q8w3kL.jpg", "overview": "Amarendra Baahubali must protect the rightful heir to the throne from a conniving brother.", "language_code": "te", "language_name": "Telugu", "genres": ["Action", "Drama", "Fantasy"], "providers": [{"provider_id": 122, "provider_name": "Disney+ Hotstar", "logo_path": "/7Fl8ylPD73btB8g3p5nQZz4c7vY.jpg"}], "watch_link": "https://www.hotstar.com", "ai_reason": "Triumphant, emotional resolution to the greatest Indian cinematic saga."},
    {"id": 624860, "title": "Pushpa: The Rise", "original_title": "Pushpa: The Rise", "release_year": "2021", "rating": 7.6, "poster_path": "/v1V8Gf9v89fHjL6w1Q6y6q8w3kL.jpg", "overview": "Pushpa Raj, a coolie, rises in the world of red sandalwood smuggling, making enemies along the way.", "language_code": "te", "language_name": "Telugu", "genres": ["Action", "Crime", "Thriller"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "High-octane mass action thriller with iconic swag."},
    {"id": 554230, "title": "Jersey", "original_title": "Jersey", "release_year": "2019", "rating": 8.3, "poster_path": "/k9Y7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "A failed cricketer decides to revive his cricketing career in his late thirties to fulfill his son's wish.", "language_code": "te", "language_name": "Telugu", "genres": ["Drama", "Family"], "providers": [{"provider_id": 122, "provider_name": "Disney+ Hotstar", "logo_path": "/7Fl8ylPD73btB8g3p5nQZz4c7vY.jpg"}], "watch_link": "https://www.hotstar.com", "ai_reason": "Deeply inspirational and emotional Telugu sports drama."},

    # --- HINDI ---
    {"id": 26022, "title": "3 Idiots", "original_title": "3 Idiots", "release_year": "2009", "rating": 8.0, "poster_path": "/66A9MqXOyVFCssoloscw79z8swE.jpg", "overview": "Two friends embark on a quest for a lost buddy while revisiting their college days and recalling the memories of their friend who inspired them to think differently.", "language_code": "hi", "language_name": "Hindi", "genres": ["Comedy", "Drama"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Timeless feel-good comedy and inspiring life lessons."},
    {"id": 850165, "title": "Jawan", "original_title": "Jawan", "release_year": "2023", "rating": 7.3, "poster_path": "/jYWmVxRjZt75sBvU7Q29J2yVq8D.jpg", "overview": "A high-octane action thriller which outlines the emotional journey of a man who is set to rectify the wrongs in the society.", "language_code": "hi", "language_name": "Hindi", "genres": ["Action", "Thriller"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "High energy action thriller with memorable mass cinematic moments."},
    {"id": 20453, "title": "Taare Zameen Par", "original_title": "Taare Zameen Par", "release_year": "2007", "rating": 8.0, "poster_path": "/8bQ7y1n6pP0lM9k2w4yP6q8w3kL.jpg", "overview": "An eight-year-old boy is thought to be a lazy trouble-maker, until the new art teacher discovers his real issue.", "language_code": "hi", "language_name": "Hindi", "genres": ["Drama", "Family"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Deeply moving family masterpiece that warms the soul."},
    {"id": 19404, "title": "Dilwale Dulhania Le Jayenge", "original_title": "Dilwale Dulhania Le Jayenge", "release_year": "1995", "rating": 8.5, "poster_path": "/lfR2v835SpHjuNWL5H2b9k8q7W7.jpg", "overview": "Raj and Simran meet on a trip across Europe and fall in love, but Simran is promised to another.", "language_code": "hi", "language_name": "Hindi", "genres": ["Romance", "Drama", "Comedy"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "The quintessential Indian romantic love story."},
    {"id": 361743, "title": "Tumbbad", "original_title": "Tumbbad", "release_year": "2018", "rating": 8.2, "poster_path": "/6N97u42qG1cE6n4X4Bq2N8g9s.jpg", "overview": "A mythological story about a goddess who created the entire universe and a demon of greed.", "language_code": "hi", "language_name": "Hindi", "genres": ["Horror", "Fantasy", "Drama"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Atmospheric, visually stunning horror fantasy masterpiece."},
    {"id": 360814, "title": "Dangal", "original_title": "Dangal", "release_year": "2016", "rating": 8.0, "poster_path": "/m1Y7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "Former wrestler Mahavir Singh Phogat and his two wrestler daughters struggle towards glory at the Commonwealth Games.", "language_code": "hi", "language_name": "Hindi", "genres": ["Drama", "Action", "Family"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Triumph of spirit and powerhouse biographical sports drama."},

    # --- TAMIL ---
    {"id": 974036, "title": "Jailer", "original_title": "Jailer", "release_year": "2023", "rating": 7.2, "poster_path": "/7Lq84Yj5QoM1dY3rP8tZ3mN7bQ8.jpg", "overview": "A retired jailer goes on a manhunt to find his son's killers. But the road leads him to a familiar, darker world.", "language_code": "ta", "language_name": "Tamil", "genres": ["Action", "Crime", "Thriller"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Stylish swagger and unstoppable heroic screen presence."},
    {"id": 838240, "title": "Robot 2.0", "original_title": "2.0", "release_year": "2018", "rating": 6.2, "poster_path": "/8p2L3s9m7k7Y1q9m7k7Y1q9m7k7.jpg", "overview": "When mobile phones start flying into the sky, scientists reboot Chitti the robot to battle a feathered creature.", "language_code": "ta", "language_name": "Tamil", "genres": ["Action", "Sci-Fi"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Sci-Fi extravaganza featuring Rajinikanth & Akshay Kumar."},
    {"id": 78383, "title": "Super Deluxe", "original_title": "Super Deluxe", "release_year": "2019", "rating": 8.2, "poster_path": "/1kP4Y9qM9k7Y1q9m7k7Y1q9m7k7.jpg", "overview": "An unfaithful wife, an estranged father, a priest and an angry boy find themselves in the most unexpected predicaments.", "language_code": "ta", "language_name": "Tamil", "genres": ["Drama", "Crime", "Thriller"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Brilliant, quirky multi-narrative cinematic gem."},
    {"id": 842675, "title": "Vikram", "original_title": "Vikram", "release_year": "2022", "rating": 8.1, "poster_path": "/n2Y7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "A special agent investigates a murder committed by a masked group of serial killers.", "language_code": "ta", "language_name": "Tamil", "genres": ["Action", "Thriller", "Crime"], "providers": [{"provider_id": 122, "provider_name": "Disney+ Hotstar", "logo_path": "/7Fl8ylPD73btB8g3p5nQZz4c7vY.jpg"}], "watch_link": "https://www.hotstar.com", "ai_reason": "Adrenaline-fueled cinematic universe action thriller with Kamal Haasan."},

    # --- MALAYALAM ---
    {"id": 490132, "title": "Manjummel Boys", "original_title": "Manjummel Boys", "release_year": "2024", "rating": 8.1, "poster_path": "/bW3mB3b1g7HkFfLgZ2nB9mK1jQ8.jpg", "overview": "A group of friends from a small town embark on a vacation to Kodaikanal, where an unexpected mishap tests their bond.", "language_code": "ml", "language_name": "Malayalam", "genres": ["Adventure", "Drama", "Thriller"], "providers": [{"provider_id": 122, "provider_name": "Disney+ Hotstar", "logo_path": "/7Fl8ylPD73btB8g3p5nQZz4c7vY.jpg"}], "watch_link": "https://www.hotstar.com", "ai_reason": "Gripping survival drama celebrating the power of true friendship."},
    {"id": 986056, "title": "Premalu", "original_title": "Premalu", "release_year": "2024", "rating": 7.9, "poster_path": "/p1K7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "Sachin's quest for love takes unexpected turns, leading to a hilarious romantic triangle in Hyderabad.", "language_code": "ml", "language_name": "Malayalam", "genres": ["Comedy", "Romance"], "providers": [{"provider_id": 122, "provider_name": "Disney+ Hotstar", "logo_path": "/7Fl8ylPD73btB8g3p5nQZz4c7vY.jpg"}], "watch_link": "https://www.hotstar.com", "ai_reason": "Delightful romantic comedy packed with laughs and lovable vibes."},
    {"id": 1184918, "title": "Aavesham", "original_title": "Aavesham", "release_year": "2024", "rating": 8.0, "poster_path": "/q3K7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "Three college students in Bangalore seek the help of a local eccentric gangster named Ranga to get back at their bullies.", "language_code": "ml", "language_name": "Malayalam", "genres": ["Action", "Comedy"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Wildly energetic mass entertainer with an iconic Fahadh Faasil performance."},
    {"id": 269149, "title": "Drishyam", "original_title": "Drishyam", "release_year": "2013", "rating": 8.3, "poster_path": "/j4K7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "A man goes to extreme lengths to save his family from punishment after the family commits an accidental crime.", "language_code": "ml", "language_name": "Malayalam", "genres": ["Thriller", "Crime", "Drama"], "providers": [{"provider_id": 122, "provider_name": "Disney+ Hotstar", "logo_path": "/7Fl8ylPD73btB8g3p5nQZz4c7vY.jpg"}], "watch_link": "https://www.hotstar.com", "ai_reason": "Masterclass thriller with legendary suspense and storytelling."},

    # --- KANNADA ---
    {"id": 843241, "title": "Kantara", "original_title": "Kantara", "release_year": "2022", "rating": 7.8, "poster_path": "/p7u44p8c0ZJ53x1f5U2s31D79.jpg", "overview": "When greed paves the way for betrayal, scheming and murder, a young tribal man reluctantly embraces the tradition of his ancestors to seek justice.", "language_code": "kn", "language_name": "Kannada", "genres": ["Action", "Drama", "Fantasy"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Folkloric visual spectacle with breathtaking divine climax."},
    {"id": 940551, "title": "Sapta Sagaradaache Ello - Side A", "original_title": "Sapta Sagaradaache Ello - Side A", "release_year": "2023", "rating": 8.1, "poster_path": "/8lK7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "Manu and Priya are deeply in love, but their dream of building a life together faces an insurmountable trial.", "language_code": "kn", "language_name": "Kannada", "genres": ["Romance", "Drama"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Poetic and deeply touching romance with soul-stirring music."},
    {"id": 585268, "title": "K.G.F: Chapter 1", "original_title": "K.G.F: Chapter 1", "release_year": "2018", "rating": 8.2, "poster_path": "/7Lq84Yj5QoM1dY3rP8tZ3mN7bQ8.jpg", "overview": "In the 1970s, a fierce rebel rises against brutal oppression in the Kolar Gold Fields.", "language_code": "kn", "language_name": "Kannada", "genres": ["Action", "Crime", "Drama"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Massive elevation, gritty style, and ground-breaking action."},

    # --- PUNJABI ---
    {"id": 157834, "title": "Carry On Jatta", "original_title": "Carry On Jatta", "release_year": "2012", "rating": 8.1, "poster_path": "/k9Y7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "A hilarious comedy of errors when Jass lies about having no family to marry the girl of his dreams.", "language_code": "pa", "language_name": "Punjabi", "genres": ["Comedy", "Romance"], "providers": [{"provider_id": 122, "provider_name": "Disney+ Hotstar", "logo_path": "/7Fl8ylPD73btB8g3p5nQZz4c7vY.jpg"}], "watch_link": "https://www.hotstar.com", "ai_reason": "Cult classic Punjabi comedy full of relentless laughs."},
    {"id": 361921, "title": "Angrej", "original_title": "Angrej", "release_year": "2015", "rating": 8.3, "poster_path": "/m1Y7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "A thoughtful and endearing romance set in rural Punjab of 1945.", "language_code": "pa", "language_name": "Punjabi", "genres": ["Romance", "Comedy", "Drama"], "providers": [{"provider_id": 122, "provider_name": "Disney+ Hotstar", "logo_path": "/7Fl8ylPD73btB8g3p5nQZz4c7vY.jpg"}], "watch_link": "https://www.hotstar.com", "ai_reason": "Heartwarming vintage romance capturing traditional Punjabi culture."},
    {"id": 551829, "title": "Qismat", "original_title": "Qismat", "release_year": "2018", "rating": 8.0, "poster_path": "/n2Y7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "A man falls in love while pretending to study in Chandigarh, leading to an emotional romantic journey.", "language_code": "pa", "language_name": "Punjabi", "genres": ["Drama", "Romance"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Tearjerker romantic drama with magnificent musical tracks."},

    # --- MARATHI ---
    {"id": 393729, "title": "Sairat", "original_title": "Sairat", "release_year": "2016", "rating": 8.0, "poster_path": "/j4K7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "Two college students from different castes fall in love, defying societal constraints.", "language_code": "mr", "language_name": "Marathi", "genres": ["Drama", "Romance"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Sensational Marathi romantic drama that made Indian cinema history."},
    {"id": 376290, "title": "Natsamrat", "original_title": "Natsamrat", "release_year": "2016", "rating": 8.3, "poster_path": "/h5K7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "A veteran Shakespearean theatre actor struggles with old age and ingratitude from his children.", "language_code": "mr", "language_name": "Marathi", "genres": ["Drama"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Nana Patekar's finest dramatic powerhouse performance."},

    # --- BENGALI ---
    {"id": 582, "title": "Pather Panchali", "original_title": "Pather Panchali", "release_year": "1955", "rating": 8.3, "poster_path": "/9vK7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "Satyajit Ray's timeless portrait of childhood life in a rural Bengali village.", "language_code": "bn", "language_name": "Bengali", "genres": ["Drama"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "One of the greatest cinematic achievements in world cinema history."},
    {"id": 105820, "title": "Bhooter Bhabishyat", "original_title": "Bhooter Bhabishyat", "release_year": "2012", "rating": 8.0, "poster_path": "/x2K7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "A group of ghosts inhabiting an old mansion unite to protect their home from being demolished.", "language_code": "bn", "language_name": "Bengali", "genres": ["Comedy", "Fantasy"], "providers": [{"provider_id": 122, "provider_name": "Disney+ Hotstar", "logo_path": "/7Fl8ylPD73btB8g3p5nQZz4c7vY.jpg"}], "watch_link": "https://www.hotstar.com", "ai_reason": "Brilliantly witty Bengali supernatural comedy satire."},

    # --- GUJARATI ---
    {"id": 643210, "title": "Hellaro", "original_title": "Hellaro", "release_year": "2019", "rating": 8.4, "poster_path": "/c3K7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "In a remote Kutch village, suppressed women find freedom through the joy of Garba folk dance.", "language_code": "gu", "language_name": "Gujarati", "genres": ["Drama", "Music"], "providers": [{"provider_id": 122, "provider_name": "Disney+ Hotstar", "logo_path": "/7Fl8ylPD73btB8g3p5nQZz4c7vY.jpg"}], "watch_link": "https://www.hotstar.com", "ai_reason": "National Award-winning Gujarati visual triumph of spirit and folk dance."},
    {"id": 839369, "title": "Chhello Show (Last Film Show)", "original_title": "Chhello Show", "release_year": "2021", "rating": 7.6, "poster_path": "/d4K7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "A 9-year-old boy in rural Gujarat falls in love with cinema and light.", "language_code": "gu", "language_name": "Gujarati", "genres": ["Drama"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "India's official entry to the Oscars, a love letter to celluloid."},

    # --- ODIA ---
    {"id": 1045230, "title": "DAMaN", "original_title": "DAMaN", "release_year": "2022", "rating": 8.5, "poster_path": "/e5K7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "A young doctor posted in a remote tribal area in Odisha battles malaria and superstition.", "language_code": "or", "language_name": "Odia", "genres": ["Drama", "Adventure"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Inspirational Odia blockbuster based on real humanitarian dedication."},

    # --- ASSAMESE ---
    {"id": 476839, "title": "Village Rockstars", "original_title": "Village Rockstars", "release_year": "2017", "rating": 7.7, "poster_path": "/f6K7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "A 10-year-old village girl in Assam dreams of owning an electric guitar and forming a rock band.", "language_code": "as", "language_name": "Assamese", "genres": ["Drama", "Family"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Poetic, deeply authentic National Award-winning Assamese cinema."},

    # --- URDU ---
    {"id": 478392, "title": "The Legend of Maula Jatt", "original_title": "The Legend of Maula Jatt", "release_year": "2022", "rating": 8.0, "poster_path": "/g7K7Y1q9m7k7Y1q9m7k7Y1q9m7k.jpg", "overview": "A fierce prizefighter with a tortured past seeks vengeance against his mortal rival Noori Natt.", "language_code": "ur", "language_name": "Urdu", "genres": ["Action", "Drama"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Visual spectacle with intense martial rivalry and epic production."},

    # --- ANIME / JAPANESE ---
    {"id": 372058, "title": "Your Name.", "original_title": "君の名は。", "release_year": "2016", "rating": 8.5, "poster_path": "/q719qXXEzOoYaps6qFsR65qW3iS.jpg", "overview": "Two high schoolers spark a connection after discovering they are magically swapping bodies.", "language_code": "ja", "language_name": "Japanese / Anime", "genres": ["Animation", "Romance", "Drama"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Gorgeous anime masterpiece full of heart, mystery, and soul."},
    {"id": 129, "title": "Spirited Away", "original_title": "千と千尋の神隠し", "release_year": "2001", "rating": 8.5, "poster_path": "/393t37SN0Bidfrki2q7V6uESJ7C.jpg", "overview": "A young girl enters a world ruled by gods, witches, and spirits, where humans are changed into beasts.", "language_code": "ja", "language_name": "Japanese / Anime", "genres": ["Animation", "Family", "Fantasy"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Studio Ghibli's Oscar-winning fantasy marvel."},
    {"id": 635302, "title": "Demon Slayer: Mugen Train", "original_title": "劇場版「鬼滅の刃」無限列車編", "release_year": "2020", "rating": 8.3, "poster_path": "/h8Rb9gBr48ODigDrng1Pz2Stafq.jpg", "overview": "Tanjiro and the Flame Hashira Kyojuro Rengoku board the Infinity Train to battle a powerful demon.", "language_code": "ja", "language_name": "Japanese / Anime", "genres": ["Animation", "Action", "Fantasy"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Unrivaled animation action with breathtaking emotional resonance."},
    {"id": 568332, "title": "Weathering with You", "original_title": "天気の子", "release_year": "2019", "rating": 8.0, "poster_path": "/qgrk7r1fUmgoi0LqV77r5rV5K3f.jpg", "overview": "A high-school runaway finds friendship with an orphan girl who has the uncanny ability to stop the rain and clear the sky.", "language_code": "ja", "language_name": "Japanese / Anime", "genres": ["Animation", "Romance", "Fantasy"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Visually arresting romantic fantasy anime on weather and love."},

    # --- ENGLISH / GLOBAL ---
    {"id": 157336, "title": "Interstellar", "original_title": "Interstellar", "release_year": "2014", "rating": 8.4, "poster_path": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg", "overview": "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel.", "language_code": "en", "language_name": "English", "genres": ["Sci-Fi", "Drama", "Adventure"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Mind-expanding cinematic exploration of love and spacetime."},
    {"id": 872585, "title": "Oppenheimer", "original_title": "Oppenheimer", "release_year": "2023", "rating": 8.1, "poster_path": "/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg", "overview": "The story of J. Robert Oppenheimer's role in the development of the atomic bomb during World War II.", "language_code": "en", "language_name": "English", "genres": ["Drama", "History"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Oscar-winning cinematic tour de force with gripping intensity."},
    {"id": 693134, "title": "Dune: Part Two", "original_title": "Dune: Part Two", "release_year": "2024", "rating": 8.2, "poster_path": "/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg", "overview": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.", "language_code": "en", "language_name": "English", "genres": ["Sci-Fi", "Adventure"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Epic visionary science fiction on a monumental scale."},
    {"id": 569094, "title": "Spider-Man: Across the Spider-Verse", "original_title": "Spider-Man: Across the Spider-Verse", "release_year": "2023", "rating": 8.4, "poster_path": "/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg", "overview": "Miles Morales catapults across the Multiverse, where he encounters a team of Spider-People charged with protecting its very existence.", "language_code": "en", "language_name": "English", "genres": ["Animation", "Action", "Adventure"], "providers": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg"}], "watch_link": "https://www.netflix.com", "ai_reason": "Revolutionary visual animation and multiverse adventure."},
    {"id": 49026, "title": "The Dark Knight Rises", "original_title": "The Dark Knight Rises", "release_year": "2012", "rating": 7.8, "poster_path": "/hrJ0cqR2t6bZ75rR2t4w3qT4yYp.jpg", "overview": "Batman returns to save Gotham from the ruthless terrorist Bane.", "language_code": "en", "language_name": "English", "genres": ["Action", "Crime", "Drama"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Grand superhero climax with towering stakes and heroic scale."},

    # --- KOREAN ---
    {"id": 496243, "title": "Parasite", "original_title": "기생충", "release_year": "2019", "rating": 8.5, "poster_path": "/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg", "overview": "All unemployed, Ki-taek's family takes peculiar interest in the wealthy and glamorous Parks for their livelihood.", "language_code": "ko", "language_name": "Korean", "genres": ["Comedy", "Thriller", "Drama"], "providers": [{"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/emthp39XA2YMNehvisUb0qRpAcG.jpg"}], "watch_link": "https://www.primevideo.com", "ai_reason": "Brilliant dark comedy thriller with unforgettable twists."}
]

def get_static_fallback_movies(preferred_lang: Optional[str] = None, preferred_genres: Optional[List[int]] = None) -> List[dict]:
    """Returns exactly 24 guaranteed top movies, prioritizing preferred language and genres."""
    pool = list(STATIC_FALLBACK_MOVIES)
    
    preferred_genre_names = []
    if preferred_genres:
        preferred_genre_names = [GENRE_MAP[g] for g in preferred_genres if g in GENRE_MAP]

    def sort_score(m: dict) -> int:
        score = 0
        if preferred_lang and preferred_lang != "all":
            if m.get("language_code") == preferred_lang:
                score += 10
        if preferred_genre_names:
            movie_genres = m.get("genres", [])
            for g in movie_genres:
                if g in preferred_genre_names:
                    score += 5
        return score

    sorted_pool = sorted(pool, key=sort_score, reverse=True)
    
    # Ensure distinct IDs and pad to exactly 24
    seen_ids = set()
    result = []
    for m in sorted_pool:
        if m["id"] not in seen_ids:
            seen_ids.add(m["id"])
            result.append(m)
        if len(result) == MAX_RECOMMENDED_MOVIES:
            break
            
    # Guarantee at least 24 items
    if len(result) < MAX_RECOMMENDED_MOVIES:
        for m in pool:
            if m["id"] not in seen_ids:
                seen_ids.add(m["id"])
                result.append(m)
            if len(result) == MAX_RECOMMENDED_MOVIES:
                break
                
    return result[:MAX_RECOMMENDED_MOVIES]

def format_fallback_movie(movie: dict, mood_tone: str) -> dict:
    movie_id = movie["id"]
    lang_code = movie.get("original_language", "en")
    lang_name = LANGUAGE_MAP.get(lang_code, lang_code.upper())
    movie_genre_names = [GENRE_MAP.get(gid) for gid in movie.get("genre_ids", []) if gid in GENRE_MAP]
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
        "providers": [],
        "watch_link": f"https://www.themoviedb.org/movie/{movie_id}/watch",
        "ai_reason": mood_tone or "This movie matches your desired mood perfectly!"
    }

async def fetch_movie_provider(client: httpx.AsyncClient, movie: dict, region: str, headers: dict, mood_tone: str) -> dict:
    movie_id = movie["id"]
    lang_code = movie.get("original_language", "en")
    lang_name = LANGUAGE_MAP.get(lang_code, lang_code.upper())
    movie_genre_names = [GENRE_MAP.get(gid) for gid in movie.get("genre_ids", []) if gid in GENRE_MAP]
    
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
                timeout=2.0
            )
            if prov_resp.status_code == 200:
                prov_data = prov_resp.json()
                if "results" in prov_data and region in prov_data["results"]:
                    region_data = prov_data["results"][region]
                    if "flatrate" in region_data:
                        providers = region_data["flatrate"]
                    elif "rent" in region_data:
                        providers = region_data["rent"]
                    elif "buy" in region_data:
                        providers = region_data["buy"]
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
        "ai_reason": mood_tone or "This movie matches your desired mood perfectly!"
    }

async def fetch_cluster_movies(client: httpx.AsyncClient, url: str, base_params: dict, headers: dict, lang_code: str, genre_filter: Optional[str], target_count: int) -> list:
    """Fetch movies for a specific language and genre cluster with randomized page offset."""
    random_page = random.randint(1, 5)
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
                random.shuffle(movies)
                return movies[:target_count]
    except Exception:
        pass
    return []

async def get_movie_recommendations(mood_data: dict, region: str = "IN", explicit_language: str | None = None) -> list:
    if not TMDB_API_KEY and not TMDB_ACCESS_TOKEN:
        raise ValueError("TMDB API credentials are not set.")
    
    genre_ids = mood_data.get("primary_genre_ids", [])
    
    # Determine genres to query: if specific genre is given, expand with complementary genres;
    # if general exploration or multiple genres, span across all major genres
    genres_to_query = []
    if genre_ids and len(genre_ids) == 1:
        primary_g = genre_ids[0]
        comp = COMPLEMENTARY_GENRES.get(primary_g, [18, 35, 28])
        # Mix primary and complementary genres
        genres_to_query = [primary_g] + comp[:3]
    elif genre_ids and len(genre_ids) > 1:
        genres_to_query = genre_ids
    else:
        # Sample varied genres across Action, Comedy, Drama, Horror, Sci-Fi, Romance, Thriller, Anime
        shuffled_genres = ALL_MAJOR_GENRES.copy()
        random.shuffle(shuffled_genres)
        genres_to_query = shuffled_genres[:6]

    base_params = {
        "include_adult": "false",
        "include_video": "false",
        "language": "en-US",
        "sort_by": "popularity.desc",
        "vote_average.gte": 5.0,
        "vote_count.gte": 10
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
    
    if not target_lang or target_lang.lower() == "all":
        # 🌟 ALL LANGUAGES & EVERY GENRE MODE:
        # Fetch concurrently across language clusters with distributed genres
        tasks = []
        for i, cluster in enumerate(MULTI_LANGUAGE_CLUSTERS):
            assigned_genre = genres_to_query[i % len(genres_to_query)] if genres_to_query else None
            genre_str = str(assigned_genre) if assigned_genre else None
            # Request buffer of candidates from each cluster
            tasks.append(
                fetch_cluster_movies(client, url, base_params, headers, cluster["lang"], genre_str, cluster["weight"] + 2)
            )
            
        cluster_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Interleave and blend across all language and genre clusters
        valid_clusters = [cr for cr in cluster_results if isinstance(cr, list) and len(cr) > 0]
        max_len = max((len(c) for c in valid_clusters), default=0)
        for idx in range(max_len):
            for cluster_movies in valid_clusters:
                if idx < len(cluster_movies):
                    movie = cluster_movies[idx]
                    if movie.get("id") not in seen_ids:
                        seen_ids.add(movie.get("id"))
                        results.append(movie)
                        if len(results) >= MAX_RECOMMENDED_MOVIES:
                            break
            if len(results) >= MAX_RECOMMENDED_MOVIES:
                break
                        
        # If needed, fetch additional diversity across major genres to reach 20
        if len(results) < MAX_RECOMMENDED_MOVIES:
            extra_genres = random.sample(ALL_MAJOR_GENRES, min(4, len(ALL_MAJOR_GENRES)))
            extra_tasks = [
                fetch_cluster_movies(client, url, base_params, headers, "hi|te|ta|ml|kn|ja|en", str(g), 5)
                for g in extra_genres
            ]
            extra_res = await asyncio.gather(*extra_tasks, return_exceptions=True)
            for cr in extra_res:
                if isinstance(cr, list):
                    for movie in cr:
                        if movie.get("id") not in seen_ids:
                            seen_ids.add(movie.get("id"))
                            results.append(movie)
                            if len(results) >= MAX_RECOMMENDED_MOVIES:
                                break
                if len(results) >= MAX_RECOMMENDED_MOVIES:
                    break

        # Broad multi-lingual fallback to guarantee 20 movies
        if len(results) < MAX_RECOMMENDED_MOVIES:
            for fb_page in [1, 2, 3]:
                if len(results) >= MAX_RECOMMENDED_MOVIES:
                    break
                fb_params = {**base_params, "page": fb_page}
                try:
                    fb_resp = await client.get(url, params=fb_params, headers=headers)
                    if fb_resp.status_code == 200:
                        for movie in fb_resp.json().get("results", []):
                            if movie.get("id") not in seen_ids:
                                seen_ids.add(movie.get("id"))
                                results.append(movie)
                                if len(results) >= MAX_RECOMMENDED_MOVIES:
                                    break
                except Exception:
                    pass
    else:
        # 🎬 SPECIFIC REGIONAL / GLOBAL LANGUAGE MODE:
        # Query pages 1 and 2 for the requested genre and complementary genres
        is_indian_regional = target_lang in ["te", "ta", "ml", "kn", "pa", "mr", "bn", "gu", "or", "as", "ur"]
        lang_base_params = dict(base_params)
        if is_indian_regional:
            # Regional languages have thousands of movies on TMDB with vote count >= 0
            lang_base_params.pop("vote_count.gte", None)
            lang_base_params.pop("vote_average.gte", None)

        tasks = []
        # Query primary genre pages 1 and 2
        for g in genres_to_query[:3]:
            tasks.append(
                client.get(url, params={**lang_base_params, "with_original_language": target_lang, "with_genres": str(g), "page": 1}, headers=headers)
            )
            tasks.append(
                client.get(url, params={**lang_base_params, "with_original_language": target_lang, "with_genres": str(g), "page": 2}, headers=headers)
            )
        # Broad queries for the language to ensure abundance of titles
        tasks.append(
            client.get(url, params={**lang_base_params, "with_original_language": target_lang, "page": 1}, headers=headers)
        )
        tasks.append(
            client.get(url, params={**lang_base_params, "with_original_language": target_lang, "page": 2}, headers=headers)
        )
            
        genre_resps = await asyncio.gather(*tasks, return_exceptions=True)
        pool = []
        for resp in genre_resps:
            if hasattr(resp, "status_code") and resp.status_code == 200:
                for movie in resp.json().get("results", []):
                    if movie.get("id") not in seen_ids:
                        seen_ids.add(movie.get("id"))
                        pool.append(movie)
                        
        random.shuffle(pool)
        results = pool[:MAX_RECOMMENDED_MOVIES]
        
        # Parallel fallback with further relaxed pages if needed
        if len(results) < MAX_RECOMMENDED_MOVIES:
            fb_tasks = [
                client.get(url, params={**lang_base_params, "with_original_language": target_lang, "page": p}, headers=headers)
                for p in [3, 4, 5]
            ]
            fb_resps = await asyncio.gather(*fb_tasks, return_exceptions=True)
            for resp in fb_resps:
                if hasattr(resp, "status_code") and resp.status_code == 200:
                    for movie in resp.json().get("results", []):
                        if movie.get("id") not in seen_ids:
                            seen_ids.add(movie.get("id"))
                            results.append(movie)
                            if len(results) >= MAX_RECOMMENDED_MOVIES:
                                break

    # Ensure final count cap is exactly 20
    # Ensure final count cap is exactly 24
    results = results[:MAX_RECOMMENDED_MOVIES]
    
    mood_tone = mood_data.get("tone_summary", "This movie matches your desired mood perfectly!")
    
    # Fetch streaming providers concurrently for all 24 movies
    provider_tasks = [
        fetch_movie_provider(client, movie, region, headers, mood_tone)
        for movie in results
    ]
    
    try:
        movies_enriched = await asyncio.wait_for(
            asyncio.gather(*provider_tasks, return_exceptions=True),
            timeout=3.0
        )
        valid_movies = []
        for i, m in enumerate(movies_enriched):
            if isinstance(m, dict) and "title" in m:
                valid_movies.append(m)
            elif i < len(results):
                valid_movies.append(format_fallback_movie(results[i], mood_tone))
        
        # Absolute guarantee: if fewer than 24, backfill to exactly 24
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
        # Instant fallback to base formatted movies + static fallback to ensure 24 items
        fallback_list = [format_fallback_movie(m, mood_tone) for m in results]
        existing_ids = {m.get("id") for m in fallback_list}
        for fallback_mov in get_static_fallback_movies(target_lang, genre_ids):
            if fallback_mov["id"] not in existing_ids:
                existing_ids.add(fallback_mov["id"])
                fallback_list.append(fallback_mov)
            if len(fallback_list) == MAX_RECOMMENDED_MOVIES:
                break
        return fallback_list[:MAX_RECOMMENDED_MOVIES]



