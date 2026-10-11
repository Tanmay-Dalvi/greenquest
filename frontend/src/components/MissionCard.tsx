import React from 'react';
import { MissionResponse } from '../types/mission';
import { Clock, Trees, Sparkles } from 'lucide-react';

interface MissionCardProps {
  mission: MissionResponse;
}

export const MissionCard: React.FC<MissionCardProps> = ({ mission }) => {
  return (
    <div className="bg-cream-50 border border-cream-300 rounded-2xl p-4 sm:p-5 shadow-sm space-y-4">
      {/* Category Pills & Timing */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-cream-200 pb-3">
        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-forest-800 text-cream-100 uppercase tracking-wider">
            <Trees className="w-3 h-3 text-amber-400 mr-1" />
            {mission.environment}
          </span>
          <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-sage-200/80 text-forest-800 capitalize">
            {mission.difficulty}
          </span>
        </div>

        <div className="flex items-center space-x-1 text-xs font-bold text-amber-600 bg-amber-50 px-2.5 py-1 rounded-full border border-amber-200/60">
          <Clock className="w-3.5 h-3.5" />
          <span>{mission.estimated_duration_minutes} min quest</span>
        </div>
      </div>

      {/* Title & Tagline */}
      <div className="space-y-1.5">
        <h2 className="font-serif text-xl sm:text-2xl font-bold text-forest-900 leading-snug">
          {mission.title}
        </h2>
        <p className="text-forest-700/90 text-xs sm:text-sm italic leading-relaxed">
          "{mission.tagline}"
        </p>
      </div>

      {/* Sensory Guidance Callout */}
      <div className="bg-sage-200/40 border border-sage-300/80 rounded-xl p-3 flex items-start space-x-2.5">
        <Sparkles className="w-4 h-4 text-forest-700 mt-0.5 shrink-0" />
        <div>
          <h4 className="text-[11px] font-bold uppercase tracking-wider text-forest-800">
            Sensory Focus
          </h4>
          <p className="text-xs text-forest-800 mt-0.5 leading-relaxed">
            {mission.sensory_prompt}
          </p>
        </div>
      </div>
    </div>
  );
};
