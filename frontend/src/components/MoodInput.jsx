import React, { useState } from 'react';
import { Search, Globe2, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import { LiquidButton } from '@/components/ui/liquid-glass-button';

export const LANGUAGES = [
  { code: "all", name: "All Indian Films", label: "🌟 All Languages" },
  { code: "hi", name: "Hindi", label: "🎬 Hindi" },
  { code: "te", name: "Telugu", label: "🎬 Telugu" },
  { code: "ta", name: "Tamil", label: "🎬 Tamil" },
  { code: "ml", name: "Malayalam", label: "🎬 Malayalam" },
  { code: "kn", name: "Kannada", label: "🎬 Kannada" },
  { code: "pa", name: "Punjabi", label: "🎬 Punjabi" },
  { code: "or", name: "Odia", label: "🎬 Odia" },
  { code: "mr", name: "Marathi", label: "🎬 Marathi" },
  { code: "bn", name: "Bengali", label: "🎬 Bengali" },
  { code: "gu", name: "Gujarati", label: "🎬 Gujarati" },
  { code: "en", name: "English", label: "🌐 English" },
];

export const GENRE_PRESETS = [
  { label: "🔥 Mass Action", prompt: "High adrenaline mass action and heroic thrillers" },
  { label: "😂 Laugh Riot Comedy", prompt: "Lighthearted hilarious comedy and feel-good fun" },
  { label: "❤️ Heartwarming Romance", prompt: "Sweet romantic love story and emotional connection" },
  { label: "🧠 Mind-Bending Thriller", prompt: "Edge-of-the-seat suspense mystery crime thriller" },
  { label: "👨‍👩‍👧 Family Drama", prompt: "Emotional family drama and wholesome bonding" },
  { label: "👻 Horror & Supernatural", prompt: "Chilling horror, supernatural eerie mystery" },
  { label: "🚀 Sci-Fi & Fantasy", prompt: "Futuristic science fiction and mythological fantasy" },
  { label: "👑 Historical Epic", prompt: "Magnificent historical period epic and war drama" },
];

export default function MoodInput({ onSearch, isLoading, selectedLanguage, setSelectedLanguage }) {
  const [customMood, setCustomMood] = useState("");

  const handlePresetClick = (presetPrompt) => {
    setCustomMood(presetPrompt);
    onSearch(presetPrompt, selectedLanguage);
  };

  const handleLanguageChange = (langCode) => {
    setSelectedLanguage(langCode);
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
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h2 className="text-4xl md:text-5xl font-extrabold mb-4 drop-shadow-lg tracking-tight">
          Mere Mood, <span className="bg-gradient-to-r from-amber-400 via-pink-400 to-red-400 bg-clip-text text-transparent">Meri Marzi</span>
        </h2>
        <p className="text-lg text-white/70 max-w-2xl mx-auto">
          Discover movies across all Indian languages & global cinema tailored to your exact mood, genres, and vibes.
        </p>
      </motion.div>

      {/* Language Selector Bar */}
      <div className="mb-6">
        <div className="flex items-center justify-center gap-2 mb-3 text-xs font-semibold uppercase tracking-wider text-white/60">
          <Globe2 className="w-4 h-4 text-amber-400" />
          <span>Select Language</span>
        </div>
        <div className="flex flex-wrap justify-center gap-2 max-w-3xl mx-auto">
          {LANGUAGES.map((lang) => {
            const isActive = selectedLanguage === lang.code;
            return (
              <button
                key={lang.code}
                type="button"
                onClick={() => handleLanguageChange(lang.code)}
                className={`px-3.5 py-1.5 rounded-full text-xs md:text-sm font-semibold transition-all duration-200 backdrop-blur-md border ${
                  isActive
                    ? "bg-amber-400 text-slate-900 border-amber-300 shadow-lg shadow-amber-400/20 scale-105"
                    : "bg-white/10 text-white/80 border-white/15 hover:bg-white/20 hover:text-white"
                }`}
              >
                {lang.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Genre / Mood Presets */}
      <div className="mb-8">
        <div className="flex items-center justify-center gap-2 mb-3 text-xs font-semibold uppercase tracking-wider text-white/60">
          <Sparkles className="w-4 h-4 text-pink-400" />
          <span>Popular Vibe & Genre Presets</span>
        </div>
        <div className="flex flex-wrap justify-center gap-2.5 max-w-3xl mx-auto">
          {GENRE_PRESETS.map((preset, idx) => (
            <motion.button
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.96 }}
              key={idx}
              type="button"
              onClick={() => handlePresetClick(preset.prompt)}
              className="px-3.5 py-1.5 rounded-full bg-slate-900/60 hover:bg-slate-800 text-blue-200 border border-blue-400/20 hover:border-blue-400/40 transition-colors text-xs md:text-sm font-medium shadow-sm"
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
            placeholder="e.g. 'Exciting Odia family movie' or 'Romantic Telugu movie with great music'..."
            className="w-full bg-transparent px-4 py-3 outline-none text-base md:text-lg text-white placeholder:text-white/40"
            disabled={isLoading}
          />
          <LiquidButton 
            type="submit" 
            disabled={isLoading || !customMood.trim()}
            size="default"
            className="rounded-xl px-5 text-white font-bold whitespace-nowrap"
          >
            {isLoading ? (
              <span className="animate-spin inline-block w-5 h-5 border-2 border-white/20 border-t-white rounded-full"></span>
            ) : (
              <div className="flex items-center gap-2">
                <Search className="w-4 h-4" />
                <span className="hidden sm:inline">Explore Films</span>
              </div>
            )}
          </LiquidButton>
        </div>
      </form>
    </div>
  );
}
