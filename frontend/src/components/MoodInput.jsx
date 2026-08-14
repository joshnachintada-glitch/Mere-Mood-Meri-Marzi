import React, { useState, useRef, useEffect } from 'react';
import { Search, Globe2, Sparkles, ChevronDown, Check, X } from 'lucide-react';
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
        <h2 className="text-4xl sm:text-5xl md:text-6xl font-black drop-shadow-sm tracking-tight text-blue-950">
          Mere Mood, <span className="text-blue-900 underline decoration-blue-950/30">Meri Marzi</span>
        </h2>
      </div>

      {/* Language Selector Bar */}
      <div className="flex justify-center mb-6 relative z-30" ref={dropdownRef}>
        <div className="relative inline-block text-left">
          <button
            type="button"
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="flex items-center gap-3 px-5 py-2.5 rounded-2xl bg-transparent hover:bg-blue-950/5 border border-blue-950/30 hover:border-blue-950 backdrop-blur-md shadow-sm transition-all duration-200 text-blue-950 group cursor-pointer"
          >
            <Globe2 className="w-4 h-4 text-blue-950 group-hover:scale-110 transition-transform" />
            <div className="text-left flex items-center gap-2">
              <span className="text-xs text-blue-950/60 uppercase font-bold tracking-wider">Industry:</span>
              <span className="text-sm font-black text-blue-950">{selectedLangObj.label}</span>
              <span className="text-xs text-blue-900/60 hidden sm:inline">({selectedLangObj.region})</span>
            </div>
            <ChevronDown className={`w-4 h-4 text-blue-950 transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`} />
          </button>

          {/* Floating Dropdown Menu */}
          <AnimatePresence>
            {isDropdownOpen && (
              <motion.div
                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -10, scale: 0.95 }}
                transition={{ duration: 0.15 }}
                className="absolute left-1/2 -translate-x-1/2 mt-2 w-72 sm:w-80 max-h-80 overflow-y-auto rounded-2xl bg-white/95 border border-blue-950/20 shadow-2xl backdrop-blur-2xl p-2 z-50 divide-y divide-blue-950/10 scrollbar-thin scrollbar-thumb-blue-950/20"
              >
                <div className="px-3 py-2 text-[11px] font-black text-blue-950/60 uppercase tracking-wider">
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
                            ? "bg-blue-950/10 text-blue-950 font-black border border-blue-950/30"
                            : "text-blue-950/80 hover:bg-blue-950/5 hover:text-blue-950"
                        }`}
                      >
                        <div className="flex flex-col">
                          <span className="font-bold">{lang.label}</span>
                          <span className="text-[11px] text-blue-900/60">{lang.region}</span>
                        </div>
                        {isSelected && <Check className="w-4 h-4 text-blue-950 shrink-0" />}
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
        <div className="relative flex items-center bg-transparent backdrop-blur-md border-2 border-blue-950/35 hover:border-blue-950 focus-within:border-blue-950 rounded-2xl overflow-hidden shadow-sm p-1.5 transition-colors">
          <input
            type="text"
            value={customMood}
            onChange={(e) => {
              setCustomMood(e.target.value);
              setSelectedGenreId(null);
            }}
            placeholder="e.g. 'Mind-bending murder mystery with a crazy twist' or 'Chill feel-good romance'..."
            className="w-full bg-transparent px-4 py-3 outline-none text-base md:text-lg text-blue-950 placeholder:text-blue-950/45 font-medium"
            disabled={isLoading}
          />
          
          {customMood && (
            <button
              type="button"
              onClick={handleClear}
              className="p-2 text-blue-950/60 hover:text-blue-950 rounded-full transition-colors mr-1 cursor-pointer"
              title="Clear input"
            >
              <X className="w-4 h-4" />
            </button>
          )}

          <button
            type="submit" 
            disabled={isLoading}
            className="rounded-xl px-6 py-2.5 text-sm bg-transparent hover:bg-blue-950/10 border border-blue-950/40 hover:border-blue-950 text-blue-950 font-black whitespace-nowrap flex items-center gap-2 transition-all cursor-pointer shadow-sm"
          >
            <Search className="w-4 h-4 text-blue-950" />
            <span className="hidden sm:inline">Explore Movies</span>
          </button>
        </div>
      </form>
    </div>
  );
}

