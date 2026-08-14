import React, { useState, useRef, useMemo } from 'react';
import axios from 'axios';
import Navbar from './components/Navbar';
import MoodInput from './components/MoodInput';
import MovieCard from './components/MovieCard';
import { GradientBackground } from '@/components/ui/silk-blend-gradient';
import { 
  Film, 
  Sparkles, 
  Filter, 
  LayoutGrid, 
  Layers, 
  ArrowUpDown, 
  RotateCcw,
  Flame,
  Laugh,
  Tv,
  Star,
  Calendar,
  Compass
} from 'lucide-react';

const GENRE_DISPLAY_CONFIG = {
  "Action": { label: "Action & High Octane", color: "from-amber-500/20 to-red-500/10 text-amber-300 border-amber-500/30" },
  "Adventure": { label: "Adventure & Journeys", color: "from-emerald-500/20 to-teal-500/10 text-emerald-300 border-emerald-500/30" },
  "Comedy": { label: "Comedy & Laughs", color: "from-yellow-500/20 to-amber-500/10 text-yellow-300 border-yellow-500/30" },
  "Drama": { label: "Drama & Emotional Stories", color: "from-blue-500/20 to-indigo-500/10 text-blue-300 border-blue-500/30" },
  "Thriller": { label: "Thriller & Suspense", color: "from-purple-500/20 to-pink-500/10 text-purple-300 border-purple-500/30" },
  "Mystery": { label: "Mystery & Investigation", color: "from-violet-500/20 to-fuchsia-500/10 text-violet-300 border-violet-500/30" },
  "Romance": { label: "Romance & Love", color: "from-pink-500/20 to-rose-500/10 text-pink-300 border-pink-500/30" },
  "Sci-Fi": { label: "Sci-Fi & Future", color: "from-cyan-500/20 to-blue-500/10 text-cyan-300 border-cyan-500/30" },
  "Fantasy": { label: "Fantasy & Magic", color: "from-amber-400/20 to-orange-500/10 text-amber-300 border-amber-400/30" },
  "Horror": { label: "Horror & Spooky", color: "from-rose-600/20 to-slate-900/40 text-rose-300 border-rose-500/30" },
  "Crime": { label: "Crime & Underworld", color: "from-zinc-500/20 to-slate-800/40 text-zinc-300 border-zinc-500/30" },
  "Animation": { label: "Anime & Animation", color: "from-indigo-500/20 to-pink-500/10 text-indigo-300 border-indigo-500/30" },
  "Family": { label: "Family & Wholesome", color: "from-teal-500/20 to-emerald-500/10 text-teal-300 border-teal-500/30" },
  "History": { label: "History & Biopic", color: "from-amber-600/20 to-yellow-600/10 text-amber-200 border-amber-600/30" },
  "Music": { label: "Music & Musical", color: "from-fuchsia-500/20 to-purple-500/10 text-fuchsia-300 border-fuchsia-500/30" },
  "War": { label: "War & Epic Combat", color: "from-red-600/20 to-orange-600/10 text-red-300 border-red-500/30" },
};

function App() {
  const [movies, setMovies] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [moodAnalysis, setMoodAnalysis] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState("all");
  
  // Arrangement & Filtering States
  const [activeFilterLang, setActiveFilterLang] = useState("all");
  const [activeFilterGenre, setActiveFilterGenre] = useState("all");
  const [sortBy, setSortBy] = useState("relevance");
  const [viewMode, setViewMode] = useState("grid"); // "grid" | "grouped"
  
  const resultsRef = useRef(null);

  const handleSearch = async (mood, language = selectedLanguage) => {
    setIsLoading(true);
    setError(null);
    setHasSearched(true);
    setActiveFilterLang("all");
    setActiveFilterGenre("all");
    
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      const response = await axios.post(`${apiUrl}/api/recommend`, {
        mood: mood,
        region: 'IN',
        language: language === 'all' ? null : language
      }, {
        timeout: 20000
      });
      
      if (response.data.error) {
        setError(response.data.error);
      } else {
        setMovies(response.data.movies || []);
        setMoodAnalysis(response.data.mood_analysis || null);
        if (resultsRef.current) {
          resultsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.error || err.response?.data?.detail || err.message;
      setError(`Failed to fetch recommendations (${detail}). Ensure backend is running and API keys are set.`);
    } finally {
      setIsLoading(false);
    }
  };

  // Compute available languages in current results with counts
  const availableResultLangs = useMemo(() => {
    const map = new Map();
    movies.forEach(m => {
      if (m.language_code) {
        const existing = map.get(m.language_code);
        if (existing) {
          existing.count += 1;
        } else {
          map.set(m.language_code, {
            code: m.language_code,
            name: m.language_name || m.language_code.toUpperCase(),
            count: 1
          });
        }
      }
    });
    return Array.from(map.values()).sort((a, b) => b.count - a.count);
  }, [movies]);

  // Compute available genres in current results with counts
  const availableResultGenres = useMemo(() => {
    const map = new Map();
    movies.forEach(m => {
      (m.genres || []).forEach(g => {
        if (g) {
          map.set(g, (map.get(g) || 0) + 1);
        }
      });
    });
    return Array.from(map.entries())
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count);
  }, [movies]);

  // Filter & Sort pipeline
  const processedMovies = useMemo(() => {
    let list = [...movies];

    // 1. Language Filter
    if (activeFilterLang !== "all") {
      list = list.filter(m => m.language_code === activeFilterLang);
    }

    // 2. Genre Filter
    if (activeFilterGenre !== "all") {
      list = list.filter(m => 
        (m.genres || []).some(g => g.toLowerCase() === activeFilterGenre.toLowerCase())
      );
    }

    // 3. Sorting
    if (sortBy === "rating") {
      list.sort((a, b) => (Number(b.rating) || 0) - (Number(a.rating) || 0));
    } else if (sortBy === "year_desc") {
      list.sort((a, b) => (parseInt(b.release_year) || 0) - (parseInt(a.release_year) || 0));
    } else if (sortBy === "year_asc") {
      list.sort((a, b) => (parseInt(a.release_year) || 0) - (parseInt(b.release_year) || 0));
    } else if (sortBy === "ott_first") {
      list.sort((a, b) => {
        const aCount = (a.providers && a.providers.length > 0) ? 1 : 0;
        const bCount = (b.providers && b.providers.length > 0) ? 1 : 0;
        if (bCount !== aCount) return bCount - aCount;
        return (Number(b.rating) || 0) - (Number(a.rating) || 0);
      });
    } else if (sortBy === "title") {
      list.sort((a, b) => (a.title || "").localeCompare(b.title || ""));
    }
    // "relevance" preserves backend AI ranked order

    return list;
  }, [movies, activeFilterLang, activeFilterGenre, sortBy]);

  // Grouped by primary genre for "Group by Genre" view mode
  const genreGroups = useMemo(() => {
    if (viewMode !== "grouped") return [];
    
    const groups = new Map();
    processedMovies.forEach(movie => {
      const primaryGenre = (movie.genres && movie.genres.length > 0) ? movie.genres[0] : "Other Cinema";
      if (!groups.has(primaryGenre)) {
        groups.set(primaryGenre, []);
      }
      groups.get(primaryGenre).push(movie);
    });

    return Array.from(groups.entries()).map(([genreName, items]) => ({
      name: genreName,
      config: GENRE_DISPLAY_CONFIG[genreName] || { icon: "🎬", label: `${genreName} Masterpieces`, color: "from-slate-800 to-slate-900 text-white border-white/20" },
      movies: items
    }));
  }, [processedMovies, viewMode]);

  const handleResetFilters = () => {
    setActiveFilterLang("all");
    setActiveFilterGenre("all");
    setSortBy("relevance");
  };

  const hasActiveFilters = activeFilterLang !== "all" || activeFilterGenre !== "all" || sortBy !== "relevance";

  return (
    <div className="min-h-screen relative z-0 text-slate-100 selection:bg-amber-400 selection:text-slate-950 font-sans">
      <GradientBackground className="absolute inset-0 -z-10" />
      <Navbar />
      
      <main className="container mx-auto px-4 sm:px-6 pb-24">
        {/* Mood Input & Header Section */}
        <MoodInput 
          onSearch={handleSearch} 
          isLoading={isLoading} 
          selectedLanguage={selectedLanguage}
          setSelectedLanguage={setSelectedLanguage}
        />
        
        {/* Results Section */}
        <div ref={resultsRef} className="mt-6 scroll-mt-20">

          {/* Loading Indicator / Skeletons */}
          {isLoading && (
            <div className="py-12 text-center">
              <div className="inline-flex items-center gap-3 px-6 py-3 rounded-2xl bg-slate-900/90 border border-amber-400/30 backdrop-blur-xl shadow-2xl mb-8">
                <Sparkles className="w-5 h-5 text-amber-400 animate-spin" />
                <span className="text-base font-bold text-amber-300">Arranging movies to match your mood...</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 max-w-7xl mx-auto">
                {[...Array(8)].map((_, i) => (
                  <div key={i} className="glass-panel rounded-2xl overflow-hidden animate-pulse flex flex-col h-[420px] bg-slate-900/40 border border-white/10">
                    <div className="aspect-[2/3] bg-slate-800/80 w-full" />
                    <div className="p-4 flex-1 flex flex-col justify-between">
                      <div className="space-y-2">
                        <div className="h-4 bg-slate-700/60 rounded w-3/4" />
                        <div className="h-3 bg-slate-800/60 rounded w-1/2" />
                      </div>
                      <div className="h-6 bg-slate-800/60 rounded w-full" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Error Banner */}
          {error && !isLoading && (
            <div className="bg-red-500/20 border border-red-500/50 text-white px-6 py-5 rounded-2xl max-w-2xl mx-auto mb-10 backdrop-blur-xl shadow-2xl">
              <p className="font-bold text-red-200 text-base">Oops! Something went wrong.</p>
              <p className="text-sm opacity-80 mt-1">{error}</p>
            </div>
          )}

          {/* Empty Results Banner */}
          {hasSearched && !isLoading && movies.length === 0 && !error && (
            <div className="text-center text-white/70 py-16 max-w-lg mx-auto bg-slate-950/60 rounded-3xl border border-white/10 backdrop-blur-xl shadow-2xl px-6">
              <Film className="w-12 h-12 mx-auto mb-3 text-amber-400/60" />
              <p className="text-xl font-bold text-white">No movies found for this query.</p>
              <p className="text-sm text-white/60 mt-1">Try choosing "All Languages" or click one of the genre mood presets above!</p>
            </div>
          )}

          {/* Render Movie Results */}
          {!isLoading && movies.length > 0 && (
            <div className="max-w-7xl mx-auto space-y-6">
              
              {/* Header & Vibes Analysis Card */}
              <div className="bg-slate-950/70 p-6 rounded-3xl border border-white/15 backdrop-blur-xl shadow-2xl">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-0.5 rounded-full bg-amber-400/20 border border-amber-400/40 text-amber-300 text-xs font-bold uppercase tracking-wider">
                        {movies.length} Masterpieces Arranged
                      </span>
                      {selectedLanguage !== "all" && (
                        <span className="px-2.5 py-0.5 rounded-full bg-blue-500/20 border border-blue-400/30 text-blue-300 text-xs font-semibold">
                          {selectedLanguage.toUpperCase()}
                        </span>
                      )}
                    </div>

                    <h3 className="text-2xl sm:text-3xl font-black text-white mt-1.5 flex items-center gap-2.5">
                      <Film className="w-7 h-7 text-amber-400 shrink-0" />
                      Curated Movie Matches
                    </h3>

                    {moodAnalysis?.tone_summary && (
                      <p className="text-sm sm:text-base text-white/80 mt-1.5 flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-pink-400 shrink-0" />
                        <span>{moodAnalysis.tone_summary}</span>
                      </p>
                    )}
                  </div>

                  {/* Vibes / Keywords Badges */}
                  {moodAnalysis?.keywords && moodAnalysis.keywords.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 items-center md:max-w-md md:justify-end">
                      <span className="text-xs text-white/50 font-bold uppercase tracking-wider mr-1">Vibes:</span>
                      {moodAnalysis.keywords.map((kw, i) => (
                        <span 
                          key={i} 
                          className="text-xs text-amber-300 bg-amber-500/15 px-3 py-1 rounded-full border border-amber-400/30 font-semibold shadow-sm"
                        >
                          #{kw}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Controls Bar: View Switcher & Sorting */}
                <div className="mt-6 pt-5 border-t border-white/10 flex flex-wrap items-center justify-between gap-4">
                  
                  {/* Left: View Mode Toggles */}
                  <div className="flex items-center gap-2 bg-slate-900/80 p-1 rounded-xl border border-white/15">
                    <button
                      type="button"
                      onClick={() => setViewMode("grid")}
                      className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                        viewMode === "grid"
                          ? "bg-amber-400 text-slate-950 shadow-md font-extrabold"
                          : "text-white/70 hover:text-white hover:bg-white/10"
                      }`}
                    >
                      <LayoutGrid className="w-3.5 h-3.5" />
                      <span>Grid View</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setViewMode("grouped")}
                      className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                        viewMode === "grouped"
                          ? "bg-amber-400 text-slate-950 shadow-md font-extrabold"
                          : "text-white/70 hover:text-white hover:bg-white/10"
                      }`}
                    >
                      <Layers className="w-3.5 h-3.5" />
                      <span>Group by Genre</span>
                    </button>
                  </div>

                  {/* Right: Sort Selector & Reset */}
                  <div className="flex items-center gap-3 flex-wrap">
                    <div className="flex items-center gap-2 bg-slate-900/80 px-3 py-1.5 rounded-xl border border-white/15">
                      <ArrowUpDown className="w-3.5 h-3.5 text-amber-400" />
                      <span className="text-xs text-white/50 font-semibold uppercase tracking-wider">Sort:</span>
                      <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                        className="bg-transparent text-xs font-bold text-amber-300 outline-none cursor-pointer pr-2"
                      >
                        <option value="relevance" className="bg-slate-950 text-white">AI Curated Match</option>
                        <option value="rating" className="bg-slate-950 text-white">Highest Rating</option>
                        <option value="year_desc" className="bg-slate-950 text-white">Newest Releases</option>
                        <option value="year_asc" className="bg-slate-950 text-white">Classic First</option>
                        <option value="ott_first" className="bg-slate-950 text-white">Streaming Available First</option>
                        <option value="title" className="bg-slate-950 text-white">Title (A → Z)</option>
                      </select>
                    </div>

                    {hasActiveFilters && (
                      <button
                        type="button"
                        onClick={handleResetFilters}
                        className="flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-bold bg-white/10 hover:bg-red-500/20 text-white/80 hover:text-red-300 border border-white/15 hover:border-red-400/40 transition-all cursor-pointer"
                        title="Reset all applied filters"
                      >
                        <RotateCcw className="w-3 h-3" />
                        <span>Reset Filters</span>
                      </button>
                    )}
                  </div>
                </div>

                {/* Filter Row 1: Languages in Results */}
                {availableResultLangs.length > 1 && (
                  <div className="mt-4 pt-4 border-t border-white/10 flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
                    <span className="text-xs text-white/50 flex items-center gap-1 shrink-0 font-bold uppercase tracking-wider">
                      <Filter className="w-3 h-3 text-amber-400" /> Industry:
                    </span>
                    <button
                      type="button"
                      onClick={() => setActiveFilterLang("all")}
                      className={`px-3 py-1 rounded-full text-xs font-bold transition-all shrink-0 cursor-pointer ${
                        activeFilterLang === "all"
                          ? "bg-amber-400 text-slate-950 shadow-md font-extrabold"
                          : "bg-white/10 text-white/70 hover:bg-white/20 border border-white/10"
                      }`}
                    >
                      All ({movies.length})
                    </button>
                    {availableResultLangs.map((l) => (
                      <button
                        key={l.code}
                        type="button"
                        onClick={() => setActiveFilterLang(l.code)}
                        className={`px-3 py-1 rounded-full text-xs font-bold transition-all shrink-0 cursor-pointer flex items-center gap-1.5 ${
                          activeFilterLang === l.code
                            ? "bg-amber-400 text-slate-950 shadow-md font-extrabold"
                            : "bg-white/10 text-white/70 hover:bg-white/20 border border-white/10"
                        }`}
                      >
                        <span>{l.name}</span>
                        <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${activeFilterLang === l.code ? 'bg-slate-950 text-amber-300' : 'bg-white/10 text-white/60'}`}>
                          {l.count}
                        </span>
                      </button>
                    ))}
                  </div>
                )}

                {/* Filter Row 2: Genres in Results */}
                {availableResultGenres.length > 1 && (
                  <div className="mt-3 flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
                    <span className="text-xs text-white/50 flex items-center gap-1 shrink-0 font-bold uppercase tracking-wider">
                      <Film className="w-3 h-3 text-amber-400" /> Genre:
                    </span>
                    <button
                      type="button"
                      onClick={() => setActiveFilterGenre("all")}
                      className={`px-3 py-1 rounded-full text-xs font-bold transition-all shrink-0 cursor-pointer ${
                        activeFilterGenre === "all"
                          ? "bg-amber-400 text-slate-950 shadow-md font-extrabold"
                          : "bg-white/10 text-white/70 hover:bg-white/20 border border-white/10"
                      }`}
                    >
                      All Genres
                    </button>
                    {availableResultGenres.map((g) => {
                      const isCurrent = activeFilterGenre.toLowerCase() === g.name.toLowerCase();
                      return (
                        <button
                          key={g.name}
                          type="button"
                          onClick={() => setActiveFilterGenre(isCurrent ? "all" : g.name)}
                          className={`px-3 py-1 rounded-full text-xs font-bold transition-all shrink-0 cursor-pointer flex items-center gap-1.5 ${
                            isCurrent
                              ? "bg-amber-400 text-slate-950 shadow-md font-extrabold"
                              : "bg-white/10 text-white/70 hover:bg-white/20 border border-white/10"
                          }`}
                        >
                          <span>{g.name}</span>
                          <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${isCurrent ? 'bg-slate-950 text-amber-300' : 'bg-white/10 text-white/60'}`}>
                            {g.count}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Filter Notice when 0 matches for active filters */}
              {processedMovies.length === 0 && (
                <div className="text-center text-white/70 py-16 max-w-md mx-auto bg-slate-950/60 rounded-3xl border border-white/10 backdrop-blur-xl px-6">
                  <Film className="w-10 h-10 mx-auto mb-3 text-amber-400/50" />
                  <p className="text-lg font-bold text-white">No movies match the selected filters.</p>
                  <p className="text-xs text-white/60 mt-1 mb-4">Try resetting language or genre filters to see all results.</p>
                  <button
                    type="button"
                    onClick={handleResetFilters}
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-amber-400 text-slate-950 hover:bg-amber-300 shadow-md transition-all cursor-pointer"
                  >
                    Reset All Filters
                  </button>
                </div>
              )}

              {/* View 1: Standard 4-Column Grid View */}
              {viewMode === "grid" && processedMovies.length > 0 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {processedMovies.map(movie => (
                    <MovieCard 
                      key={movie.id} 
                      movie={movie} 
                      onGenreClick={(g) => setActiveFilterGenre(g)}
                      activeGenre={activeFilterGenre}
                    />
                  ))}
                </div>
              )}

              {/* View 2: Grouped by Genre View */}
              {viewMode === "grouped" && processedMovies.length > 0 && (
                <div className="space-y-10">
                  {genreGroups.map((group) => (
                    <section key={group.name} className="space-y-4">
                      {/* Section Header */}
                      <div className="flex items-center justify-between bg-slate-950/50 px-5 py-3 rounded-2xl border border-white/10 backdrop-blur-md">
                        <div className="flex items-center gap-3">
                          <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
                            <Film className="w-5 h-5" />
                          </div>
                          <div>
                            <h4 className="text-lg sm:text-xl font-black text-white">{group.config.label}</h4>
                            <p className="text-xs text-white/60">Curated recommendations matching this genre</p>
                          </div>
                        </div>
                        <span className="px-3 py-1 rounded-full bg-amber-500/15 border border-amber-400/30 text-amber-300 text-xs font-extrabold">
                          {group.movies.length} {group.movies.length === 1 ? "Movie" : "Movies"}
                        </span>
                      </div>

                      {/* Genre Subgrid */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {group.movies.map(movie => (
                          <MovieCard 
                            key={movie.id} 
                            movie={movie} 
                            onGenreClick={(g) => setActiveFilterGenre(g)}
                            activeGenre={activeFilterGenre}
                          />
                        ))}
                      </div>
                    </section>
                  ))}
                </div>
              )}

            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
