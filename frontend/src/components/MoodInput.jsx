import React, { useState, useRef, useEffect, useMemo } from 'react';
import { Search, Globe2, Sparkles, ChevronDown, Check, X, Compass, Flame, Laugh, Rocket, Sparkle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { HoverBorderGradient } from '@/components/ui/hover-border-gradient';

export const LANGUAGES = [
  { code: "all", name: "All Indian & Global Films", label: "🌟 All Languages", region: "Pan-India & Global" },
  { code: "hi", name: "Hindi", label: "🎬 Hindi", region: "Bollywood" },
  { code: "te", name: "Telugu", label: "🎬 Telugu", region: "Tollywood" },
  { code: "ta", name: "Tamil", label: "🎬 Tamil", region: "Kollywood" },
  { code: "ml", name: "Malayalam", label: "🎬 Malayalam", region: "Mollywood" },
  { code: "kn", name: "Kannada", label: "🎬 Kannada", region: "Sandalwood" },
  { code: "pa", name: "Punjabi", label: "🎬 Punjabi", region: "Pollywood" },
  { code: "or", name: "Odia", label: "🎬 Odia", region: "Ollywood" },
  { code: "mr", name: "Marathi", label: "🎬 Marathi", region: "Marathi Cinema" },
  { code: "bn", name: "Bengali", label: "🎬 Bengali", region: "Tollywood (Bengali)" },
  { code: "gu", name: "Gujarati", label: "🎬 Gujarati", region: "Dhollywood" },
  { code: "as", name: "Assamese", label: "🎬 Assamese", region: "Jollywood" },
  { code: "ur", name: "Urdu", label: "🎬 Urdu", region: "Indian Urdu Cinema" },
  { code: "ko", name: "Korean / K-Dramas", label: "🇰🇷 K-Dramas & Korean", region: "K-Dramas & Korean Cinema" },
  { code: "ja", name: "Japanese / Anime", label: "🎌 Anime (Japanese)", region: "Anime & Japanese Cinema" },
  { code: "en", name: "English", label: "🌐 English", region: "Global / Hollywood" },
];

export const GENRE_CATEGORIES = [
  { id: "all", label: "✨ All Moods" },
  { id: "action_thrill", label: "🔥 Action & Thrill" },
  { id: "comedy_romance", label: "❤️ Comedy & Romance" },
  { id: "scifi_fantasy", label: "🚀 Sci-Fi & Mystery" },
  { id: "world_cinema", label: "🎌 Anime & Drama" },
];

export const GENRE_PRESETS = [
  // Action & Thrill
  { id: "action", label: "🔥 Action", category: "action_thrill", prompt: "Action movies with intense thrill and high energy" },
  { id: "thriller", label: "🔍 Thriller", category: "action_thrill", prompt: "Gripping thriller, suspense and mystery movies" },
  { id: "crime", label: "🕵️ Crime", category: "action_thrill", prompt: "Intense crime, underworld, and mafia sagas" },
  { id: "adventure", label: "🗺️ Adventure", category: "action_thrill", prompt: "Epic adventure, exploration, and journey movies" },
  { id: "war", label: "⚔️ War", category: "action_thrill", prompt: "Gripping war dramas, heroic bravery, and epic combat sagas" },
  
  // Comedy & Romance
  { id: "comedy", label: "😂 Comedy", category: "comedy_romance", prompt: "Hilarious comedy movies with feel-good laughter" },
  { id: "romance", label: "❤️ Romance", category: "comedy_romance", prompt: "Heartwarming romantic love story movies" },
  { id: "family", label: "👨‍👩‍👧 Family", category: "comedy_romance", prompt: "Wholesome, magical family movies for all ages" },
  { id: "music", label: "🎵 Musical", category: "comedy_romance", prompt: "Soulful musical journeys, melodious rhythms, and dance" },
  
  // Sci-Fi & Mystery
  { id: "scifi", label: "🚀 Sci-Fi", category: "scifi_fantasy", prompt: "Futuristic science fiction and mind-bending Sci-Fi movies" },
  { id: "fantasy", label: "✨ Fantasy", category: "scifi_fantasy", prompt: "Magical fantasy and mythical adventure movies" },
  { id: "horror", label: "👻 Horror", category: "scifi_fantasy", prompt: "Chilling and scary horror movies" },
  { id: "mystery", label: "🧩 Mystery", category: "scifi_fantasy", prompt: "Intriguing mysteries, suspenseful investigations, and clever detective puzzles" },

  // World & Drama
  { id: "drama", label: "🎭 Drama", category: "world_cinema", prompt: "Emotional and powerful drama movies" },
  { id: "kdrama", label: "🫰 K-Drama", category: "world_cinema", prompt: "Top Korean movies and K-drama romantic thrillers" },
  { id: "anime", label: "🎌 Anime", category: "world_cinema", prompt: "Masterpiece anime movies with stunning animation and storytelling" },
  { id: "history", label: "📜 History", category: "world_cinema", prompt: "Magnificent historical epics and monumental biographical stories" },
];

export default function MoodInput({ onSearch, isLoading, selectedLanguage, setSelectedLanguage }) {
  const [customMood, setCustomMood] = useState("");
  const [activeCategory, setActiveCategory] = useState("all");
  const [selectedPresetId, setSelectedPresetId] = useState(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const selectedLangObj = LANGUAGES.find(l => l.code === selectedLanguage) || LANGUAGES[0];

  // Filtered genre presets based on active category tab
  const displayedPresets = useMemo(() => {
    if (activeCategory === "all") return GENRE_PRESETS;
    return GENRE_PRESETS.filter(p => p.category === activeCategory);
  }, [activeCategory]);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handlePresetClick = (preset) => {
    setSelectedPresetId(preset.id);
    setCustomMood(preset.prompt);
    onSearch(preset.prompt, selectedLanguage);
  };

  const handleSelectLanguage = (langCode) => {
    setSelectedLanguage(langCode);
    setIsDropdownOpen(false);
    const query = customMood.trim() || "Top rated movies across all genres and industries";
    onSearch(query, langCode);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const query = customMood.trim() || "Top rated movies across all genres and industries";
    onSearch(query, selectedLanguage);
  };

  const handleClear = () => {
    setCustomMood("");
    setSelectedPresetId(null);
  };

  return (
    <div className="w-full max-w-5xl mx-auto mt-6 mb-10 px-4">
      {/* Hero Heading */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-400/20 text-amber-300 text-xs font-semibold uppercase tracking-widest mb-3 backdrop-blur-md">
          <Sparkles className="w-3.5 h-3.5" /> AI-Powered Movie Recommender
        </div>
        <h2 className="text-4xl sm:text-5xl md:text-6xl font-black mb-3 drop-shadow-xl tracking-tight text-white">
          Mere Mood, <span className="text-amber-400">Meri Marzi</span>
        </h2>
        <p className="text-base sm:text-lg text-white/70 max-w-2xl mx-auto leading-relaxed">
          Discover movies arranged across all Indian & global cinema industries tailored to your exact mood, genre, and vibes.
        </p>
      </div>

      {/* Language Selector Bar */}
      <div className="flex justify-center mb-6 relative z-30" ref={dropdownRef}>
        <div className="relative inline-block text-left">
          <button
            type="button"
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="flex items-center gap-3 px-5 py-2.5 rounded-2xl bg-slate-900/90 hover:bg-slate-800/95 border border-white/20 hover:border-amber-400/60 backdrop-blur-xl shadow-xl transition-all duration-200 text-white group cursor-pointer"
          >
            <Globe2 className="w-4 h-4 text-amber-400 group-hover:scale-110 transition-transform" />
            <div className="text-left flex items-center gap-2">
              <span className="text-xs text-white/50 uppercase font-bold tracking-wider">Industry:</span>
              <span className="text-sm font-extrabold text-amber-300">{selectedLangObj.label}</span>
              <span className="text-xs text-white/40 hidden sm:inline">({selectedLangObj.region})</span>
            </div>
            <ChevronDown className={`w-4 h-4 text-white/60 transition-transform duration-200 ${isDropdownOpen ? 'rotate-180 text-amber-400' : ''}`} />
          </button>

          {/* Floating Dropdown Menu */}
          <AnimatePresence>
            {isDropdownOpen && (
              <motion.div
                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -10, scale: 0.95 }}
                transition={{ duration: 0.15 }}
                className="absolute left-1/2 -translate-x-1/2 mt-2 w-72 sm:w-80 max-h-80 overflow-y-auto rounded-2xl bg-slate-950/95 border border-white/20 shadow-2xl backdrop-blur-2xl p-2 z-50 divide-y divide-white/5 scrollbar-thin scrollbar-thumb-white/20"
              >
                <div className="px-3 py-2 text-[11px] font-bold text-white/40 uppercase tracking-wider">
                  Select Movie Industry & Language
                </div>
                <div className="py-1">
                  {LANGUAGES.map((lang) => {
                    const isSelected = selectedLanguage === lang.code;
                    return (
                      <button
                        key={lang.code}
                        type="button"
                        onClick={() => handleSelectLanguage(lang.code)}
                        className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-sm transition-colors text-left cursor-pointer ${
                          isSelected
                            ? "bg-amber-400/20 text-amber-300 font-bold border border-amber-400/40"
                            : "text-white/80 hover:bg-white/10 hover:text-white"
                        }`}
                      >
                        <div className="flex flex-col">
                          <span className="font-semibold">{lang.label}</span>
                          <span className="text-[11px] text-white/50">{lang.region}</span>
                        </div>
                        {isSelected && <Check className="w-4 h-4 text-amber-400 shrink-0" />}
                      </button>
                    );
                  })}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Genre Categories Nav Tabs */}
      <div className="flex items-center justify-center gap-1.5 mb-3 flex-wrap">
        {GENRE_CATEGORIES.map((cat) => {
          const isActive = activeCategory === cat.id;
          return (
            <button
              key={cat.id}
              type="button"
              onClick={() => setActiveCategory(cat.id)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all duration-200 cursor-pointer ${
                isActive
                  ? "bg-amber-400 text-slate-950 shadow-md shadow-amber-400/20 font-extrabold scale-105"
                  : "bg-slate-900/60 text-white/70 hover:bg-slate-800 hover:text-white border border-white/10"
              }`}
            >
              {cat.label}
            </button>
          );
        })}
      </div>

      {/* Categorized Genre Presets Grid */}
      <div className="mb-6">
        <motion.div 
          layout
          className="flex flex-wrap justify-center gap-2 max-w-3xl mx-auto"
        >
          <AnimatePresence>
            {displayedPresets.map((preset) => {
              const isSelected = selectedPresetId === preset.id || customMood === preset.prompt;
              return (
                <motion.button
                  key={preset.id}
                  layout
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.15 }}
                  type="button"
                  onClick={() => handlePresetClick(preset)}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-semibold shadow-sm backdrop-blur-md transition-all duration-200 cursor-pointer flex items-center gap-1.5 ${
                    isSelected
                      ? "bg-gradient-to-r from-amber-400 to-amber-300 text-slate-950 font-bold border border-amber-200 shadow-amber-500/20 shadow-md scale-105"
                      : "bg-slate-900/80 text-blue-100/90 border border-white/15 hover:border-amber-400/50 hover:bg-slate-800 hover:text-white"
                  }`}
                  disabled={isLoading}
                >
                  <span>{preset.label}</span>
                </motion.button>
              );
            })}
          </AnimatePresence>
        </motion.div>
      </div>

      {/* Freeform Search Bar */}
      <form onSubmit={handleSubmit} className="relative max-w-3xl mx-auto">
        <div className="relative flex items-center bg-slate-950/90 backdrop-blur-xl border border-white/20 hover:border-amber-400/50 focus-within:border-amber-400 rounded-2xl overflow-hidden shadow-2xl p-1.5 transition-colors">
          <input
            type="text"
            value={customMood}
            onChange={(e) => {
              setCustomMood(e.target.value);
              setSelectedPresetId(null);
            }}
            placeholder="e.g. 'Mind-bending murder mystery with a crazy twist' or 'Chill feel-good romance'..."
            className="w-full bg-transparent px-4 py-3 outline-none text-base md:text-lg text-white placeholder:text-white/40"
            disabled={isLoading}
          />
          
          {customMood && (
            <button
              type="button"
              onClick={handleClear}
              className="p-2 text-white/50 hover:text-white rounded-full transition-colors mr-1 cursor-pointer"
              title="Clear input"
            >
              <X className="w-4 h-4" />
            </button>
          )}

          <HoverBorderGradient 
            as="button"
            type="submit" 
            disabled={isLoading}
            containerClassName="rounded-full shrink-0"
            className="rounded-full px-6 py-2.5 text-sm bg-slate-950 text-white font-bold whitespace-nowrap flex items-center gap-2 hover:text-amber-300 transition-colors cursor-pointer"
          >
            <Search className="w-4 h-4 text-amber-400" />
            <span className="hidden sm:inline">Explore Movies</span>
          </HoverBorderGradient>
        </div>
      </form>
    </div>
  );
}
