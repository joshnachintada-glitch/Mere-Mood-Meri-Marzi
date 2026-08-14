import React, { useState, useRef, useEffect } from 'react';
import { Search, Globe2, ChevronDown, Check, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { HoverBorderGradient } from '@/components/ui/hover-border-gradient';
import GenreCarousel from './GenreCarousel';

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

export default function MoodInput({ onSearch, isLoading, selectedLanguage, setSelectedLanguage }) {
  const [customMood, setCustomMood] = useState("");
  const [selectedGenreId, setSelectedGenreId] = useState(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const selectedLangObj = LANGUAGES.find(l => l.code === selectedLanguage) || LANGUAGES[0];

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

  const handleSelectGenre = (genre) => {
    setSelectedGenreId(genre.id);
    setCustomMood(genre.prompt);
    onSearch(genre.prompt, selectedLanguage);
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
    setSelectedGenreId(null);
  };

  return (
    <div className="w-full max-w-5xl mx-auto mt-6 mb-10 px-4">
      {/* Hero Heading */}
      <div className="text-center mb-8">
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

      {/* 🌟 15-Genre Interactive Carousel */}
      <GenreCarousel
        onSelectGenre={handleSelectGenre}
        selectedGenreId={selectedGenreId}
        isLoading={isLoading}
      />

      {/* Freeform Search Bar */}
      <form onSubmit={handleSubmit} className="relative max-w-3xl mx-auto">
        <div className="relative flex items-center bg-slate-950/90 backdrop-blur-xl border border-white/20 hover:border-amber-400/50 focus-within:border-amber-400 rounded-2xl overflow-hidden shadow-2xl p-1.5 transition-colors">
          <input
            type="text"
            value={customMood}
            onChange={(e) => {
              setCustomMood(e.target.value);
              setSelectedGenreId(null);
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

