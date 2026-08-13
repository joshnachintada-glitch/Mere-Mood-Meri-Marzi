import React, { useState } from 'react';
import axios from 'axios';
import Navbar from './components/Navbar';
import MoodInput from './components/MoodInput';
import MovieCard from './components/MovieCard';
import { GradientBackground } from '@/components/ui/silk-blend-gradient';
import { Film, Sparkles, Filter } from 'lucide-react';

function App() {
  const [movies, setMovies] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [moodAnalysis, setMoodAnalysis] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState("all");
  const [activeFilterLang, setActiveFilterLang] = useState("all");

  const handleSearch = async (mood, language = selectedLanguage) => {
    setIsLoading(true);
    setError(null);
    setHasSearched(true);
    setMovies([]);
    setActiveFilterLang("all");
    
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      const response = await axios.post(`${apiUrl}/api/recommend`, {
        mood: mood,
        region: 'IN',
        language: language === 'all' ? null : language
      });
      
      if (response.data.error) {
        setError(response.data.error);
      } else {
        setMovies(response.data.movies || []);
        setMoodAnalysis(response.data.mood_analysis || null);
      }
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.error || err.response?.data?.detail || err.message;
      setError(`Failed to fetch recommendations (${detail}). Ensure backend is running and API keys are set.`);
    } finally {
      setIsLoading(false);
    }
  };

  // Filter movies in UI if user clicks on specific language tab in results
  const displayedMovies = activeFilterLang === "all"
    ? movies
    : movies.filter(m => m.language_code === activeFilterLang);

  // Get unique languages present in current search results
  const availableResultLangs = Array.from(
    new Set(movies.map(m => m.language_code).filter(Boolean))
  ).map(code => {
    const matched = movies.find(m => m.language_code === code);
    return {
      code,
      name: matched?.language_name || code.toUpperCase()
    };
  });

  return (
    <div className="min-h-screen relative z-0 text-slate-100">
      <GradientBackground className="absolute inset-0 -z-10" />
      <Navbar />
      
      <main className="container mx-auto px-4 pb-20">
        <MoodInput 
          onSearch={handleSearch} 
          isLoading={isLoading} 
          selectedLanguage={selectedLanguage}
          setSelectedLanguage={setSelectedLanguage}
        />
        
        {error && (
          <div className="bg-red-500/20 border border-red-500 text-white px-6 py-4 rounded-xl max-w-2xl mx-auto mb-10 backdrop-blur-md">
            <p className="font-bold">Oops! Something went wrong.</p>
            <p className="text-sm opacity-80">{error}</p>
          </div>
        )}

        {hasSearched && !isLoading && movies.length === 0 && !error && (
          <div className="text-center text-white/70 py-16 max-w-md mx-auto bg-white/5 rounded-2xl border border-white/10 backdrop-blur-md">
            <Film className="w-10 h-10 mx-auto mb-3 text-white/40" />
            <p className="text-lg font-semibold text-white">No movies found for this mood & language.</p>
            <p className="text-sm text-white/60 mt-1">Try choosing "All Languages" or search with different keywords!</p>
          </div>
        )}

        {movies.length > 0 && (
          <div className="mt-8">
            {/* Header & Vibes */}
            <div className="flex items-center justify-between mb-6 flex-wrap gap-4 bg-slate-950/40 p-4 rounded-2xl border border-white/10 backdrop-blur-md">
              <div>
                <h3 className="text-2xl font-extrabold flex items-center gap-2">
                  <Film className="w-6 h-6 text-amber-400" />
                  Your Movie Matches ({displayedMovies.length})
                </h3>
                {moodAnalysis?.tone_summary && (
                  <p className="text-sm text-white/70 mt-1 flex items-center gap-1.5">
                    <Sparkles className="w-4 h-4 text-pink-400 shrink-0" />
                    <span>{moodAnalysis.tone_summary}</span>
                  </p>
                )}
              </div>

              {moodAnalysis?.keywords && moodAnalysis.keywords.length > 0 && (
                <div className="flex gap-1.5 flex-wrap items-center">
                  <span className="text-xs text-white/50 font-semibold uppercase tracking-wider">Vibes:</span>
                  {moodAnalysis.keywords.slice(0, 4).map((kw, i) => (
                    <span key={i} className="text-xs text-amber-300 bg-amber-500/10 px-2.5 py-1 rounded-full border border-amber-400/20 font-medium">
                      #{kw}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Quick Result Language Filters if results contain multiple languages */}
            {availableResultLangs.length > 1 && (
              <div className="flex items-center gap-2 mb-6 overflow-x-auto pb-2">
                <span className="text-xs text-white/60 flex items-center gap-1 shrink-0 font-medium">
                  <Filter className="w-3.5 h-3.5 text-amber-400" /> Filter results:
                </span>
                <button
                  type="button"
                  onClick={() => setActiveFilterLang("all")}
                  className={`px-3 py-1 rounded-full text-xs font-semibold transition-all shrink-0 ${
                    activeFilterLang === "all"
                      ? "bg-amber-400 text-slate-950 shadow"
                      : "bg-white/10 text-white/70 hover:bg-white/20"
                  }`}
                >
                  All ({movies.length})
                </button>
                {availableResultLangs.map((l) => {
                  const count = movies.filter(m => m.language_code === l.code).length;
                  return (
                    <button
                      key={l.code}
                      type="button"
                      onClick={() => setActiveFilterLang(l.code)}
                      className={`px-3 py-1 rounded-full text-xs font-semibold transition-all shrink-0 ${
                        activeFilterLang === l.code
                          ? "bg-amber-400 text-slate-950 shadow"
                          : "bg-white/10 text-white/70 hover:bg-white/20"
                      }`}
                    >
                      {l.name} ({count})
                    </button>
                  );
                })}
              </div>
            )}
            
            {/* Movie Cards Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {displayedMovies.map(movie => (
                <MovieCard key={movie.id} movie={movie} />
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
