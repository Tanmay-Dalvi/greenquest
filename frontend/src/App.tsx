import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { PreferenceForm } from './components/PreferenceForm';
import { MissionCard } from './components/MissionCard';
import { MissionChecklist } from './components/MissionChecklist';
import { SafetyNotice } from './components/SafetyNotice';
import { OfflineBanner } from './components/OfflineBanner';
import { HistoryDrawer } from './components/HistoryDrawer';
import {
  MissionPreferenceRequest,
  MissionResponse,
  StoredMissionProgress,
} from './types/mission';
import { requestMission, checkBackendHealth } from './services/api';
import { storage } from './services/storage';
import { RotateCcw, AlertCircle } from 'lucide-react';

export const App: React.FC = () => {
  const [activeMission, setActiveMission] = useState<MissionResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);
  const [history, setHistory] = useState<StoredMissionProgress[]>([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Initialize from local storage and setup network listeners
  useEffect(() => {
    const saved = storage.getActiveMission();
    if (saved) {
      setActiveMission(saved);
    }
    setHistory(storage.getMissionHistory());

    const handleOnline = () => {
      setIsOnline(true);
      checkBackendHealth().then((h) => {
        if (!h.online) setIsOnline(false);
      });
    };
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Initial check
    checkBackendHealth().then((h) => {
      if (!h.online) setIsOnline(false);
    });

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleCreateMission = async (prefs: MissionPreferenceRequest) => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const { mission, usedClientOfflineFallback } = await requestMission(prefs);
      // If the mission was successfully returned by the backend, restore online status
      if (!usedClientOfflineFallback) {
        setIsOnline(true);
      }
      setActiveMission(mission);
      storage.saveActiveMission(mission);
      setHistory(storage.getMissionHistory());
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      console.error('Mission generation failed', err);
      setErrorMsg('Failed to generate mission. Please check your options.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleStep = (stepNumber: number) => {
    if (!activeMission) return;
    const updated = storage.toggleStepCompletion(activeMission.id, stepNumber);
    if (updated) {
      setActiveMission(updated);
      setHistory(storage.getMissionHistory());
    }
  };

  const handleStartNewMission = () => {
    storage.clearActiveMission();
    setActiveMission(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSelectHistoryMission = (mission: MissionResponse) => {
    setActiveMission(mission);
    storage.saveActiveMission(mission);
  };

  const handleClearHistory = () => {
    localStorage.removeItem('greenquest_mission_history');
    setHistory([]);
  };

  return (
    <div className="min-h-screen bg-cream-100 flex flex-col font-sans">
      {/* Top Header */}
      <Header
        isOnline={isOnline}
        onOpenHistory={() => setIsHistoryOpen(true)}
        onResetToForm={handleStartNewMission}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-md w-full mx-auto px-4 py-4 sm:py-6 safe-bottom">
        {errorMsg && (
          <div className="mb-4 p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* View Switch: Active Mission vs Preferences Form */}
        {activeMission ? (
          <div className="space-y-4 animate-fade-in pb-12">
            {/* Model & Generation Metadata */}
            <OfflineBanner
              fallbackUsed={activeMission.generator_info.fallback_used}
              providerName={activeMission.generator_info.provider}
            />

            {/* Structured Mission Card */}
            <MissionCard mission={activeMission} />

            {/* Interactive Step Checklist */}
            <MissionChecklist
              steps={activeMission.steps}
              onToggleStep={handleToggleStep}
            />

            {/* Stewardship & Safety Guidance */}
            <SafetyNotice
              leaveNoTrace={activeMission.leave_no_trace_principle}
              safetyNotes={activeMission.safety_notes}
            />

            {/* Restart Button */}
            <div className="pt-2">
              <button
                type="button"
                onClick={handleStartNewMission}
                className="w-full py-3 px-4 rounded-xl text-xs font-bold border border-cream-300 bg-cream-50 hover:bg-cream-200/80 text-forest-800 transition flex items-center justify-center space-x-1.5 shadow-xs"
              >
                <RotateCcw className="w-3.5 h-3.5 text-sage-500" />
                <span>Start Another Micro-Adventure</span>
              </button>
            </div>
          </div>
        ) : (
          <PreferenceForm
            onSubmit={handleCreateMission}
            isLoading={isLoading}
          />
        )}
      </main>

      {/* History Drawer */}
      <HistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        history={history}
        onSelectMission={handleSelectHistoryMission}
        onClearHistory={handleClearHistory}
      />
    </div>
  );
};
