import React from 'react';
import { Clapperboard } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="glass-panel sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <Clapperboard className="w-8 h-8 text-blue-400" />
      </div>
      <div className="text-sm font-medium text-white/80 hidden sm:block">
        Mere Mood Meri Marzi
      </div>
    </nav>
  );
}
