import React, { useState } from 'react';
import { Search } from 'lucide-react';
import { motion } from 'framer-motion';
import { LiquidButton } from '@/components/ui/liquid-glass-button';

const PRESETS = [
  "😊 Lighthearted Comedy",
  "💔 Heartbroken & Healing",
  "🏎️ High-Octane Action",
  "🧠 Mind-Bending Thriller",
  "☕ Cozy Rainy Day"
];

export default function MoodInput({ onSearch, isLoading }) {
  const [customMood, setCustomMood] = useState("");

  const handlePresetClick = (preset) => {
    setCustomMood(preset);
    onSearch(preset);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (customMood.trim()) {
      onSearch(customMood);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto mt-12 mb-16 px-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h2 className="text-4xl md:text-5xl font-extrabold mb-4 drop-shadow-lg">
          Choose your mood, we'll pick the movie.
        </h2>
        <p className="text-lg text-white/70">
          Stream it anywhere. Type how you feel or pick a vibe below.
        </p>
      </motion.div>

      <div className="flex flex-wrap justify-center gap-3 mb-8">
        {PRESETS.map((preset, idx) => (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            key={idx}
            onClick={() => handlePresetClick(preset)}
            className="px-4 py-2 rounded-full bg-blue-100/90 hover:bg-blue-200 text-blue-900 transition-colors text-sm font-bold shadow-sm"
            disabled={isLoading}
          >
            {preset}
          </motion.button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="relative group">
        <div className="absolute -inset-1 bg-gradient-to-r from-bollywood-pink to-bollywood-orange rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
        <div className="relative flex items-center bg-bollywood-dark/80 backdrop-blur-xl border border-white/20 rounded-2xl overflow-hidden shadow-2xl p-1.5">
          <input
            type="text"
            value={customMood}
            onChange={(e) => setCustomMood(e.target.value)}
            placeholder="e.g., 'Feeling stressed after exams, want something motivational...'"
            className="w-full bg-transparent px-4 py-3 outline-none text-lg text-white placeholder:text-blue-300/70"
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
                <span className="hidden sm:inline">Find Movies</span>
              </div>
            )}
          </LiquidButton>
        </div>
      </form>
    </div>
  );
}
