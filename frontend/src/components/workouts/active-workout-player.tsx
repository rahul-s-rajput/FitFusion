'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import {
  CheckCircle2,
  Pause,
  Play,
  RotateCcw,
  SkipForward,
  Timer,
  Zap,
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';

export type WorkoutSection = 'warmup' | 'main' | 'cooldown';

export interface WorkoutStep {
  id: string;
  name: string;
  section: WorkoutSection;
  sets?: number;
  reps?: number;
  durationSeconds?: number;
  restSeconds?: number;
  instructions?: string;
  equipment?: string[];
  targetMuscles?: string[];
  mediaUrl?: string;
}

export interface WorkoutSummary {
  completedSteps: number;
  skippedSteps: number;
  totalSteps: number;
  totalElapsedSeconds: number;
  estimatedCalories?: number;
}

interface ActiveWorkoutPlayerProps {
  steps: WorkoutStep[];
  onExit?: () => void;
  onComplete?: (summary: WorkoutSummary) => void;
}

interface StepProgressState {
  status: 'pending' | 'completed' | 'skipped';
  completedSets: number;
}

const sectionLabelMap: Record<WorkoutSection, string> = {
  warmup: 'Warm-up',
  main: 'Main',
  cooldown: 'Cooldown',
};

const sectionBadgeClass: Record<WorkoutSection, string> = {
  warmup: 'bg-amber-500/10 text-amber-700',
  main: 'bg-emerald-500/10 text-emerald-700',
  cooldown: 'bg-sky-500/10 text-sky-700',
};

const formatClock = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
    .toString()
    .padStart(2, '0');
  const secs = Math.floor(seconds % 60)
    .toString()
    .padStart(2, '0');
  return `${mins}:${secs}`;
};

const estimateCalories = (steps: WorkoutStep[], totalSeconds: number) => {
  if (!totalSeconds) return undefined;
  const mets = 7.5;
  const weightKg = 75;
  const caloriesPerMinute = (mets * 3.5 * weightKg) / 200;
  return Math.max(1, Math.round((totalSeconds / 60) * caloriesPerMinute));
};

type RestPhase = 'between-sets' | 'between-steps';

type DurationSource = 'auto' | 'manual';

export function ActiveWorkoutPlayer({ steps, onExit, onComplete }: ActiveWorkoutPlayerProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentSet, setCurrentSet] = useState(1);
  const [isActive, setIsActive] = useState(false);
  const [isResting, setIsResting] = useState(false);
  const [restPhase, setRestPhase] = useState<RestPhase | null>(null);
  const [exerciseRemaining, setExerciseRemaining] = useState(steps[0]?.durationSeconds ?? 0);
  const [restRemaining, setRestRemaining] = useState(0);
  const [workoutElapsed, setWorkoutElapsed] = useState(0);
  const [stepStates, setStepStates] = useState<StepProgressState[]>(() =>
    steps.map(() => ({ status: 'pending', completedSets: 0 }))
  );
  const hasFinishedRef = useRef(false);

  useEffect(() => {
    setCurrentIndex(0);
    setCurrentSet(1);
    setIsActive(false);
    setIsResting(false);
    setRestPhase(null);
    setExerciseRemaining(steps[0]?.durationSeconds ?? 0);
    setRestRemaining(0);
    setWorkoutElapsed(0);
    setStepStates(steps.map(() => ({ status: 'pending', completedSets: 0 })));
    hasFinishedRef.current = false;
  }, [steps]);

  const currentStep = steps[currentIndex];
  const totalSteps = steps.length;

  const completedSteps = useMemo(
    () => stepStates.filter((state) => state.status === 'completed').length,
    [stepStates]
  );
  const skippedSteps = useMemo(
    () => stepStates.filter((state) => state.status === 'skipped').length,
    [stepStates]
  );

  const progressPercent = useMemo(() => {
    if (totalSteps === 0) return 0;
    return ((completedSteps + skippedSteps) / totalSteps) * 100;
  }, [completedSteps, skippedSteps, totalSteps]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (!isActive) return;
    if (!totalSteps) return;

    const timer = window.setInterval(() => {
      setWorkoutElapsed((prev) => prev + 1);

      if (isResting) {
        setRestRemaining((prev) => {
          if (prev <= 1) {
            window.setTimeout(() => finishRestPhase(), 0);
            return 0;
          }
          return prev - 1;
        });
        return;
      }

      const step = steps[currentIndex];
      if (!step?.durationSeconds) {
        return;
      }

      setExerciseRemaining((prev) => {
        if (prev <= 1) {
          window.setTimeout(() => handleDurationCompletion('auto'), 0);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => window.clearInterval(timer);
  }, [isActive, isResting, currentIndex, steps, totalSteps]);

  const finishWorkout = () => {
    if (hasFinishedRef.current) return;
    hasFinishedRef.current = true;
    setIsActive(false);
    const summary: WorkoutSummary = {
      completedSteps,
      skippedSteps,
      totalSteps,
      totalElapsedSeconds: workoutElapsed,
      estimatedCalories: estimateCalories(steps, workoutElapsed),
    };
    onComplete?.(summary);
  };

  useEffect(() => {
    if (currentIndex >= totalSteps && totalSteps > 0) {
      finishWorkout();
    }
  }, [currentIndex, totalSteps]);

  const startWorkout = () => {
    if (!currentStep) return;
    if (currentStep.durationSeconds && exerciseRemaining <= 0) {
      setExerciseRemaining(currentStep.durationSeconds);
    }
    setIsActive(true);
  };

  const pauseWorkout = () => {
    setIsActive(false);
  };

  const resetTimerForCurrent = () => {
    const step = steps[currentIndex];
    if (!step?.durationSeconds) return;
    setExerciseRemaining(step.durationSeconds);
  };

  const completeSetOrExercise = () => {
    const step = steps[currentIndex];
    if (!step) return;

    const totalSets = step.sets && step.sets > 0 ? step.sets : 1;

    setStepStates((prev) =>
      prev.map((state, index) =>
        index === currentIndex
          ? { ...state, completedSets: Math.min(state.completedSets + 1, totalSets) }
          : state
      )
    );

    if (currentSet >= totalSets) {
      markStepCompleted();
    } else {
      startRestPhase('between-sets');
    }
  };

  const handleDurationCompletion = (source: DurationSource) => {
    const step = steps[currentIndex];
    if (!step) return;

    const totalSets = step.sets && step.sets > 0 ? step.sets : 1;

    setStepStates((prev) =>
      prev.map((state, index) =>
        index === currentIndex
          ? { ...state, completedSets: Math.min(state.completedSets + 1, totalSets) }
          : state
      )
    );

    if (totalSets > 1 && currentSet < totalSets) {
      startRestPhase('between-sets');
      return;
    }

    markStepCompleted();
  };

  const skipCurrentStep = () => {
    if (!currentStep) return;

    setStepStates((prev) =>
      prev.map((state, index) =>
        index === currentIndex ? { ...state, status: 'skipped' } : state
      )
    );

    moveToNextStep();
  };

  const markStepCompleted = () => {
    const step = steps[currentIndex];
    if (!step) return;

    setStepStates((prev) =>
      prev.map((state, index) =>
        index === currentIndex
          ? {
              status: 'completed',
              completedSets: Math.max(state.completedSets, step.sets && step.sets > 0 ? step.sets : 1),
            }
          : state
      )
    );

    if (step.restSeconds && step.restSeconds > 0 && currentIndex < totalSteps - 1) {
      startRestPhase('between-steps');
    } else {
      moveToNextStep();
    }
  };

  const startRestPhase = (phase: RestPhase) => {
    const step = steps[currentIndex];
    const restValue = step?.restSeconds ?? 0;

    setIsResting(true);
    setRestPhase(phase);
    setExerciseRemaining(0);

    if (restValue > 0) {
      setRestRemaining(restValue);
    } else {
      window.setTimeout(() => finishRestPhase(), 0);
    }
  };

  const finishRestPhase = () => {
    const step = steps[currentIndex];
    setIsResting(false);
    const phase = restPhase;
    setRestPhase(null);

    if (phase === 'between-sets' && step) {
      setCurrentSet((prev) => prev + 1);
      if (step.durationSeconds) {
        setExerciseRemaining(step.durationSeconds);
      }
    } else if (phase === 'between-steps') {
      moveToNextStep();
    }
  };

  const moveToNextStep = () => {
    const nextIndex = currentIndex + 1;
    if (nextIndex >= totalSteps) {
      setCurrentIndex(nextIndex);
      return;
    }

    setCurrentIndex(nextIndex);
    setCurrentSet(1);
    setExerciseRemaining(steps[nextIndex]?.durationSeconds ?? 0);
    setRestRemaining(0);
    setIsResting(false);
    setRestPhase(null);
  };

  if (steps.length === 0) {
    return (
      <Card className="border-dashed border-border/60 bg-muted/40">
        <CardContent className="py-12 text-center text-sm text-muted-foreground">
          No workout steps available yet.
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-5">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle className="text-base font-semibold">Workout Progress</CardTitle>
          <Badge variant="secondary" className="bg-primary/10 text-primary">
            {completedSteps}/{totalSteps} done
          </Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-end justify-between">
            <div>
              <div className="text-xs uppercase tracking-wide text-muted-foreground">Total Time</div>
              <div className="text-3xl font-semibold tracking-tight">{formatClock(workoutElapsed)}</div>
            </div>
            <div className="text-right text-sm text-muted-foreground">
              {sectionLabelMap[currentStep.section]}
            </div>
          </div>
          <Progress value={progressPercent} className="h-2" />
        </CardContent>
      </Card>

      <AnimatePresence mode="wait">
        {isResting ? (
          <motion.div
            key="rest"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="border-orange-200 bg-orange-50">
              <CardContent className="flex flex-col items-center space-y-4 py-8">
                <div className="flex items-center gap-2 rounded-full bg-white/60 px-4 py-1 text-xs font-semibold uppercase tracking-wide text-orange-700">
                  <Timer className="h-4 w-4" /> Rest
                </div>
                <div className="font-mono text-5xl font-semibold text-orange-600">
                  {formatClock(restRemaining)}
                </div>
                <p className="text-sm text-orange-800">
                  Breathe and reset. {restPhase === 'between-sets' ? 'Next set starting soon.' : 'Next exercise up next.'}
                </p>
                <div className="flex flex-wrap items-center gap-3">
                  <Button onClick={finishRestPhase} variant="outline">
                    Skip Rest
                  </Button>
                  <Button onClick={isActive ? pauseWorkout : startWorkout} variant="ghost">
                    {isActive ? (
                      <>
                        <Pause className="mr-2 h-4 w-4" /> Pause Timer
                      </>
                    ) : (
                      <>
                        <Play className="mr-2 h-4 w-4" /> Resume
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ) : (
          <motion.div
            key={currentStep.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="border-border/60">
              <CardHeader className="space-y-2">
                <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  <Badge variant="outline" className={sectionBadgeClass[currentStep.section]}>
                    {sectionLabelMap[currentStep.section]}
                  </Badge>
                  <span className="text-muted-foreground">Step {currentIndex + 1} of {totalSteps}</span>
                </div>
                <CardTitle className="text-2xl font-semibold">
                  {currentStep.name}
                </CardTitle>
                {currentStep.instructions && (
                  <p className="text-sm text-muted-foreground">{currentStep.instructions}</p>
                )}
              </CardHeader>
              <CardContent className="space-y-5">
                <div className="grid grid-cols-2 gap-3 text-sm md:grid-cols-4">
                  {currentStep.sets && (
                    <div className="rounded-xl border border-border/60 bg-muted/40 p-3 text-center">
                      <div className="text-xs uppercase tracking-wide text-muted-foreground">Sets</div>
                      <div className="mt-1 text-xl font-semibold">
                        {currentSet}/{currentStep.sets}
                      </div>
                    </div>
                  )}
                  {currentStep.reps && (
                    <div className="rounded-xl border border-border/60 bg-muted/40 p-3 text-center">
                      <div className="text-xs uppercase tracking-wide text-muted-foreground">Reps</div>
                      <div className="mt-1 text-xl font-semibold">{currentStep.reps}</div>
                    </div>
                  )}
                  {currentStep.durationSeconds && (
                    <div className="rounded-xl border border-border/60 bg-muted/40 p-3 text-center">
                      <div className="text-xs uppercase tracking-wide text-muted-foreground">Duration</div>
                      <div className="mt-1 font-mono text-xl font-semibold">{formatClock(exerciseRemaining)}</div>
                    </div>
                  )}
                  <div className="rounded-xl border border-border/60 bg-muted/40 p-3 text-center">
                    <div className="text-xs uppercase tracking-wide text-muted-foreground">Rest</div>
                    <div className="mt-1 text-xl font-semibold">{currentStep.restSeconds ?? 0}s</div>
                  </div>
                </div>

                {currentStep.targetMuscles && currentStep.targetMuscles.length > 0 && (
                  <div>
                    <div className="text-xs uppercase tracking-wide text-muted-foreground">Target muscles</div>
                    <div className="mt-2 flex flex-wrap gap-2 text-xs">
                      {currentStep.targetMuscles.map((muscle) => (
                        <Badge key={muscle} variant="secondary" className="capitalize">
                          {muscle}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {currentStep.equipment && currentStep.equipment.length > 0 && (
                  <div className="text-xs text-muted-foreground">
                    Equipment: {currentStep.equipment.join(', ')}
                  </div>
                )}

                <div className="flex flex-wrap items-center gap-3">
                  {!isActive ? (
                    <Button onClick={startWorkout} className="flex-1">
                      <Play className="mr-2 h-4 w-4" /> Start Workout
                    </Button>
                  ) : (
                    <>
                      <Button variant="outline" onClick={pauseWorkout}>
                        <Pause className="mr-2 h-4 w-4" /> Pause
                      </Button>
                      {currentStep.durationSeconds ? (
                        <Button onClick={() => handleDurationCompletion('manual')} className="flex-1">
                          <CheckCircle2 className="mr-2 h-4 w-4" /> Mark Complete
                        </Button>
                      ) : (
                        <Button onClick={completeSetOrExercise} className="flex-1">
                          <CheckCircle2 className="mr-2 h-4 w-4" />
                          {currentStep.sets && currentSet < currentStep.sets ? 'Complete Set' : 'Complete Exercise'}
                        </Button>
                      )}
                      <Button variant="outline" onClick={skipCurrentStep}>
                        <SkipForward className="mr-2 h-4 w-4" /> Skip
                      </Button>
                    </>
                  )}
                  {currentStep.durationSeconds && isActive && (
                    <Button variant="ghost" onClick={resetTimerForCurrent}>
                      <RotateCcw className="mr-2 h-4 w-4" /> Reset Timer
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      <Card className="border-border/60">
        <CardHeader>
          <CardTitle className="text-base">Exercise Overview</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {steps.map((step, index) => {
            const state = stepStates[index];
            const isCurrent = index === currentIndex && !isResting;
            const statusBadge = state.status === 'completed'
              ? 'bg-emerald-500 text-white'
              : state.status === 'skipped'
              ? 'bg-muted text-muted-foreground'
              : 'bg-muted';

            return (
              <div
                key={step.id}
                className={`flex items-center justify-between rounded-xl border p-3 ${
                  isCurrent
                    ? 'border-primary bg-primary/5'
                    : state.status === 'completed'
                    ? 'border-emerald-200 bg-emerald-50'
                    : 'border-border/60 bg-muted/20'
                }`}
              >
                <div>
                  <div className="font-medium">{step.name}</div>
                  <div className="text-xs text-muted-foreground">
                    {sectionLabelMap[step.section]} - {step.sets ? `${step.sets} sets` : step.durationSeconds ? `${Math.max(1, Math.round(step.durationSeconds / 60))} min` : '1 set'}
                  </div>
                </div>
                <div className={`flex h-6 w-6 items-center justify-center rounded-full text-[10px] font-semibold ${statusBadge}`}>
                  {state.status === 'completed' ? index + 1 : state.status === 'skipped' ? 'SK' : index + 1}
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>

      {onExit && (
        <div className="flex justify-end">
          <Button variant="ghost" onClick={onExit} className="text-muted-foreground">
            <Zap className="mr-2 h-4 w-4" /> End Session
          </Button>
        </div>
      )}
    </div>
  );
}
