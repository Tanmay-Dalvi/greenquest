export type EnvironmentType =
  | 'park'
  | 'forest'
  | 'neighborhood'
  | 'garden'
  | 'waterfront'
  | 'trail';

export type MoodType =
  | 'mindful'
  | 'curious'
  | 'playful'
  | 'contemplative'
  | 'energized';

export type EnergyLevel = 'low' | 'moderate' | 'brisk';

export type CompanionType = 'solo' | 'family' | 'friends' | 'dog';

export type SensoryType = 'sight' | 'sound' | 'touch' | 'scent' | 'spatial';

export type DifficultyLevel = 'easy' | 'moderate' | 'challenging';

export interface MissionPreferenceRequest {
  duration_minutes: number;
  environment: EnvironmentType;
  mood: MoodType;
  energy_level: EnergyLevel;
  companion_type: CompanionType;
  sensory_focus: SensoryType[];
  notes?: string;
}

export interface MissionStep {
  step_number: number;
  title: string;
  instruction: string;
  sensory_type: SensoryType;
  estimated_minutes: number;
  completed: boolean;
}

export interface GeneratorInfo {
  provider: string;
  model: string;
  fallback_used: boolean;
  generation_time_ms: number;
  safety_validated: boolean;
}

export interface MissionResponse {
  id: string;
  title: string;
  tagline: string;
  environment: EnvironmentType;
  estimated_duration_minutes: number;
  difficulty: DifficultyLevel;
  theme: string;
  sensory_prompt: string;
  leave_no_trace_principle: string;
  safety_notes: string[];
  steps: MissionStep[];
  generator_info: GeneratorInfo;
  created_at: string;
}

export interface StoredMissionProgress {
  mission: MissionResponse;
  completedStepIndices: number[];
  isFullyCompleted: boolean;
  lastUpdated: string;
}

