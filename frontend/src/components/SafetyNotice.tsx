import React, { useState } from 'react';
import { ShieldCheck, ChevronDown, ChevronUp, Leaf } from 'lucide-react';

interface SafetyNoticeProps {
  leaveNoTrace: string;
  safetyNotes: string[];
}

export const SafetyNotice: React.FC<SafetyNoticeProps> = ({
  leaveNoTrace,
  safetyNotes,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="bg-cream-50 border border-cream-300 rounded-xl p-3.5 space-y-2.5 text-xs">
      {/* Leave No Trace callout */}
      <div className="flex items-start space-x-2 text-forest-800">
        <Leaf className="w-4 h-4 text-forest-600 mt-0.5 shrink-0" />
        <div className="space-y-0.5">
          <span className="font-bold uppercase tracking-wider text-[10px] text-forest-700">
            Leave No Trace Stewardship
          </span>
          <p className="text-forest-800 leading-relaxed text-[11px]">{leaveNoTrace}</p>
        </div>
      </div>

      {/* Safety notes accordion */}
      <div className="border-t border-cream-200 pt-2">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="w-full flex items-center justify-between text-left text-forest-700 hover:text-forest-900 transition font-medium text-[11px]"
        >
          <span className="flex items-center space-x-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-sage-500" />
            <span>Outdoor Safety Guidance ({safetyNotes.length} notes)</span>
          </span>
          {isOpen ? (
            <ChevronUp className="w-3.5 h-3.5" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5" />
          )}
        </button>

        {isOpen && (
          <ul className="mt-2 space-y-1 pl-5 list-disc text-forest-700/90 text-[11px] leading-relaxed">
            {safetyNotes.map((note, idx) => (
              <li key={idx}>{note}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};
