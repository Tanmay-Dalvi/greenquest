import React from 'react';
import { StoredMissionProgress, MissionResponse } from '../types/mission';
import { X, CheckCircle2, Circle, Trees, ArrowRight, Trash2 } from 'lucide-react';

interface HistoryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  history: StoredMissionProgress[];
  onSelectMission: (mission: MissionResponse) => void;
  onClearHistory: () => void;
}

export const HistoryDrawer: React.FC<HistoryDrawerProps> = ({
  isOpen,
  onClose,
  history,
  onSelectMission,
  onClearHistory,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-forest-950/60 backdrop-blur-xs animate-fade-in">
      <div className="w-full max-w-sm bg-cream-100 h-full shadow-2xl flex flex-col border-l border-cream-300 safe-top safe-bottom">
        {/* Drawer Header */}
        <div className="p-4 border-b border-cream-300 flex items-center justify-between bg-cream-200/50">
          <div>
            <h3 className="font-serif font-bold text-base text-forest-900">
              Saved Quests
            </h3>
            <p className="text-[11px] text-forest-600">
              Stored locally on this device
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-forest-700 hover:bg-cream-300 transition"
            aria-label="Close History"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* History List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {history.length === 0 ? (
            <div className="text-center py-12 text-forest-600 space-y-2">
              <Trees className="w-8 h-8 mx-auto text-sage-400" />
              <p className="text-xs">No saved explorations yet.</p>
              <p className="text-[11px] text-sage-500">
                Generate a quest to save your progress offline.
              </p>
            </div>
          ) : (
            history.map((entry) => {
              const m = entry.mission;
              const dateStr = new Date(entry.lastUpdated).toLocaleDateString(undefined, {
                month: 'short',
                day: 'numeric',
              });

              return (
                <div
                  key={m.id}
                  onClick={() => {
                    onSelectMission(m);
                    onClose();
                  }}
                  className="bg-cream-50 border border-cream-300 hover:border-forest-700 rounded-xl p-3.5 space-y-2 cursor-pointer transition shadow-xs active:scale-[0.99]"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-forest-700 bg-cream-200 px-2 py-0.5 rounded">
                      {m.environment}
                    </span>
                    <span className="text-[10px] text-sage-600">{dateStr}</span>
                  </div>

                  <h4 className="font-serif font-bold text-sm text-forest-900 line-clamp-1">
                    {m.title}
                  </h4>

                  <div className="flex items-center justify-between text-xs text-forest-700 pt-1">
                    <span className="flex items-center space-x-1 text-[11px]">
                      {entry.isFullyCompleted ? (
                        <>
                          <CheckCircle2 className="w-3.5 h-3.5 text-forest-700" />
                          <span className="font-semibold text-forest-800">Completed</span>
                        </>
                      ) : (
                        <>
                          <Circle className="w-3.5 h-3.5 text-amber-500" />
                          <span>
                            {entry.completedStepIndices.length}/{m.steps.length} Steps
                          </span>
                        </>
                      )}
                    </span>

                    <span className="flex items-center space-x-1 text-[11px] font-semibold text-forest-800">
                      <span>Resume</span>
                      <ArrowRight className="w-3 h-3 text-amber-600" />
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer Actions */}
        {history.length > 0 && (
          <div className="p-3 border-t border-cream-300 bg-cream-200/30 flex justify-between items-center text-xs">
            <span className="text-[11px] text-forest-600">
              {history.length} quests cached
            </span>
            <button
              onClick={onClearHistory}
              className="text-[11px] text-rose-700 hover:text-rose-900 flex items-center space-x-1 px-2 py-1 rounded hover:bg-rose-50 transition"
            >
              <Trash2 className="w-3 h-3" />
              <span>Clear History</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
