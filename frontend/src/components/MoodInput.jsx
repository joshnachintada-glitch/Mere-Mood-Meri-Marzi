import React, { useState, useRef, useEffect } from 'react';
import { Search, Globe2, Sparkles, ChevronDown, Check } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { LiquidButton } from '@/components/ui/liquid-glass-button';

export const LANGUAGES = [
  { code: "all", name: "All Indian Films", label: "🌟 All Languages", region: "Pan-India" },
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
  { code: "en", name: "English", label: "🌐 English", region: "Global / Indian English" },
];

export const GENRE_PRESETS = [
  { label: "Action", prompt: "Action movies with intense thrill and high energy" },
  { label: "Comedy", prompt: "Hilarious comedy movies with feel-good laughter" },
  { label: "Drama", prompt: "Emotional and powerful drama movies" },
  { label: "Horror", prompt: "Chilling and scary horror movies" },
  { label: "Science Fiction (Sci-Fi)", prompt: "Futuristic science fiction and mind-bending Sci-Fi movies" },
  { label: "Fantasy", prompt: "Magical fantasy and mythical adventure movies" },
  { label: "Thriller & Suspense", prompt: "Gripping thriller, suspense and mystery movies" },
  { label: "Romance", prompt: "Heartwarming romantic love story movies" },
];

export default function MoodInput({ onSearch, isLoading, selectedLanguage, setSelectedLanguage }) {
  const [customMood, setCustomMood] = useState("");
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

  const handlePresetClick = (presetPrompt) => {
    setCustomMood(presetPrompt);
    onSearch(presetPrompt, selectedLanguage);
  };

  const handleSelectLanguage = (langCode) => {
    setSelectedLanguage(langCode);
    setIsDropdownOpen(false);
    if (customMood.trim()) {
      onSearch(customMood, langCode);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (customMood.trim()) {
      onSearch(customMood, selectedLanguage);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto mt-8 mb-12 px-4">
      {/* Hero Heading */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h2 className="text-4xl md:text-5xl font-extrabold mb-4 drop-shadow-lg tracking-tight text-white">
          Mere Mood, Meri Marzi
        </h2>
        <p className="text-lg text-white/70 max-w-2xl mx-auto">
          Discover movies across all Indian languages & genres tailored to your exact mood and vibes.
        </p>
      </motion.div>

      {/* Language Dropdown Menu Bar */}
      <div className="flex justify-center mb-6 relative z-30" ref={dropdownRef}>
        <div className="relative inline-block text-left">
          <button
            type="button"
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="flex items-center gap-3 px-5 py-2.5 rounded-2xl bg-slate-900/80 hover:bg-slate-800/90 border border-white/20 hover:border-amber-400/50 backdrop-blur-xl shadow-xl transition-all duration-200 text-white group"
          >
            <Globe2 className="w-4 h-4 text-amber-400 group-hover:scale-110 transition-transform" />
            <div className="text-left flex items-center gap-2">
              <span className="text-xs text-white/50 uppercase font-semibold tracking-wider">Language:</span>
              <span className="text-sm font-bold text-amber-300">{selectedLangObj.label}</span>
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
                        className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-sm transition-colors text-left ${
                          isSelected
                            ? "bg-amber-400/15 text-amber-300 font-bold border border-amber-400/30"
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

      {/* Genre / Mood Presets */}
      <div className="mb-8">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 max-w-3xl mx-auto">
          {GENRE_PRESETS.map((preset, idx) => (
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              key={idx}
              type="button"
              onClick={() => handlePresetClick(preset.prompt)}
              className="w-full py-2 px-3 rounded-xl bg-slate-900/70 hover:bg-slate-800/90 text-blue-100 border border-blue-400/20 hover:border-amber-400/50 hover:text-white transition-all text-xs sm:text-sm font-semibold shadow-md text-center flex items-center justify-center backdrop-blur-md"
              disabled={isLoading}
            >
              {preset.label}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Search Input Bar */}
      <form onSubmit={handleSubmit} className="relative group max-w-2xl mx-auto">
        <div className="absolute -inset-1 bg-gradient-to-r from-pink-500 via-amber-500 to-indigo-500 rounded-2xl blur opacity-30 group-hover:opacity-60 transition duration-500"></div>
        <div className="relative flex items-center bg-slate-950/80 backdrop-blur-xl border border-white/20 rounded-2xl overflow-hidden shadow-2xl p-1.5">
          <input
            type="text"
            value={customMood}
            onChange={(e) => setCustomMood(e.target.value)}
            placeholder="e.g. 'Thrilling mystery murder investigation' or 'Heartfelt family comedy'..."
            className="w-full bg-transparent px-4 py-3 outline-none text-base md:text-lg text-white placeholder:text-white/40"
            disabled={isLoading}
          />
          <LiquidButton 
            type="submit" 
            disabled={isLoading || !customMood.trim()}
            size="default"
            className="rounded-xl px-5 text-white font-bold whitespace-nowrap"
          >
            <div className="flex items-center gap-2">
              <Search className="w-4 h-4" />
              <span className="hidden sm:inline">{isLoading ? "Searching..." : "Explore Films"}</span>
            </div>
          </LiquidButton>
        </div>
      </form>
    </div>
  );
}
