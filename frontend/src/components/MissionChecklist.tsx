import React from 'react';
import { MissionStep, SensoryType } from '../types/mission';
import {
  CheckCircle2,
  Circle,
  Clock,
  Eye,
  Volume2,
  Hand,
  Wind,
  Maximize2,
  Award,
} from 'lucide-react';

interface MissionChecklistProps {
  steps: MissionStep[];
  onToggleStep: (stepNumber: number) => void;
}

const SENSE_ICONS: Record<SensoryType, React.FC<{ className?: string }>> = {
  sight: Eye,
  sound: Volume2,
  touch: Hand,
  scent: Wind,
  spatial: Maximize2,
};

export const MissionChecklist: React.FC<MissionChecklistProps> = ({
  steps,
  onToggleStep,
}) => {
  const completedCount = steps.filter((s) => s.completed).length;
  const progressPercent = Math.round((completedCount / steps.length) * 100);
  const isAllComplete = steps.length > 0 && completedCount === steps.length;

  return (
    <div className="space-y-4">
      {/* Progress Bar Header */}
      <div className="bg-cream-50 border border-cream-300 rounded-xl p-3 shadow-xs space-y-2">
        <div className="flex items-center justify-between text-xs font-bold text-forest-800">
          <span className="uppercase tracking-wider">Quest Progress</span>
          <span className="text-amber-600">
            {completedCount} of {steps.length} Steps Completed ({progressPercent}%)
          </span>
        </div>
        <div className="w-full bg-cream-200 h-2.5 rounded-full overflow-hidden">
          <div
            className="bg-forest-700 h-full rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Completion Celebration Card */}
      {isAllComplete && (
        <div className="bg-forest-800 text-cream-50 border border-forest-900 rounded-2xl p-4 shadow-md text-center space-y-2 animate-fade-in">
          <div className="w-10 h-10 rounded-full bg-amber-500/20 text-amber-400 mx-auto flex items-center justify-center border border-amber-400/40">
            <Award className="w-6 h-6" />
          </div>
          <h3 className="font-serif text-lg font-bold">
            Micro-Adventure Accomplished!
          </h3>
          <p className="text-xs text-sage-200 max-w-xs mx-auto leading-relaxed">
            You took time to unplug, breathe fresh air, and engage your senses with the living world.
          </p>
        </div>
      )}

      {/* Interactive Step Items */}
      <div className="space-y-3">
        {steps.map((step) => {
          const SenseIcon = SENSE_ICONS[step.sensory_type] || Eye;
          return (
            <div
              key={step.step_number}
              onClick={() => onToggleStep(step.step_number)}
              className={`p-4 rounded-xl border transition-all cursor-pointer select-none active:scale-[0.99] ${
                step.completed
                  ? 'bg-sage-200/40 border-sage-400/60 opacity-90'
                  : 'bg-cream-50 border-cream-300 hover:border-forest-600 shadow-xs'
              }`}
            >
              <div className="flex items-start space-x-3">
                {/* Checkbox Icon */}
                <button
                  type="button"
                  aria-label={`Toggle step ${step.step_number}`}
                  className="mt-0.5 focus:outline-none shrink-0"
                >
                  {step.completed ? (
                    <CheckCircle2 className="w-5 h-5 text-forest-700 fill-forest-100" />
                  ) : (
                    <Circle className="w-5 h-5 text-sage-400 hover:text-forest-600" />
                  )}
                </button>

                {/* Content */}
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <span
                      className={`text-xs font-bold leading-tight ${
                        step.completed
                          ? 'line-through text-forest-600'
                          : 'text-forest-900'
                      }`}
                    >
                      Step {step.step_number}: {step.title}
                    </span>

                    <div className="flex items-center space-x-1.5 shrink-0">
                      <span className="flex items-center space-x-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-cream-200/80 text-forest-700 capitalize">
                        <SenseIcon className="w-3 h-3 text-forest-600 mr-0.5" />
                        {step.sensory_type}
                      </span>
                      <span className="text-[10px] font-semibold text-amber-600 flex items-center">
                        <Clock className="w-2.5 h-2.5 mr-0.5" />
                        {step.estimated_minutes}m
                      </span>
                    </div>
                  </div>

                  <p
                    className={`text-xs leading-relaxed ${
                      step.completed ? 'text-forest-500' : 'text-forest-800'
                    }`}
                  >
                    {step.instruction}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
