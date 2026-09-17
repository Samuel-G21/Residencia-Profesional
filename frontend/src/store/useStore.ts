import { create } from 'zustand';

interface AppState {
  currentPhase: number;
  setCurrentPhase: (phase: number) => void;
  loadingMessage: string;
  setLoadingMessage: (msg: string) => void;
}

export const useStore = create<AppState>((set) => ({
  currentPhase: 1,
  setCurrentPhase: (phase) => set({ currentPhase: phase }),
  loadingMessage: '',
  setLoadingMessage: (msg) => set({ loadingMessage: msg }),
}));
