import React from 'react';
import { Compass, History, Wifi, WifiOff } from 'lucide-react';

interface HeaderProps {
  isOnline: boolean;
  onOpenHistory: () => void;
  onResetToForm: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  isOnline,
  onOpenHistory,
  onResetToForm,
}) => {
  return (
    <header className="sticky top-0 z-30 bg-forest-800 text-cream-100 shadow-md border-b border-forest-900 safe-top">
      <div className="max-w-md mx-auto px-4 py-3 flex items-center justify-between">
        {/* Brand identity */}
        <button
          onClick={onResetToForm}
          className="flex items-center space-x-2.5 text-left focus:outline-none focus:ring-2 focus:ring-amber-500 rounded-lg p-1 transition"
          aria-label="GreenQuest Home"
        >
          <div className="w-8 h-8 rounded-lg bg-forest-700 border border-sage-400 flex items-center justify-center text-amber-400 shadow-inner">
            <Compass className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-serif font-bold text-lg leading-tight tracking-wide text-cream-50">
              GreenQuest
            </h1>
            <p className="text-[10px] tracking-wider uppercase text-sage-300 font-medium">
              Outdoor Companion
            </p>
          </div>
        </button>

        {/* Action Controls */}
        <div className="flex items-center space-x-2">
          {/* Connectivity Badge */}
          <div
            className={`flex items-center space-x-1 px-2 py-1 rounded-full text-[11px] font-medium transition-colors ${
              isOnline
                ? 'bg-forest-900/80 text-sage-200 border border-forest-700'
                : 'bg-amber-600/30 text-amber-200 border border-amber-500/50'
            }`}
            title={isOnline ? 'Online mode active' : 'Offline mode active (Local storage & cached generation)'}
          >
            {isOnline ? (
              <>
                <Wifi className="w-3 h-3 text-sage-300" />
                <span className="hidden sm:inline">Online</span>
              </>
            ) : (
              <>
                <WifiOff className="w-3 h-3 text-amber-400" />
                <span>Offline</span>
              </>
            )}
          </div>

          {/* History Button */}
          <button
            onClick={onOpenHistory}
            className="p-2 rounded-lg bg-forest-700/60 hover:bg-forest-700 text-cream-100 border border-forest-600 transition flex items-center focus:ring-2 focus:ring-amber-500"
            aria-label="View Adventure History"
            title="Saved adventures"
          >
            <History className="w-4 h-4 text-sage-200" />
          </button>
        </div>
      </div>
    </header>
  );
};
