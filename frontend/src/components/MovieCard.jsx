import React from 'react';
import { Star, Play } from 'lucide-react';
import { motion } from 'framer-motion';

export default function MovieCard({ movie }) {
  const posterUrl = movie.poster_path 
    ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
    : 'https://via.placeholder.com/500x750?text=No+Poster';

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ y: -10 }}
      onClick={() => window.open(movie.watch_link, '_blank', 'noopener,noreferrer')}
      className="glass-panel rounded-2xl overflow-hidden flex flex-col h-full group cursor-pointer"
    >
      <div className="relative aspect-[2/3] overflow-hidden bg-black/40">
        <img 
          src={posterUrl} 
          alt={movie.title} 
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
        />
        <div className="absolute top-3 right-3 glass-panel px-2 py-1 rounded-lg flex items-center gap-1 font-bold">
          <Star className="w-4 h-4 text-bollywood-yellow fill-bollywood-yellow" />
          <span>{movie.rating.toFixed(1)}</span>
        </div>
      </div>
      
      <div className="p-5 flex-grow flex flex-col">
        <div className="flex justify-between items-start mb-2 gap-2">
          <h3 className="text-xl font-bold line-clamp-1">{movie.title}</h3>
          <span className="text-white/60 text-sm whitespace-nowrap">{movie.release_year}</span>
        </div>
        
        <p className="text-sm text-white/70 italic mb-4 flex-grow line-clamp-3">
          "{movie.ai_reason}"
        </p>
        
        <div className="mt-auto pt-4 border-t border-white/10">
          {movie.providers && movie.providers.length > 0 ? (
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs text-white/50 uppercase tracking-wider">Stream on:</span>
              {movie.providers.slice(0, 3).map(provider => (
                <div key={provider.provider_id} className="w-8 h-8 rounded overflow-hidden shadow-lg" title={provider.provider_name}>
                  <img src={`https://image.tmdb.org/t/p/original${provider.logo_path}`} alt={provider.provider_name} />
                </div>
              ))}
              {movie.providers.length > 3 && (
                <span className="text-xs text-white/50">+{movie.providers.length - 3}</span>
              )}
            </div>
          ) : (
            <div className="text-xs text-white/40 italic flex items-center gap-1">
              <Play className="w-3 h-3" /> No major streaming data found
            </div>
          )}
        </div>

      </div>
    </motion.div>
  );
}
