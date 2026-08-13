import React from 'react';
import { Star, Play, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

export default function MovieCard({ movie }) {
  const posterUrl = movie.poster_path 
    ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
    : 'https://via.placeholder.com/500x750?text=No+Poster';

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ y: -8 }}
      transition={{ duration: 0.2 }}
      onClick={() => window.open(movie.watch_link, '_blank', 'noopener,noreferrer')}
      className="glass-panel rounded-2xl overflow-hidden flex flex-col h-full group cursor-pointer border border-white/10 hover:border-amber-400/50 transition-all duration-300 shadow-xl hover:shadow-2xl hover:shadow-amber-500/10"
    >
      {/* Poster Image Container */}
      <div className="relative aspect-[2/3] overflow-hidden bg-slate-900">
        <img 
          src={posterUrl} 
          alt={movie.title} 
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />
        
        {/* Rating Badge */}
        <div className="absolute top-3 right-3 glass-panel px-2.5 py-1 rounded-lg flex items-center gap-1 font-bold text-xs bg-black/60 backdrop-blur-md border border-white/20 text-white shadow-lg">
          <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
          <span>{movie.rating ? Number(movie.rating).toFixed(1) : "N/A"}</span>
        </div>

        {/* Language Badge */}
        {movie.language_name && (
          <div className="absolute top-3 left-3 px-2.5 py-1 rounded-lg text-xs font-semibold bg-amber-400/90 text-slate-950 backdrop-blur-md shadow-lg border border-amber-300/40">
            {movie.language_name}
          </div>
        )}

        {/* Genre Badges Overlay */}
        {movie.genres && movie.genres.length > 0 && (
          <div className="absolute bottom-3 left-3 right-3 flex gap-1.5 flex-wrap">
            {movie.genres.map((genre, idx) => (
              <span 
                key={idx} 
                className="px-2 py-0.5 rounded-md text-[11px] font-medium bg-black/70 backdrop-blur-md text-white/90 border border-white/15"
              >
                {genre}
              </span>
            ))}
          </div>
        )}
      </div>
      
      {/* Content Container */}
      <div className="p-5 flex-grow flex flex-col justify-between bg-slate-950/40 backdrop-blur-sm">
        <div>
          <div className="flex justify-between items-start mb-2 gap-2">
            <h3 className="text-lg font-bold text-white line-clamp-1 group-hover:text-amber-300 transition-colors">
              {movie.title}
            </h3>
            {movie.release_year && (
              <span className="text-white/60 text-xs font-medium px-2 py-0.5 rounded bg-white/10 whitespace-nowrap">
                {movie.release_year}
              </span>
            )}
          </div>
          
          <p className="text-xs text-white/70 italic mb-4 line-clamp-3 leading-relaxed flex items-start gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-pink-400 shrink-0 mt-0.5" />
            <span>"{movie.ai_reason}"</span>
          </p>
        </div>
        
        {/* Streaming Providers */}
        <div className="pt-3 border-t border-white/10 mt-2">
          {movie.providers && movie.providers.length > 0 ? (
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[11px] text-white/50 uppercase tracking-wider font-semibold">Stream on:</span>
              <div className="flex items-center gap-1.5 flex-wrap">
                {movie.providers.slice(0, 4).map(provider => (
                  <div 
                    key={provider.provider_id} 
                    className="w-7 h-7 rounded-lg overflow-hidden shadow-md border border-white/20" 
                    title={provider.provider_name}
                  >
                    <img 
                      src={`https://image.tmdb.org/t/p/original${provider.logo_path}`} 
                      alt={provider.provider_name} 
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))}
                {movie.providers.length > 4 && (
                  <span className="text-xs text-white/60 font-semibold">+{movie.providers.length - 4}</span>
                )}
              </div>
            </div>
          ) : (
            <div className="text-[11px] text-white/40 italic flex items-center gap-1">
              <Play className="w-3 h-3 text-amber-400" /> Watch options available on TMDB
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
