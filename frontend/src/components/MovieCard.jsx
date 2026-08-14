import React, { useState } from 'react';
import { Star, Play, Sparkles } from 'lucide-react';

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
      className="rounded-2xl overflow-hidden flex flex-col h-full group cursor-pointer border border-blue-950/20 hover:border-blue-950 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 relative bg-transparent backdrop-blur-md"
    >
      {/* Poster Image Container */}
      <div className="relative aspect-[2/3] overflow-hidden bg-slate-900/40">
        <img 
          src={imageSrc} 
          alt={movie.title} 
          onError={() => setImageSrc(defaultPoster)}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />
        
        {/* Rating Badge */}
        <div className="absolute top-3 right-3 px-2.5 py-1 rounded-lg flex items-center gap-1 font-black text-xs bg-transparent backdrop-blur-md border border-blue-950/30 text-blue-950 shadow-sm z-10">
          <Star className="w-3.5 h-3.5 text-blue-950 fill-blue-950" />
          <span>{movie.rating ? Number(movie.rating).toFixed(1) : "N/A"}</span>
        </div>

        {/* Language Badge */}
        {movie.language_name && (
          <div className="absolute top-3 left-3 px-2.5 py-1 rounded-lg text-xs font-black bg-transparent text-blue-950 backdrop-blur-md shadow-sm border border-blue-950/30 z-10">
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
                  className={`px-2.5 py-0.5 rounded-md text-[11px] font-bold transition-all duration-200 backdrop-blur-md border ${
                    isCurrent
                      ? "bg-blue-950/20 text-blue-950 border-2 border-blue-950 shadow-sm font-black"
                      : "bg-transparent text-blue-950 border-blue-950/40 hover:bg-blue-950/10 hover:border-blue-950"
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
        <div className="absolute inset-x-0 bottom-0 h-20 bg-gradient-to-t from-slate-900/60 via-slate-900/20 to-transparent pointer-events-none" />
      </div>
      
      {/* Content Container */}
      <div className="p-5 flex-grow flex flex-col justify-between bg-transparent backdrop-blur-md border-t border-blue-950/10">
        <div>
          <div className="flex justify-between items-start mb-2 gap-2">
            <h3 className="text-lg font-black text-blue-950 line-clamp-1 group-hover:text-blue-900 transition-colors" title={movie.title}>
              {movie.title}
            </h3>
            {movie.release_year && (
              <span className="text-blue-950 text-xs font-bold px-2 py-0.5 rounded bg-transparent border border-blue-950/25 whitespace-nowrap">
                {movie.release_year}
              </span>
            )}
          </div>
          
          <p className="text-xs text-blue-950/80 italic mb-4 line-clamp-2 leading-relaxed flex items-start gap-1.5 min-h-[32px] font-medium">
            <Sparkles className="w-3.5 h-3.5 text-blue-950 shrink-0 mt-0.5" />
            <span>"{movie.ai_reason}"</span>
          </p>
        </div>
        
        {/* Streaming Providers Section */}
        <div className="pt-3 border-t border-blue-950/10 mt-2">
          {movie.providers && movie.providers.length > 0 ? (
            <div className="flex items-center justify-between gap-2 flex-wrap">
              <span className="text-[11px] text-blue-950/60 uppercase tracking-wider font-black">Stream on:</span>
              <div className="flex items-center gap-1.5 flex-wrap">
                {movie.providers.slice(0, 4).map(provider => (
                  <div 
                    key={provider.provider_id} 
                    className="w-7 h-7 rounded-lg overflow-hidden shadow-sm border border-blue-950/25 hover:scale-110 transition-transform bg-transparent" 
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
                  <span className="text-xs text-blue-950 font-black bg-transparent px-1.5 py-0.5 rounded border border-blue-950/25">
                    +{movie.providers.length - 4}
                  </span>
                )}
              </div>
            </div>
          ) : (
            <div className="text-[11px] text-blue-950/70 italic flex items-center justify-between font-medium">
              <span className="flex items-center gap-1 text-blue-950">
                <Play className="w-3 h-3 text-blue-950" /> Watch Options
              </span>
              <span className="text-[10px] text-blue-950 font-bold hover:underline flex items-center gap-0.5">
                View on TMDB &rarr;
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
