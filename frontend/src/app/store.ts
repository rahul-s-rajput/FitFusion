import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

interface WorkoutData {
  workout?: {
    name?: string;
    description?: string;
    workout_type?: string;
    duration_minutes?: number;
    difficulty_level?: string;
    estimated_calories?: number;
    warmup?: any[];
    exercises?: any[];
    cooldown?: any[];
    safety_notes?: string[];
    equipment_needed?: string[];
    modifications?: Record<string, any>;
  };
  agentContributions?: any[];
  executionTime?: number;
}

interface WorkoutState {
  generatedWorkout: WorkoutData | null;
  setGeneratedWorkout: (workout: WorkoutData | null) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  error: string | null;
  setError: (error: string | null) => void;
}

export const useWorkout = create<WorkoutState>()(
  immer((set) => ({
    generatedWorkout: null,
    isLoading: false,
    error: null,
    setGeneratedWorkout: (workout) =>
      set((state) => {
        state.generatedWorkout = workout;
        state.error = null;
      }),
    setIsLoading: (loading) =>
      set((state) => {
        state.isLoading = loading;
      }),
    setError: (error) =>
      set((state) => {
        state.error = error;
        state.isLoading = false;
      }),
  }))
);
