import React from 'react';
import { Clapperboard } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 px-6 py-4 flex items-center justify-between bg-transparent backdrop-blur-md border-b border-blue-950/20">
      <div className="flex items-center gap-3">
        <Clapperboard className="w-7 h-7 text-blue-950" />
        <span className="text-lg font-black text-blue-950 tracking-tight">
          Mere Mood Meri Marzi
        </span>
      </div>
    </nav>
  );
}
