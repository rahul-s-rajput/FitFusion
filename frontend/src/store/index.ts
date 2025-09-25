/**
 * Zustand Store Setup for FitFusion AI Workout App
 * Manages global application state with offline-first architecture
 */

import { create } from 'zustand';
import { shallow } from 'zustand/shallow';
import { subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { persist, createJSONStorage } from 'zustand/middleware';
import { UserProfile, Equipment, WorkoutProgram, WorkoutSession, ProgressRecord } from '../lib/db';

// Types for store state
export interface User {
  id?: string;
  profile?: UserProfile;
  isAuthenticated: boolean;
  preferences: {
    theme: 'light' | 'dark' | 'system';
    notifications: boolean;
    offlineMode: boolean;
    syncEnabled: boolean;
  };
}

export interface GeneratedWorkoutResult {
  workout: any;
  agentContributions?: any[];
  executionTime?: number;
  completedAt?: string;
}

export interface WorkoutState {
  activeProgram?: WorkoutProgram;
  currentSession?: WorkoutSession;
  todaySessions: WorkoutSession[];
  recentPrograms: WorkoutProgram[];
  isGenerating: boolean;
  generationProgress: number;
  generationMessage: string;
  generationTaskId?: string;
  generatedWorkout: GeneratedWorkoutResult | null;
  generationError: string | null;
}

export interface EquipmentState {
  inventory: Equipment[];
  availableEquipment: Equipment[];
  suggestions: any[];
  isLoading: boolean;
}

export interface ProgressState {
  recentRecords: ProgressRecord[];
  stats: {
    totalWorkouts: number;
    currentStreak: number;
    longestStreak: number;
    totalWorkoutTime: number;
    favoriteWorkoutType: string;
  };
  achievements: any[];
  isLoading: boolean;
}

export interface SyncState {
  isOnline: boolean;
  lastSyncTime?: Date;
  pendingSync: number;
  syncInProgress: boolean;
  syncError?: string;
}

export interface UIState {
  sidebarOpen: boolean;
  currentPage: string;
  loading: {
    global: boolean;
    components: Record<string, boolean>;
  };
  notifications: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    title: string;
    message: string;
    timestamp: Date;
    read: boolean;
  }>;
  modals: {
    workoutGeneration: boolean;
    equipmentAdd: boolean;
    sessionComplete: boolean;
    profileSetup: boolean;
  };
}

// Combined store interface
export interface AppStore {
  // State
  user: User;
  workout: WorkoutState;
  equipment: EquipmentState;
  progress: ProgressState;
  sync: SyncState;
  ui: UIState;

  // User Actions
  setUser: (user: Partial<User>) => void;
  updateUserProfile: (profile: Partial<UserProfile>) => void;
  setAuthenticated: (authenticated: boolean) => void;
  updatePreferences: (preferences: Partial<User['preferences']>) => void;

  // Workout Actions
  setActiveProgram: (program?: WorkoutProgram) => void;
  setCurrentSession: (session?: WorkoutSession) => void;
  updateTodaySessions: (sessions: WorkoutSession[]) => void;
  updateRecentPrograms: (programs: WorkoutProgram[]) => void;
  setGenerationState: (isGenerating: boolean, progress?: number, message?: string) => void;
  startWorkoutGeneration: () => void;
  setGenerationTaskId: (taskId: string | null) => void;
  completeWorkoutGeneration: (payload: GeneratedWorkoutResult) => void;
  setGenerationError: (error?: string) => void;

  // Equipment Actions
  setEquipmentInventory: (equipment: Equipment[]) => void;
  addEquipment: (equipment: Equipment) => void;
  updateEquipment: (id: number, updates: Partial<Equipment>) => void;
  removeEquipment: (id: number) => void;
  setEquipmentSuggestions: (suggestions: any[]) => void;
  setEquipmentLoading: (loading: boolean) => void;

  // Progress Actions
  setRecentRecords: (records: ProgressRecord[]) => void;
  addProgressRecord: (record: ProgressRecord) => void;
  updateStats: (stats: Partial<ProgressState['stats']>) => void;
  setAchievements: (achievements: any[]) => void;
  setProgressLoading: (loading: boolean) => void;

  // Sync Actions
  setOnlineStatus: (online: boolean) => void;
  updateSyncState: (state: Partial<SyncState>) => void;
  incrementPendingSync: () => void;
  decrementPendingSync: () => void;
  setSyncError: (error?: string) => void;

  // UI Actions
  setSidebarOpen: (open: boolean) => void;
  setCurrentPage: (page: string) => void;
  setGlobalLoading: (loading: boolean) => void;
  setComponentLoading: (component: string, loading: boolean) => void;
  addNotification: (notification: Omit<UIState['notifications'][0], 'id' | 'timestamp' | 'read'>) => void;
  markNotificationRead: (id: string) => void;
  removeNotification: (id: string) => void;
  setModalOpen: (modal: keyof UIState['modals'], open: boolean) => void;

  // Utility Actions
  reset: () => void;
  hydrate: () => Promise<void>;
}

// Initial state
const initialState = {
  user: {
    isAuthenticated: false,
    preferences: {
      theme: 'system' as const,
      notifications: true,
      offlineMode: false,
      syncEnabled: true,
    },
  },
  workout: {
    todaySessions: [],
    recentPrograms: [],
    isGenerating: false,
    generationProgress: 0,
    generationMessage: 'Ready to generate your next workout.',
    generationTaskId: undefined,
    generatedWorkout: null,
    generationError: null,
  },
  equipment: {
    inventory: [],
    availableEquipment: [],
    suggestions: [],
    isLoading: false,
  },
  progress: {
    recentRecords: [],
    stats: {
      totalWorkouts: 0,
      currentStreak: 0,
      longestStreak: 0,
      totalWorkoutTime: 0,
      favoriteWorkoutType: '',
    },
    achievements: [],
    isLoading: false,
  },
  sync: {
    isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
    pendingSync: 0,
    syncInProgress: false,
  },
  ui: {
    sidebarOpen: false,
    currentPage: 'home',
    loading: {
      global: false,
      components: {},
    },
    notifications: [],
    modals: {
      workoutGeneration: false,
      equipmentAdd: false,
      sessionComplete: false,
      profileSetup: false,
    },
  },
};

// Create the store with middleware
export const useAppStore = create<AppStore>()(
  subscribeWithSelector(
    immer(
      persist(
        (set, get) => ({
          ...initialState,

          // User Actions
          setUser: (user) =>
            set((state) => {
              Object.assign(state.user, user);
            }),

          updateUserProfile: (profile) =>
            set((state) => {
              if (state.user.profile) {
                Object.assign(state.user.profile, profile);
              } else {
                state.user.profile = profile as UserProfile;
              }
            }),

          setAuthenticated: (authenticated) =>
            set((state) => {
              state.user.isAuthenticated = authenticated;
            }),

          updatePreferences: (preferences) =>
            set((state) => {
              Object.assign(state.user.preferences, preferences);
            }),

          // Workout Actions
          setActiveProgram: (program) =>
            set((state) => {
              state.workout.activeProgram = program;
            }),

          setCurrentSession: (session) =>
            set((state) => {
              state.workout.currentSession = session;
            }),

          updateTodaySessions: (sessions) =>
            set((state) => {
              state.workout.todaySessions = sessions;
            }),

          updateRecentPrograms: (programs) =>
            set((state) => {
              state.workout.recentPrograms = programs;
            }),

          setGenerationState: (isGenerating, progress, message) =>
            set((state) => {
              state.workout.isGenerating = isGenerating;
              if (typeof progress === 'number') {
                state.workout.generationProgress = progress;
              }
              if (typeof message === 'string') {
                state.workout.generationMessage = message;
              }
            }),

          startWorkoutGeneration: () =>
            set((state) => {
              state.workout.isGenerating = true;
              state.workout.generationProgress = 0;
              state.workout.generationMessage = 'Initializing AI agents...';
              state.workout.generationTaskId = undefined;
              state.workout.generatedWorkout = null;
              state.workout.generationError = null;
            }),

          setGenerationTaskId: (taskId) =>
            set((state) => {
              state.workout.generationTaskId = taskId || undefined;
            }),

          completeWorkoutGeneration: (payload) =>
            set((state) => {
              state.workout.isGenerating = false;
              state.workout.generationProgress = 100;
              state.workout.generationMessage = 'Workout generated successfully!';
              state.workout.generatedWorkout = {
                workout: payload.workout,
                agentContributions: payload.agentContributions || [],
                executionTime: payload.executionTime,
                completedAt: payload.completedAt,
              };

              if (payload.workout) {
                const summaryProgram: WorkoutProgram = {
                  id: payload.workout.workout_id || Date.now(),
                  user_id: undefined,
                  name: payload.workout.name || 'AI Generated Workout',
                  description: payload.workout.description || '',
                  duration_days: 1,
                  difficulty_level: (payload.workout.difficulty_level || 'beginner') as any,
                  daily_schedules: payload.workout.exercises,
                  ai_generation_metadata: {
                    agentContributions: payload.agentContributions || [],
                    executionTime: payload.executionTime,
                    equipmentNeeded: payload.workout.equipment_needed,
                  },
                  is_active: false,
                  completion_percentage: 0,
                  created_at: new Date(),
                  updated_at: new Date(),
                  sync_status: 'pending',
                };
                state.workout.recentPrograms.unshift(summaryProgram);
                if (state.workout.recentPrograms.length > 10) {
                  state.workout.recentPrograms = state.workout.recentPrograms.slice(0, 10);
                }
              }

              state.workout.generationTaskId = undefined;
              state.workout.generationError = null;
            }),

          setGenerationError: (error) =>
            set((state) => {
              state.workout.generationError = error || null;
              if (error) {
                state.workout.generationMessage = error;
                state.workout.isGenerating = false;
              }
            }),

          // Equipment Actions
          setEquipmentInventory: (equipment) =>
            set((state) => {
              state.equipment.inventory = equipment;
              state.equipment.availableEquipment = equipment.filter(e => e.is_available);
            }),

          addEquipment: (equipment) =>
            set((state) => {
              state.equipment.inventory.push(equipment);
              if (equipment.is_available) {
                state.equipment.availableEquipment.push(equipment);
              }
            }),

          updateEquipment: (id, updates) =>
            set((state) => {
              const index = state.equipment.inventory.findIndex(e => e.id === id);
              if (index !== -1) {
                Object.assign(state.equipment.inventory[index], updates);
                // Update available equipment list
                state.equipment.availableEquipment = state.equipment.inventory.filter(e => e.is_available);
              }
            }),

          removeEquipment: (id) =>
            set((state) => {
              state.equipment.inventory = state.equipment.inventory.filter(e => e.id !== id);
              state.equipment.availableEquipment = state.equipment.availableEquipment.filter(e => e.id !== id);
            }),

          setEquipmentSuggestions: (suggestions) =>
            set((state) => {
              state.equipment.suggestions = suggestions;
            }),

          setEquipmentLoading: (loading) =>
            set((state) => {
              state.equipment.isLoading = loading;
            }),

          // Progress Actions
          setRecentRecords: (records) =>
            set((state) => {
              state.progress.recentRecords = records;
            }),

          addProgressRecord: (record) =>
            set((state) => {
              state.progress.recentRecords.unshift(record);
              // Keep only recent 50 records
              if (state.progress.recentRecords.length > 50) {
                state.progress.recentRecords = state.progress.recentRecords.slice(0, 50);
              }
            }),

          updateStats: (stats) =>
            set((state) => {
              Object.assign(state.progress.stats, stats);
            }),

          setAchievements: (achievements) =>
            set((state) => {
              state.progress.achievements = achievements;
            }),

          setProgressLoading: (loading) =>
            set((state) => {
              state.progress.isLoading = loading;
            }),

          // Sync Actions
          setOnlineStatus: (online) =>
            set((state) => {
              state.sync.isOnline = online;
            }),

          updateSyncState: (syncState) =>
            set((state) => {
              Object.assign(state.sync, syncState);
            }),

          incrementPendingSync: () =>
            set((state) => {
              state.sync.pendingSync += 1;
            }),

          decrementPendingSync: () =>
            set((state) => {
              state.sync.pendingSync = Math.max(0, state.sync.pendingSync - 1);
            }),

          setSyncError: (error) =>
            set((state) => {
              state.sync.syncError = error;
            }),

          // UI Actions
          setSidebarOpen: (open) =>
            set((state) => {
              state.ui.sidebarOpen = open;
            }),

          setCurrentPage: (page) =>
            set((state) => {
              state.ui.currentPage = page;
            }),

          setGlobalLoading: (loading) =>
            set((state) => {
              state.ui.loading.global = loading;
            }),

          setComponentLoading: (component, loading) =>
            set((state) => {
              state.ui.loading.components[component] = loading;
            }),

          addNotification: (notification) =>
            set((state) => {
              const id = Date.now().toString() + Math.random().toString(36).substr(2, 9);
              if (!Array.isArray(state.ui.notifications)) {
                state.ui.notifications = [];
              }
              state.ui.notifications.unshift({
                ...notification,
                id,
                timestamp: new Date(),
                read: false,
              });
              // Keep only recent 20 notifications
              if (state.ui.notifications.length > 20) {
                state.ui.notifications = state.ui.notifications.slice(0, 20);
              }
            }),

          markNotificationRead: (id) =>
            set((state) => {
              const notification = state.ui.notifications.find(n => n.id === id);
              if (notification) {
                notification.read = true;
              }
            }),

          removeNotification: (id) =>
            set((state) => {
              state.ui.notifications = state.ui.notifications.filter(n => n.id !== id);
            }),

          setModalOpen: (modal, open) =>
            set((state) => {
              state.ui.modals[modal] = open;
            }),

          // Utility Actions
          reset: () => set(initialState),

          hydrate: async () => {
            // This would load initial data from IndexedDB
            // Implementation would go here
          },
        }),
        {
          name: 'fitfusion-store',
          storage: createJSONStorage(() => localStorage),
          partialize: (state) => ({
            user: {
              preferences: state.user.preferences,
              profile: state.user.profile,
            },
            ui: {
              sidebarOpen: state.ui.sidebarOpen,
              currentPage: state.ui.currentPage,
            },
          }),
          merge: (persistedState: any, currentState: any) => {
            const merged = {
              ...currentState,
              ...persistedState,
            };

            if (persistedState?.user) {
              merged.user = {
                ...currentState.user,
                ...persistedState.user,
              };
            }

            if (persistedState?.ui) {
              merged.ui = {
                ...currentState.ui,
                ...persistedState.ui,
              };
            }

            if (!Array.isArray(merged.ui.notifications)) {
              merged.ui.notifications = currentState.ui.notifications;
            }

            if (!merged.ui.loading) {
              merged.ui.loading = currentState.ui.loading;
            } else {
              merged.ui.loading = {
                global: merged.ui.loading.global ?? currentState.ui.loading.global,
                components: {
                  ...currentState.ui.loading.components,
                  ...(merged.ui.loading.components || {}),
                },
              };
            }

            return merged;
          },
        }
      )
    )
  )
);

// Selectors for common state access patterns
export const useUser = () => useAppStore((state) => state.user);
export const useWorkout = () => useAppStore((state) => state.workout);
export const useEquipment = () => useAppStore((state) => state.equipment);
export const useProgress = () => useAppStore((state) => state.progress);
export const useSync = () => useAppStore((state) => state.sync);
export const useUI = () => useAppStore((state) => state.ui);

// Action selectors
export const useUserActions = () => ({
  setUser: useAppStore((state) => state.setUser),
  updateUserProfile: useAppStore((state) => state.updateUserProfile),
  setAuthenticated: useAppStore((state) => state.setAuthenticated),
  updatePreferences: useAppStore((state) => state.updatePreferences),
});

export const useWorkoutActions = () => ({
  setActiveProgram: useAppStore((state) => state.setActiveProgram),
  setCurrentSession: useAppStore((state) => state.setCurrentSession),
  updateTodaySessions: useAppStore((state) => state.updateTodaySessions),
  updateRecentPrograms: useAppStore((state) => state.updateRecentPrograms),
  setGenerationState: useAppStore((state) => state.setGenerationState),
  startWorkoutGeneration: useAppStore((state) => state.startWorkoutGeneration),
  setGenerationTaskId: useAppStore((state) => state.setGenerationTaskId),
  completeWorkoutGeneration: useAppStore((state) => state.completeWorkoutGeneration),
  setGenerationError: useAppStore((state) => state.setGenerationError),
});

export const useEquipmentActions = () => ({
  setEquipmentInventory: useAppStore((state) => state.setEquipmentInventory),
  addEquipment: useAppStore((state) => state.addEquipment),
  updateEquipment: useAppStore((state) => state.updateEquipment),
  removeEquipment: useAppStore((state) => state.removeEquipment),
  setEquipmentSuggestions: useAppStore((state) => state.setEquipmentSuggestions),
  setEquipmentLoading: useAppStore((state) => state.setEquipmentLoading),
});

export const useProgressActions = () => ({
  setRecentRecords: useAppStore((state) => state.setRecentRecords),
  addProgressRecord: useAppStore((state) => state.addProgressRecord),
  updateStats: useAppStore((state) => state.updateStats),
  setAchievements: useAppStore((state) => state.setAchievements),
  setProgressLoading: useAppStore((state) => state.setProgressLoading),
});

export const useSyncActions = () => ({
  setOnlineStatus: useAppStore((state) => state.setOnlineStatus),
  updateSyncState: useAppStore((state) => state.updateSyncState),
  incrementPendingSync: useAppStore((state) => state.incrementPendingSync),
  decrementPendingSync: useAppStore((state) => state.decrementPendingSync),
  setSyncError: useAppStore((state) => state.setSyncError),
});

export const useUIActions = () => ({
  setSidebarOpen: useAppStore((state) => state.setSidebarOpen),
  setCurrentPage: useAppStore((state) => state.setCurrentPage),
  setGlobalLoading: useAppStore((state) => state.setGlobalLoading),
  setComponentLoading: useAppStore((state) => state.setComponentLoading),
  addNotification: useAppStore((state) => state.addNotification),
  markNotificationRead: useAppStore((state) => state.markNotificationRead),
  removeNotification: useAppStore((state) => state.removeNotification),
  setModalOpen: useAppStore((state) => state.setModalOpen),
});




