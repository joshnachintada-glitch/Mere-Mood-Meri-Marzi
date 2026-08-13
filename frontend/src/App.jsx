import React, { useState } from 'react';
import axios from 'axios';
import Navbar from './components/Navbar';
import MoodInput from './components/MoodInput';
import MovieCard from './components/MovieCard';
import { GradientBackground } from '@/components/ui/silk-blend-gradient';

function App() {
  const [movies, setMovies] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [moodAnalysis, setMoodAnalysis] = useState(null);

  const handleSearch = async (mood) => {
    setIsLoading(true);
    setError(null);
    setHasSearched(true);
    setMovies([]);
    
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      const response = await axios.post(`${apiUrl}/api/recommend`, {
        mood: mood,
        region: 'IN'
      });
      
      if (response.data.error) {
        setError(response.data.error);
      } else {
        setMovies(response.data.movies);
        setMoodAnalysis(response.data.mood_analysis);
      }
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.error || err.response?.data?.detail || err.message;
      setError(`Failed to fetch recommendations (${detail}). Ensure backend is running and API keys are set.`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative z-0">
      <GradientBackground className="absolute inset-0 -z-10" />
      <Navbar />
      
      <main className="container mx-auto px-4 pb-20">
        <MoodInput onSearch={handleSearch} isLoading={isLoading} />
        
        {error && (
          <div className="bg-red-500/20 border border-red-500 text-white px-6 py-4 rounded-xl max-w-2xl mx-auto mb-10 backdrop-blur-md">
            <p className="font-bold">Oops! Something went wrong.</p>
            <p className="text-sm opacity-80">{error}</p>
          </div>
        )}

        {hasSearched && !isLoading && movies.length === 0 && !error && (
          <div className="text-center text-white/60 py-10">
            No movies found for this mood. Try something else!
          </div>
        )}

        {movies.length > 0 && (
          <div className="mt-8">
            <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
              <h3 className="text-2xl font-bold">Your Movie Matches</h3>
              {moodAnalysis && (
                <div className="flex gap-2 flex-wrap">
                  <span className="text-sm text-white/80 bg-white/10 px-4 py-2 rounded-full backdrop-blur-sm border border-white/20">
                    AI detected vibes: <span className="font-semibold text-bollywood-yellow">{moodAnalysis.keywords.slice(0, 3).join(", ")}</span>
                  </span>
                  {moodAnalysis.original_language && (
                    <span className="text-sm text-white/80 bg-white/10 px-4 py-2 rounded-full backdrop-blur-sm border border-white/20">
                      Language: <span className="font-semibold text-bollywood-yellow">{moodAnalysis.original_language.toUpperCase()}</span>
                    </span>
                  )}
                </div>
              )}
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {movies.map(movie => (
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
