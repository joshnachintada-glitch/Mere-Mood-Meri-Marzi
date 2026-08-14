import React, { useRef, useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

export const CAROUSEL_GENRES = [
  {
    id: "action",
    name: "Action",
    icon: "🔥",
    tagline: "High Octane & Combat",
    prompt: "Action movies with intense thrill and high energy",
    gradient: "from-amber-500/20 via-orange-600/15 to-red-600/10",
    border: "border-amber-500/30 hover:border-amber-400",
    activeBorder: "border-amber-400 ring-2 ring-amber-400/40",
    accentColor: "text-amber-400"
  },
  {
    id: "thriller",
    name: "Thriller",
    icon: "🔍",
    tagline: "Edge of Seat Suspense",
    prompt: "Gripping thriller, suspense and mystery movies",
    gradient: "from-purple-500/20 via-violet-600/15 to-pink-600/10",
    border: "border-purple-500/30 hover:border-purple-400",
    activeBorder: "border-purple-400 ring-2 ring-purple-400/40",
    accentColor: "text-purple-400"
  },
  {
    id: "crime",
    name: "Crime",
    icon: "🕵️",
    tagline: "Mafia & Underworld",
    prompt: "Intense crime, underworld, and mafia sagas",
    gradient: "from-zinc-500/20 via-slate-700/15 to-red-900/10",
    border: "border-zinc-500/30 hover:border-zinc-300",
    activeBorder: "border-zinc-300 ring-2 ring-zinc-300/40",
    accentColor: "text-zinc-300"
  },
  {
    id: "adventure",
    name: "Adventure",
    icon: "🗺️",
    tagline: "Epic Quests & Journeys",
    prompt: "Epic adventure, exploration, and journey movies",
    gradient: "from-emerald-500/20 via-teal-600/15 to-cyan-600/10",
    border: "border-emerald-500/30 hover:border-emerald-400",
    activeBorder: "border-emerald-400 ring-2 ring-emerald-400/40",
    accentColor: "text-emerald-400"
  },
  {
    id: "war",
    name: "War",
    icon: "⚔️",
    tagline: "Battlefield & Heroism",
    prompt: "Gripping war dramas, heroic bravery, and epic combat sagas",
    gradient: "from-red-600/20 via-orange-700/15 to-amber-900/10",
    border: "border-red-500/30 hover:border-red-400",
    activeBorder: "border-red-400 ring-2 ring-red-400/40",
    accentColor: "text-red-400"
  },
  {
    id: "comedy",
    name: "Comedy",
    icon: "😂",
    tagline: "Laughs & Feel-Good Fun",
    prompt: "Hilarious comedy movies with feel-good laughter",
    gradient: "from-yellow-500/20 via-amber-500/15 to-orange-500/10",
    border: "border-yellow-500/30 hover:border-yellow-400",
    activeBorder: "border-yellow-400 ring-2 ring-yellow-400/40",
    accentColor: "text-yellow-400"
  },
  {
    id: "romance",
    name: "Romance",
    icon: "❤️",
    tagline: "Love & Heartwarming",
    prompt: "Heartwarming romantic love story movies",
    gradient: "from-pink-500/20 via-rose-600/15 to-red-500/10",
    border: "border-pink-500/30 hover:border-pink-400",
    activeBorder: "border-pink-400 ring-2 ring-pink-400/40",
    accentColor: "text-pink-400"
  },
  {
    id: "family",
    name: "Family",
    icon: "👨‍👩‍👧",
    tagline: "Wholesome & Magical",
    prompt: "Wholesome, magical family movies for all ages",
    gradient: "from-teal-500/20 via-emerald-600/15 to-sky-600/10",
    border: "border-teal-500/30 hover:border-teal-400",
    activeBorder: "border-teal-400 ring-2 ring-teal-400/40",
    accentColor: "text-teal-400"
  },
  {
    id: "musical",
    name: "Musical",
    icon: "🎵",
    tagline: "Rhythm, Songs & Dance",
    prompt: "Melodious musical spectacles, rhythmic songs, and dance",
    gradient: "from-fuchsia-500/20 via-purple-600/15 to-indigo-600/10",
    border: "border-fuchsia-500/30 hover:border-fuchsia-400",
    activeBorder: "border-fuchsia-400 ring-2 ring-fuchsia-400/40",
    accentColor: "text-fuchsia-400"
  },
  {
    id: "scifi",
    name: "Sci-Fi",
    icon: "🚀",
    tagline: "Future & Spacetime",
    prompt: "Futuristic science fiction and mind-bending Sci-Fi movies",
    gradient: "from-cyan-500/20 via-sky-600/15 to-blue-600/10",
    border: "border-cyan-500/30 hover:border-cyan-400",
    activeBorder: "border-cyan-400 ring-2 ring-cyan-400/40",
    accentColor: "text-cyan-400"
  },
  {
    id: "fantasy",
    name: "Fantasy",
    icon: "✨",
    tagline: "Magic, Myths & Realms",
    prompt: "Magical fantasy and mythical adventure movies",
    gradient: "from-amber-400/20 via-yellow-600/15 to-purple-600/10",
    border: "border-amber-400/30 hover:border-amber-300",
    activeBorder: "border-amber-300 ring-2 ring-amber-300/40",
    accentColor: "text-amber-300"
  },
  {
    id: "horror",
    name: "Horror",
    icon: "👻",
    tagline: "Chills, Spooks & Fear",
    prompt: "Chilling and scary horror movies",
    gradient: "from-rose-600/20 via-red-800/15 to-slate-950/40",
    border: "border-rose-600/30 hover:border-rose-500",
    activeBorder: "border-rose-500 ring-2 ring-rose-500/40",
    accentColor: "text-rose-400"
  },
  {
    id: "mystery",
    name: "Mystery",
    icon: "🧩",
    tagline: "Whodunit & Puzzles",
    prompt: "Intriguing mysteries, suspenseful investigations, and clever detective puzzles",
    gradient: "from-violet-500/20 via-indigo-600/15 to-slate-800/20",
    border: "border-violet-500/30 hover:border-violet-400",
    activeBorder: "border-violet-400 ring-2 ring-violet-400/40",
    accentColor: "text-violet-400"
  },
  {
    id: "drama",
    name: "Drama",
    icon: "🎭",
    tagline: "Human Stories & Depth",
    prompt: "Emotional and powerful drama movies",
    gradient: "from-blue-500/20 via-indigo-600/15 to-slate-800/20",
    border: "border-blue-500/30 hover:border-blue-400",
    activeBorder: "border-blue-400 ring-2 ring-blue-400/40",
    accentColor: "text-blue-400"
  },
  {
    id: "history",
    name: "History",
    icon: "📜",
    tagline: "Biopics & Period Epics",
    prompt: "Magnificent historical epics and monumental biographical stories",
    gradient: "from-amber-600/20 via-yellow-700/15 to-stone-800/20",
    border: "border-amber-600/30 hover:border-amber-500",
    activeBorder: "border-amber-500 ring-2 ring-amber-500/40",
    accentColor: "text-amber-300"
  }
];

export default function GenreCarousel({ onSelectGenre, selectedGenreId, isLoading }) {
  const scrollRef = useRef(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

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

  const handleScroll = (direction) => {
    if (scrollRef.current) {
      const scrollAmount = direction === 'left' ? -320 : 320;
      scrollRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
  };

  return (
    <div className="w-full relative mb-8">
      {/* Header with Title & Navigation Controls */}
      <div className="flex items-center justify-between mb-3 px-1">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide uppercase flex items-center gap-2">
              Browse by Genre Carousel
              <span className="text-[11px] font-normal px-2 py-0.5 rounded-full bg-white/10 text-white/60">
                15 Curated Genres
              </span>
            </h3>
          </div>
        </div>

        {/* Carousel Navigation Buttons */}
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => handleScroll('left')}
            disabled={!canScrollLeft || isLoading}
            aria-label="Scroll left"
            className={`p-2 rounded-xl border backdrop-blur-md transition-all duration-200 cursor-pointer ${
              canScrollLeft
                ? "bg-slate-900/90 hover:bg-slate-800 text-white border-white/20 hover:border-amber-400/50 shadow-md shadow-slate-950/40"
                : "bg-slate-950/40 text-white/20 border-white/5 cursor-not-allowed"
            }`}
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={() => handleScroll('right')}
            disabled={!canScrollRight || isLoading}
            aria-label="Scroll right"
            className={`p-2 rounded-xl border backdrop-blur-md transition-all duration-200 cursor-pointer ${
              canScrollRight
                ? "bg-slate-900/90 hover:bg-slate-800 text-white border-white/20 hover:border-amber-400/50 shadow-md shadow-slate-950/40"
                : "bg-slate-950/40 text-white/20 border-white/5 cursor-not-allowed"
            }`}
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Carousel Track Container */}
      <div className="relative group">
        {/* Left Fade Gradient */}
        {canScrollLeft && (
          <div className="absolute left-0 top-0 bottom-0 w-12 bg-gradient-to-r from-slate-950 to-transparent z-10 pointer-events-none rounded-l-2xl" />
        )}
        
        {/* Right Fade Gradient */}
        {canScrollRight && (
          <div className="absolute right-0 top-0 bottom-0 w-12 bg-gradient-to-l from-slate-950 to-transparent z-10 pointer-events-none rounded-r-2xl" />
        )}

        {/* Scrollable Cards Track */}
        <div
          ref={scrollRef}
          className="flex items-center gap-3 overflow-x-auto scrollbar-none py-2 px-1 scroll-smooth snap-x snap-mandatory"
          style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
          {CAROUSEL_GENRES.map((genre) => {
            const isSelected = selectedGenreId === genre.id;
            return (
              <motion.button
                key={genre.id}
                type="button"
                whileHover={{ scale: 1.03, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => onSelectGenre(genre)}
                disabled={isLoading}
                className={`snap-start shrink-0 w-44 sm:w-48 text-left rounded-2xl p-3.5 bg-gradient-to-br ${genre.gradient} bg-slate-950/80 backdrop-blur-xl border transition-all duration-200 cursor-pointer shadow-lg relative overflow-hidden group ${
                  isSelected ? genre.activeBorder : genre.border
                }`}
              >
                {/* Active Indicator Glow */}
                {isSelected && (
                  <div className="absolute top-2 right-2 flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
                    <span className="w-2 h-2 rounded-full bg-amber-400" />
                  </div>
                )}

                {/* Genre Icon & Badge */}
                <div className="flex items-center justify-between mb-2">
                  <span className="text-2xl drop-shadow-md">{genre.icon}</span>
                  <span className={`text-[10px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full bg-white/10 ${genre.accentColor}`}>
                    {genre.name}
                  </span>
                </div>

                {/* Genre Title */}
                <h4 className="text-base font-extrabold text-white group-hover:text-amber-300 transition-colors tracking-tight">
                  {genre.name}
                </h4>

                {/* Subtitle / Vibe */}
                <p className="text-[11px] text-white/60 font-medium line-clamp-1 mt-0.5">
                  {genre.tagline}
                </p>

                {/* Bottom Highlight Glow Bar */}
                <div className={`h-1 w-0 group-hover:w-full rounded-full bg-gradient-to-r ${isSelected ? 'w-full from-amber-400 to-amber-300' : 'from-white/30 to-amber-400/50'} transition-all duration-300 mt-2.5`} />
              </motion.button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
