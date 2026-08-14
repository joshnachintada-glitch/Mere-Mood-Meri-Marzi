import React, { useState } from 'react';
import { Star, Play, Sparkles, Film } from 'lucide-react';

export default function MovieCard({ movie, onGenreClick, activeGenre }) {
  const defaultPoster = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=500&q=80";
  const [imageSrc, setImageSrc] = useState(
    movie.poster_path 
      ? (movie.poster_path.startsWith('http') ? movie.poster_path : `https://image.tmdb.org/t/p/w500${movie.poster_path}`)
      : defaultPoster
  );

  const genres = movie.genres && Array.isArray(movie.genres) ? movie.genres : [];

  return (
    <div 
      onClick={() => window.open(movie.watch_link, '_blank', 'noopener,noreferrer')}
      className="glass-panel rounded-2xl overflow-hidden flex flex-col h-full group cursor-pointer border border-white/10 hover:border-amber-400/60 hover:shadow-2xl hover:shadow-amber-500/10 transition-all duration-300 transform hover:-translate-y-1 relative bg-slate-900/60 backdrop-blur-md"
    >
      {/* Poster Image Container */}
      <div className="relative aspect-[2/3] overflow-hidden bg-slate-950">
        <img 
          src={imageSrc} 
          alt={movie.title} 
          onError={() => setImageSrc(defaultPoster)}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />
        
        {/* Rating Badge */}
        <div className="absolute top-3 right-3 glass-panel px-2.5 py-1 rounded-lg flex items-center gap-1 font-bold text-xs bg-slate-950/80 backdrop-blur-md border border-white/20 text-white shadow-lg z-10">
          <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
          <span>{movie.rating ? Number(movie.rating).toFixed(1) : "N/A"}</span>
        </div>

        {/* Language Badge */}
        {movie.language_name && (
          <div className="absolute top-3 left-3 px-2.5 py-1 rounded-lg text-xs font-bold bg-amber-400 text-slate-950 backdrop-blur-md shadow-lg border border-amber-300/40 z-10">
            {movie.language_name}
          </div>
        )}

        {/* Genre Badges Overlay */}
        {genres.length > 0 && (
          <div className="absolute bottom-3 left-3 right-3 flex gap-1.5 flex-wrap z-10">
            {genres.slice(0, 3).map((genre, idx) => {
              const isCurrent = activeGenre && activeGenre.toLowerCase() === genre.toLowerCase();
              return (
                <button
                  key={idx} 
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (onGenreClick) onGenreClick(genre);
                  }}
                  className={`px-2.5 py-0.5 rounded-md text-[11px] font-semibold transition-all duration-200 backdrop-blur-md border ${
                    isCurrent
                      ? "bg-amber-400 text-slate-950 border-amber-300 shadow-md font-bold"
                      : "bg-black/75 text-white/90 border-white/20 hover:bg-amber-400/90 hover:text-slate-950 hover:border-amber-300"
                  }`}
                  title={`Filter by ${genre}`}
                >
                  {genre}
                </button>
              );
            })}
          </div>
        )}

        {/* Subtle Dark Gradient Overlay at Bottom of Poster */}
        <div className="absolute inset-x-0 bottom-0 h-20 bg-gradient-to-t from-slate-950/90 via-slate-950/40 to-transparent pointer-events-none" />
      </div>
      
      {/* Content Container */}
      <div className="p-5 flex-grow flex flex-col justify-between bg-slate-950/60 backdrop-blur-md border-t border-white/5">
        <div>
          <div className="flex justify-between items-start mb-2 gap-2">
            <h3 className="text-lg font-bold text-white line-clamp-1 group-hover:text-amber-300 transition-colors" title={movie.title}>
              {movie.title}
            </h3>
            {movie.release_year && (
              <span className="text-amber-200/90 text-xs font-semibold px-2 py-0.5 rounded bg-amber-500/15 border border-amber-400/20 whitespace-nowrap">
                {movie.release_year}
              </span>
            )}
          </div>
          
          <p className="text-xs text-white/70 italic mb-4 line-clamp-2 leading-relaxed flex items-start gap-1.5 min-h-[32px]">
            <Sparkles className="w-3.5 h-3.5 text-pink-400 shrink-0 mt-0.5" />
            <span>"{movie.ai_reason}"</span>
          </p>
        </div>
        
        {/* Streaming Providers Section */}
        <div className="pt-3 border-t border-white/10 mt-2">
          {movie.providers && movie.providers.length > 0 ? (
            <div className="flex items-center justify-between gap-2 flex-wrap">
              <span className="text-[11px] text-white/50 uppercase tracking-wider font-bold">Stream on:</span>
              <div className="flex items-center gap-1.5 flex-wrap">
                {movie.providers.slice(0, 4).map(provider => (
                  <div 
                    key={provider.provider_id} 
                    className="w-7 h-7 rounded-lg overflow-hidden shadow-md border border-white/20 hover:scale-110 transition-transform bg-slate-800" 
                    title={provider.provider_name}
                  >
                    <img 
                      src={`https://image.tmdb.org/t/p/original${provider.logo_path}`} 
                      alt={provider.provider_name} 
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                  </div>
                ))}
                {movie.providers.length > 4 && (
                  <span className="text-xs text-amber-300 font-bold bg-amber-500/15 px-1.5 py-0.5 rounded border border-amber-400/20">
                    +{movie.providers.length - 4}
                  </span>
                )}
              </div>
            </div>
          ) : (
            <div className="text-[11px] text-white/50 italic flex items-center justify-between">
              <span className="flex items-center gap-1 text-white/60">
                <Play className="w-3 h-3 text-amber-400" /> Watch Options
              </span>
              <span className="text-[10px] text-amber-400/90 font-medium hover:underline flex items-center gap-0.5">
                View on TMDB &rarr;
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
