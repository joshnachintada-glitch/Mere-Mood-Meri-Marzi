import React, { useRef, useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Layers } from 'lucide-react';
import { motion } from 'framer-motion';

export const CAROUSEL_GENRES = [
  {
    id: "action",
    name: "Action",
    tagline: "High Octane",
    prompt: "Action movies with intense thrill and high energy",
    accent: "text-amber-400 border-amber-500/30 hover:border-amber-400",
    dot: "bg-amber-400"
  },
  {
    id: "thriller",
    name: "Thriller",
    tagline: "Suspense",
    prompt: "Gripping thriller, suspense and mystery movies",
    accent: "text-purple-400 border-purple-500/30 hover:border-purple-400",
    dot: "bg-purple-400"
  },
  {
    id: "crime",
    name: "Crime",
    tagline: "Underworld",
    prompt: "Intense crime, underworld, and mafia sagas",
    accent: "text-zinc-300 border-zinc-500/30 hover:border-zinc-300",
    dot: "bg-zinc-300"
  },
  {
    id: "adventure",
    name: "Adventure",
    tagline: "Expedition",
    prompt: "Epic adventure, exploration, and journey movies",
    accent: "text-emerald-400 border-emerald-500/30 hover:border-emerald-400",
    dot: "bg-emerald-400"
  },
  {
    id: "war",
    name: "War",
    tagline: "Battlefield",
    prompt: "Gripping war dramas, heroic bravery, and epic combat sagas",
    accent: "text-red-400 border-red-500/30 hover:border-red-400",
    dot: "bg-red-400"
  },
  {
    id: "comedy",
    name: "Comedy",
    tagline: "Feel-Good",
    prompt: "Hilarious comedy movies with feel-good laughter",
    accent: "text-yellow-400 border-yellow-500/30 hover:border-yellow-400",
    dot: "bg-yellow-400"
  },
  {
    id: "romance",
    name: "Romance",
    tagline: "Love Story",
    prompt: "Heartwarming romantic love story movies",
    accent: "text-pink-400 border-pink-500/30 hover:border-pink-400",
    dot: "bg-pink-400"
  },
  {
    id: "family",
    name: "Family",
    tagline: "Wholesome",
    prompt: "Wholesome, magical family movies for all ages",
    accent: "text-teal-400 border-teal-500/30 hover:border-teal-400",
    dot: "bg-teal-400"
  },
  {
    id: "musical",
    name: "Musical",
    tagline: "Soundtrack",
    prompt: "Melodious musical spectacles, rhythmic songs, and dance",
    accent: "text-fuchsia-400 border-fuchsia-500/30 hover:border-fuchsia-400",
    dot: "bg-fuchsia-400"
  },
  {
    id: "scifi",
    name: "Sci-Fi",
    tagline: "Futuristic",
    prompt: "Futuristic science fiction and mind-bending Sci-Fi movies",
    accent: "text-cyan-400 border-cyan-500/30 hover:border-cyan-400",
    dot: "bg-cyan-400"
  },
  {
    id: "fantasy",
    name: "Fantasy",
    tagline: "Mythical",
    prompt: "Magical fantasy and mythical adventure movies",
    accent: "text-amber-300 border-amber-400/30 hover:border-amber-300",
    dot: "bg-amber-300"
  },
  {
    id: "horror",
    name: "Horror",
    tagline: "Chills",
    prompt: "Chilling and scary horror movies",
    accent: "text-rose-400 border-rose-600/30 hover:border-rose-500",
    dot: "bg-rose-400"
  },
  {
    id: "mystery",
    name: "Mystery",
    tagline: "Whodunit",
    prompt: "Intriguing mysteries, suspenseful investigations, and clever detective puzzles",
    accent: "text-violet-400 border-violet-500/30 hover:border-violet-400",
    dot: "bg-violet-400"
  },
  {
    id: "drama",
    name: "Drama",
    tagline: "Emotional",
    prompt: "Emotional and powerful drama movies",
    accent: "text-blue-400 border-blue-500/30 hover:border-blue-400",
    dot: "bg-blue-400"
  },
  {
    id: "history",
    name: "History",
    tagline: "Period Epic",
    prompt: "Magnificent historical epics and monumental biographical stories",
    accent: "text-amber-300 border-amber-600/30 hover:border-amber-500",
    dot: "bg-amber-300"
  }
];

export default function GenreCarousel({ onSelectGenre, selectedGenreId, isLoading }) {
  const scrollRef = useRef(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);
  const [isPaused, setIsPaused] = useState(false);

  const checkScrollability = () => {
    if (scrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
      setCanScrollLeft(scrollLeft > 10);
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10);
    }
  };

  useEffect(() => {
    checkScrollability();
    const current = scrollRef.current;
    if (current) {
      current.addEventListener('scroll', checkScrollability);
      window.addEventListener('resize', checkScrollability);
      return () => {
        current.removeEventListener('scroll', checkScrollability);
        window.removeEventListener('resize', checkScrollability);
      };
    }
  }, []);

  // Auto-scroll loop effect
  useEffect(() => {
    if (isPaused || isLoading) return;

    const interval = setInterval(() => {
      if (scrollRef.current) {
        const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
        const maxScroll = scrollWidth - clientWidth;

        // When reaching the end, smooth loop back to start
        if (scrollLeft >= maxScroll - 10) {
          scrollRef.current.scrollTo({ left: 0, behavior: 'smooth' });
        } else {
          // Advance smoothly by ~130px (one pill width)
          scrollRef.current.scrollBy({ left: 130, behavior: 'smooth' });
        }
      }
    }, 2200);

    return () => clearInterval(interval);
  }, [isPaused, isLoading]);

  const handleScroll = (direction) => {
    if (scrollRef.current) {
      const scrollAmount = direction === 'left' ? -220 : 220;
      scrollRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
  };

  return (
    <div 
      className="w-full relative mb-5"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
      onTouchStart={() => setIsPaused(true)}
      onTouchEnd={() => setIsPaused(false)}
    >
      {/* Sleek Minimal Header */}
      <div className="flex items-center justify-between mb-2 px-1">
        <div className="flex items-center gap-1.5">
          <Layers className="w-3 h-3 text-amber-400" />
          <span className="text-[11px] font-bold text-white/80 uppercase tracking-wider">
            Genres
          </span>
          <span className="text-[9px] font-semibold px-1.5 py-0.2 rounded-full bg-white/10 text-white/50">
            15
          </span>
        </div>

        {/* Carousel Arrow Controls */}
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => handleScroll('left')}
            disabled={!canScrollLeft || isLoading}
            aria-label="Scroll genres left"
            className={`p-1 rounded-md border backdrop-blur-md transition-all duration-150 cursor-pointer ${
              canScrollLeft
                ? "bg-slate-900/90 hover:bg-slate-800 text-white border-white/20 hover:border-amber-400/50"
                : "bg-slate-950/40 text-white/20 border-white/5 cursor-not-allowed"
            }`}
          >
            <ChevronLeft className="w-3 h-3" />
          </button>
          <button
            type="button"
            onClick={() => handleScroll('right')}
            disabled={!canScrollRight || isLoading}
            aria-label="Scroll genres right"
            className={`p-1 rounded-md border backdrop-blur-md transition-all duration-150 cursor-pointer ${
              canScrollRight
                ? "bg-slate-900/90 hover:bg-slate-800 text-white border-white/20 hover:border-amber-400/50"
                : "bg-slate-950/40 text-white/20 border-white/5 cursor-not-allowed"
            }`}
          >
            <ChevronRight className="w-3 h-3" />
          </button>
        </div>
      </div>

      {/* Carousel Track Container */}
      <div className="relative">
        {/* Left Fade Gradient */}
        {canScrollLeft && (
          <div className="absolute left-0 top-0 bottom-0 w-6 bg-gradient-to-r from-slate-950 to-transparent z-10 pointer-events-none rounded-l-lg" />
        )}
        
        {/* Right Fade Gradient */}
        {canScrollRight && (
          <div className="absolute right-0 top-0 bottom-0 w-6 bg-gradient-to-l from-slate-950 to-transparent z-10 pointer-events-none rounded-r-lg" />
        )}

        {/* Scrollable Compact Pills/Cards */}
        <div
          ref={scrollRef}
          className="flex items-center gap-1.5 overflow-x-auto scrollbar-none py-1 px-0.5 scroll-smooth snap-x"
          style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
          {CAROUSEL_GENRES.map((genre) => {
            const isSelected = selectedGenreId === genre.id;
            return (
              <motion.button
                key={genre.id}
                type="button"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => onSelectGenre(genre)}
                disabled={isLoading}
                className={`snap-start shrink-0 flex items-center gap-1.5 px-2.5 py-1 rounded-lg border backdrop-blur-md transition-all duration-150 cursor-pointer ${
                  isSelected
                    ? "bg-amber-400 text-slate-950 font-bold border-amber-300 shadow-sm shadow-amber-400/20"
                    : `bg-slate-950/90 hover:bg-slate-900 text-white/90 ${genre.accent}`
                }`}
              >
                <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${isSelected ? 'bg-slate-950' : genre.dot}`} />
                <span className="text-[11px] font-semibold whitespace-nowrap">{genre.name}</span>
                <span className={`text-[9px] whitespace-nowrap ${isSelected ? 'text-slate-800 font-medium' : 'text-white/40'}`}>
                  {genre.tagline}
                </span>
              </motion.button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
