import React, { useState } from 'react';
import {
  EnvironmentType,
  MoodType,
  EnergyLevel,
  CompanionType,
  SensoryType,
  MissionPreferenceRequest,
} from '../types/mission';
import {
  Trees,
  Footprints,
  Flower2,
  Waves,
  Building2,
  Compass,
  Clock,
  Sparkles,
  Heart,
  Dog,
  Users,
  User,
  Eye,
  Volume2,
  Hand,
  Wind,
  Maximize2,
} from 'lucide-react';

interface PreferenceFormProps {
  onSubmit: (prefs: MissionPreferenceRequest) => void;
  isLoading: boolean;
}

const ENVIRONMENTS: Array<{ id: EnvironmentType; label: string; icon: React.FC<{ className?: string }> }> = [
  { id: 'park', label: 'City Park', icon: Trees },
  { id: 'forest', label: 'Forest / Woods', icon: Trees },
  { id: 'garden', label: 'Garden', icon: Flower2 },
  { id: 'waterfront', label: 'Waterfront', icon: Waves },
  { id: 'trail', label: 'Trail / Path', icon: Footprints },
  { id: 'neighborhood', label: 'Neighborhood', icon: Building2 },
];

const DURATIONS = [15, 30, 45, 60];

const MOODS: Array<{ id: MoodType; label: string }> = [
  { id: 'mindful', label: 'Mindful' },
  { id: 'curious', label: 'Curious' },
  { id: 'playful', label: 'Playful' },
  { id: 'contemplative', label: 'Contemplative' },
  { id: 'energized', label: 'Energized' },
];

const ENERGIES: Array<{ id: EnergyLevel; label: string; desc: string }> = [
  { id: 'low', label: 'Gentle', desc: 'Slow, stationary pauses' },
  { id: 'moderate', label: 'Balanced', desc: 'Leisurely walking' },
  { id: 'brisk', label: 'Brisk', desc: 'Continuous movement' },
];

const COMPANIONS: Array<{ id: CompanionType; label: string; icon: React.FC<{ className?: string }> }> = [
  { id: 'solo', label: 'Solo', icon: User },
  { id: 'dog', label: 'With Dog', icon: Dog },
  { id: 'friends', label: 'Friends', icon: Users },
  { id: 'family', label: 'Family', icon: Heart },
];

const SENSES: Array<{ id: SensoryType; label: string; icon: React.FC<{ className?: string }> }> = [
  { id: 'sight', label: 'Sight', icon: Eye },
  { id: 'sound', label: 'Sound', icon: Volume2 },
  { id: 'touch', label: 'Touch', icon: Hand },
  { id: 'scent', label: 'Scent', icon: Wind },
  { id: 'spatial', label: 'Space', icon: Maximize2 },
];

export const PreferenceForm: React.FC<PreferenceFormProps> = ({ onSubmit, isLoading }) => {
  const [environment, setEnvironment] = useState<EnvironmentType>('park');
  const [duration, setDuration] = useState<number>(30);
  const [mood, setMood] = useState<MoodType>('mindful');
  const [energy, setEnergy] = useState<EnergyLevel>('moderate');
  const [companion, setCompanion] = useState<CompanionType>('solo');
  const [sensoryFocus, setSensoryFocus] = useState<SensoryType[]>(['sight', 'sound']);
  const [notes, setNotes] = useState<string>('');

  const toggleSense = (sense: SensoryType) => {
    if (sensoryFocus.includes(sense)) {
      if (sensoryFocus.length > 1) {
        setSensoryFocus(sensoryFocus.filter((s) => s !== sense));
      }
    } else {
      setSensoryFocus([...sensoryFocus, sense]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      duration_minutes: duration,
      environment,
      mood,
      energy_level: energy,
      companion_type: companion,
      sensory_focus: sensoryFocus,
      notes: notes.trim() || undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 pb-8">
      {/* Introduction Hero Card */}
      <div className="bg-cream-200/70 border border-cream-300 rounded-2xl p-4 sm:p-5 shadow-sm text-center">
        <h2 className="font-serif text-xl sm:text-2xl font-bold text-forest-900 leading-snug">
          Where will your senses wander today?
        </h2>
        <p className="text-forest-700/80 text-xs sm:text-sm mt-1.5 leading-relaxed max-w-sm mx-auto">
          Set your outdoor setting and mindful pace. We’ll generate a structured micro-quest to help you slow down.
        </p>
      </div>

      {/* 1. Environment Selection */}
      <div className="space-y-2">
        <label className="block text-xs font-bold uppercase tracking-wider text-forest-800">
          1. Environment
        </label>
        <div className="grid grid-cols-3 gap-2">
          {ENVIRONMENTS.map((env) => {
            const Icon = env.icon;
            const isSelected = environment === env.id;
            return (
              <button
                type="button"
                key={env.id}
                onClick={() => setEnvironment(env.id)}
                className={`p-3 rounded-xl border flex flex-col items-center justify-center text-center transition-all ${
                  isSelected
                    ? 'bg-forest-800 text-cream-100 border-forest-900 shadow-sm ring-2 ring-forest-700'
                    : 'bg-cream-50 text-forest-900 border-cream-300 hover:bg-cream-200/50'
                }`}
              >
                <Icon className={`w-5 h-5 mb-1.5 ${isSelected ? 'text-amber-400' : 'text-sage-500'}`} />
                <span className="text-xs font-semibold leading-tight">{env.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. Duration Selector */}
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <label className="text-xs font-bold uppercase tracking-wider text-forest-800 flex items-center space-x-1.5">
            <Clock className="w-3.5 h-3.5 text-forest-600" />
            <span>2. Time Available</span>
          </label>
          <span className="text-xs font-bold text-amber-600">{duration} minutes</span>
        </div>
        <div className="grid grid-cols-4 gap-2">
          {DURATIONS.map((mins) => (
            <button
              type="button"
              key={mins}
              onClick={() => setDuration(mins)}
              className={`py-2.5 rounded-xl text-xs font-bold transition border ${
                duration === mins
                  ? 'bg-amber-500 text-white border-amber-600 shadow-sm'
                  : 'bg-cream-50 text-forest-800 border-cream-300 hover:bg-cream-200'
              }`}
            >
              {mins}m
            </button>
          ))}
        </div>
      </div>

      {/* 3. Mood Selection */}
      <div className="space-y-2">
        <label className="block text-xs font-bold uppercase tracking-wider text-forest-800">
          3. Adventure Mindset
        </label>
        <div className="flex flex-wrap gap-2">
          {MOODS.map((m) => {
            const isSelected = mood === m.id;
            return (
              <button
                type="button"
                key={m.id}
                onClick={() => setMood(m.id)}
                className={`px-3.5 py-1.5 rounded-full text-xs font-medium border transition ${
                  isSelected
                    ? 'bg-forest-700 text-cream-100 border-forest-800 shadow-xs'
                    : 'bg-cream-50 text-forest-800 border-cream-300 hover:bg-cream-200'
                }`}
              >
                {m.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* 4. Energy Level */}
      <div className="space-y-2">
        <label className="block text-xs font-bold uppercase tracking-wider text-forest-800">
          4. Physical Energy
        </label>
        <div className="grid grid-cols-3 gap-2">
          {ENERGIES.map((eng) => {
            const isSelected = energy === eng.id;
            return (
              <button
                type="button"
                key={eng.id}
                onClick={() => setEnergy(eng.id)}
                className={`p-2.5 rounded-xl border text-left transition ${
                  isSelected
                    ? 'bg-sage-400/20 border-sage-500 text-forest-900 ring-1 ring-sage-500'
                    : 'bg-cream-50 text-forest-800 border-cream-300 hover:bg-cream-200'
                }`}
              >
                <div className="font-bold text-xs">{eng.label}</div>
                <div className="text-[10px] text-forest-600 mt-0.5 leading-tight">{eng.desc}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* 5. Sensory Focus */}
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <label className="text-xs font-bold uppercase tracking-wider text-forest-800">
            5. Senses to Awaken
          </label>
          <span className="text-[11px] text-sage-600 font-medium">Select 1 or more</span>
        </div>
        <div className="grid grid-cols-5 gap-1.5">
          {SENSES.map((sense) => {
            const Icon = sense.icon;
            const isSelected = sensoryFocus.includes(sense.id);
            return (
              <button
                type="button"
                key={sense.id}
                onClick={() => toggleSense(sense.id)}
                className={`py-2 px-1 rounded-xl border flex flex-col items-center justify-center transition ${
                  isSelected
                    ? 'bg-forest-800 text-cream-50 border-forest-900 shadow-xs ring-1 ring-amber-500'
                    : 'bg-cream-50 text-forest-700 border-cream-300 hover:bg-cream-200'
                }`}
              >
                <Icon className={`w-4 h-4 mb-1 ${isSelected ? 'text-amber-400' : 'text-sage-400'}`} />
                <span className="text-[10px] font-semibold">{sense.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 6. Companions */}
      <div className="space-y-2">
        <label className="block text-xs font-bold uppercase tracking-wider text-forest-800">
          6. Exploring With
        </label>
        <div className="grid grid-cols-4 gap-2">
          {COMPANIONS.map((comp) => {
            const Icon = comp.icon;
            const isSelected = companion === comp.id;
            return (
              <button
                type="button"
                key={comp.id}
                onClick={() => setCompanion(comp.id)}
                className={`py-2 px-1.5 rounded-xl border flex items-center justify-center space-x-1.5 transition text-xs font-medium ${
                  isSelected
                    ? 'bg-forest-700 text-cream-50 border-forest-800 shadow-xs'
                    : 'bg-cream-50 text-forest-800 border-cream-300 hover:bg-cream-200'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isSelected ? 'text-amber-400' : 'text-sage-500'}`} />
                <span>{comp.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Optional Local Context */}
      <div className="space-y-1.5">
        <label className="block text-xs font-bold uppercase tracking-wider text-forest-800">
          Local Landmarks (Optional)
        </label>
        <input
          type="text"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="e.g. Near duck pond, north entrance, oak grove"
          maxLength={100}
          className="w-full px-3.5 py-2.5 text-xs rounded-xl bg-cream-50 border border-cream-300 focus:outline-none focus:ring-2 focus:ring-forest-700 focus:border-forest-700 placeholder:text-forest-400"
        />
      </div>

      {/* Submit Action Button */}
      <button
        type="submit"
        disabled={isLoading}
        className={`w-full py-3.5 px-4 rounded-xl font-bold text-sm tracking-wide shadow-md transition flex items-center justify-center space-x-2 text-cream-50 ${
          isLoading
            ? 'bg-forest-600/70 cursor-not-allowed'
            : 'bg-forest-800 hover:bg-forest-900 active:scale-[0.99] ring-2 ring-forest-700/50'
        }`}
      >
        {isLoading ? (
          <>
            <Sparkles className="w-4 h-4 animate-spin text-amber-400" />
            <span>Consulting Nature Planner...</span>
          </>
        ) : (
          <>
            <Compass className="w-4 h-4 text-amber-400" />
            <span>Generate Outdoor Micro-Adventure</span>
          </>
        )}
      </button>
    </form>
  );
};

