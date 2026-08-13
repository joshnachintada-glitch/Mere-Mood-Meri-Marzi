import React from 'react';
import { Clapperboard } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="glass-panel sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <Clapperboard className="w-7 h-7 text-amber-400" />
        <span className="text-lg font-bold text-white tracking-tight">
          Mere Mood Meri Marzi
        </span>
      </div>
    </nav>
  );
}
