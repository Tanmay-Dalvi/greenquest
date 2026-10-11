import { MissionResponse, StoredMissionProgress } from '../types/mission';

const ACTIVE_MISSION_KEY = 'greenquest_active_mission';
const HISTORY_KEY = 'greenquest_mission_history';

export const storage = {
  getActiveMission(): MissionResponse | null {
    try {
      const data = localStorage.getItem(ACTIVE_MISSION_KEY);
      return data ? JSON.parse(data) : null;
    } catch {
      return null;
    }
  },

  saveActiveMission(mission: MissionResponse): void {
    try {
      localStorage.setItem(ACTIVE_MISSION_KEY, JSON.stringify(mission));
      this.syncToHistory(mission);
    } catch (err) {
      console.warn('LocalStorage save failed', err);
    }
  },

  clearActiveMission(): void {
    try {
      localStorage.removeItem(ACTIVE_MISSION_KEY);
    } catch (err) {
      console.warn('LocalStorage clear failed', err);
    }
  },

  toggleStepCompletion(missionId: string, stepNumber: number): MissionResponse | null {
    const active = this.getActiveMission();
    if (!active || active.id !== missionId) return null;

    const updatedSteps = active.steps.map((step) => {
      if (step.step_number === stepNumber) {
        return { ...step, completed: !step.completed };
      }
      return step;
    });

    const updatedMission: MissionResponse = {
      ...active,
      steps: updatedSteps,
    };

    this.saveActiveMission(updatedMission);
    return updatedMission;
  },

  getMissionHistory(): StoredMissionProgress[] {
    try {
      const data = localStorage.getItem(HISTORY_KEY);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  },

  syncToHistory(mission: MissionResponse): void {
    try {
      const history = this.getMissionHistory();
      const completedIndices = mission.steps
        .filter((s) => s.completed)
        .map((s) => s.step_number);
      const isFullyCompleted =
        mission.steps.length > 0 && completedIndices.length === mission.steps.length;

      const existingIndex = history.findIndex((h) => h.mission.id === mission.id);
      const entry: StoredMissionProgress = {
        mission,
        completedStepIndices: completedIndices,
        isFullyCompleted,
        lastUpdated: new Date().toISOString(),
      };

      if (existingIndex >= 0) {
        history[existingIndex] = entry;
      } else {
        history.unshift(entry);
      }

      // Keep up to 20 past missions locally
      localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, 20)));
    } catch (err) {
      console.warn('Failed to sync mission history', err);
    }
  },
};

