'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { AnimatePresence, motion } from 'framer-motion';
import {
  Activity,
  CheckCircle2,
  ChevronRight,
  Clock,
  Dumbbell,
  Loader2,
  Sparkles,
} from 'lucide-react';

import { apiClient } from '../../../lib/api-client';
import { useWorkout, useUIActions } from '../../../store';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Separator } from '../../../components/ui/separator';
import { MobileBottomNav } from '../../../components/workouts/mobile-bottom-nav';
import { ActiveWorkoutPlayer, WorkoutStep, WorkoutSummary } from '../../../components/workouts/active-workout-player';

const formatSeconds = (value?: number | string | null) => {
  if (value === undefined || value === null) return null;
  const numeric = typeof value === 'number' ? value : Number(value);
  if (!Number.isFinite(numeric) || numeric <= 0) return null;
  const total = Math.round(numeric);
  const minutes = Math.floor(total / 60);
  const seconds = total % 60;
  if (minutes > 0 && seconds > 0) return `${minutes}m ${seconds}s`;
  if (minutes > 0) return `${minutes}m`;
  return `${seconds}s`;
};

const formatDateLabel = (value?: string | Date | null) => {
  if (!value) return null;
  const dateValue = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(dateValue.getTime())) return null;
  return dateValue.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const getFirstSchedule = (program: any) => {
  if (!program?.daily_schedules) return null;
  if (Array.isArray(program.daily_schedules)) {
    return program.daily_schedules[0] ?? null;
  }
  if (typeof program.daily_schedules === 'object') {
    const values = Object.values(program.daily_schedules);
    return values.length > 0 ? values[0] : null;
  }
  return null;
};

const getPhaseDurations = (program: any) => {
  const metadataDurations = program?.ai_generation_metadata?.phase_duration_seconds;
  if (metadataDurations) {
    return metadataDurations;
  }
  const schedule = getFirstSchedule(program);
  if (schedule?.phase_duration_seconds) {
    return schedule.phase_duration_seconds;
  }
  return null;
};

const formatPhaseSummary = (program: any) => {
  const durations = getPhaseDurations(program);
  if (!durations) {
    return null;
  }
  const summary: string[] = [];
  if (durations.warmup) summary.push(`Warm-up ${formatSeconds(durations.warmup)}`);
  if (durations.main) summary.push(`Main ${formatSeconds(durations.main)}`);
  if (durations.cooldown) summary.push(`Cooldown ${formatSeconds(durations.cooldown)}`);
  return summary.join(' | ');
};

const safeArray = (value: any): any[] => {
  if (!value) return [];
  if (Array.isArray(value)) return value;
  return [value];
};

const sanitizeNumber = (value: any): number | undefined => {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === 'string') {
    const numeric = Number(value);
    if (Number.isFinite(numeric)) {
      return numeric;
    }
  }
  return undefined;
};

const mapExerciseToStep = (item: any, section: WorkoutStep['section'], index: number): WorkoutStep => {
  const sets = sanitizeNumber(item.sets ?? item.total_sets ?? item.rounds);
  const reps = sanitizeNumber(item.reps ?? item.target_reps);
  const durationRaw = sanitizeNumber(item.duration ?? item.duration_seconds ?? item.work_duration ?? item.target_duration);
  const durationSeconds = durationRaw ? Math.round(durationRaw) : undefined;
  const restRaw = sanitizeNumber(item.rest ?? item.rest_seconds ?? item.rest_time);
  const restSeconds = restRaw ? Math.round(restRaw) : section === 'main' ? 60 : 30;

  return {
    id: `${section}-${index}-${item.id ?? item.name ?? 'exercise'}`,
    name: item.name ?? 'Exercise',
    section,
    sets: sets && sets > 0 ? sets : undefined,
    reps: reps && reps > 0 ? reps : undefined,
    durationSeconds: durationSeconds && durationSeconds > 0 ? durationSeconds : undefined,
    restSeconds: restSeconds && restSeconds > 0 ? restSeconds : undefined,
    instructions: item.instructions ?? item.description ?? item.cue,
    equipment: safeArray(item.equipment ?? item.equipment_needed).filter(Boolean),
    targetMuscles: safeArray(item.target_muscles ?? item.primary_muscles ?? item.muscles).filter(Boolean),
    mediaUrl: item.media_url ?? item.video ?? item.image,
  };
};

const buildStepsFromPlan = (plan: any): WorkoutStep[] => {
  if (!plan) return [];
  const warmup = safeArray(plan.warmup);
  const main = safeArray(plan.exercises ?? plan.main);
  const cooldown = safeArray(plan.cooldown);

  const steps: WorkoutStep[] = [];
  warmup.forEach((item, index) => steps.push(mapExerciseToStep(item, 'warmup', index)));
  main.forEach((item, index) => steps.push(mapExerciseToStep(item, 'main', index)));
  cooldown.forEach((item, index) => steps.push(mapExerciseToStep(item, 'cooldown', index)));

  return steps;
};

const buildStepsFromProgramSchedule = (program: any): WorkoutStep[] => {
  const schedule = getFirstSchedule(program);
  if (!schedule) return [];
  return buildStepsFromPlan({
    warmup: schedule.warmup_exercises,
    exercises: schedule.main_exercises,
    cooldown: schedule.cooldown_exercises,
  });
};

const sumDurationSeconds = (steps: WorkoutStep[]) => {
  return steps.reduce((total, step) => {
    if (step.durationSeconds) {
      return total + step.durationSeconds + (step.restSeconds ?? 0);
    }
    if (step.sets && step.reps) {
      const estimatedPerRep = 4; // seconds per rep estimate
      return total + step.sets * step.reps * estimatedPerRep + (step.restSeconds ?? 0);
    }
    return total + (step.restSeconds ?? 0) + 45;
  }, 0);
};

const estimateCaloriesBurned = (steps: WorkoutStep[]) => {
  const totalSeconds = sumDurationSeconds(steps);
  if (!totalSeconds) return undefined;
  const mets = 7.5; // general strength training MET value
  const weightKg = 75; // assume average weight
  const caloriesPerMinute = (mets * 3.5 * weightKg) / 200;
  return Math.round((totalSeconds / 60) * caloriesPerMinute);
};

const SectionBadgeMap: Record<WorkoutStep['section'], string> = {
  warmup: 'bg-amber-500/15 text-amber-800',
  main: 'bg-emerald-500/15 text-emerald-800',
  cooldown: 'bg-sky-500/15 text-sky-800',
};

const ActiveProgramsPage = () => {
  const router = useRouter();
  const { setCurrentPage, addNotification } = useUIActions();
  const workoutState = useWorkout();

  const [programs, setPrograms] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedProgramId, setExpandedProgramId] = useState<string | null>(null);

  const [view, setView] = useState<'overview' | 'player' | 'complete'>('overview');
  const [activeSteps, setActiveSteps] = useState<WorkoutStep[]>([]);
  const [activeProgramName, setActiveProgramName] = useState<string>('Workout Session');
  const [summary, setSummary] = useState<WorkoutSummary | null>(null);

  const recentGeneratedWorkout = workoutState.generatedWorkout?.workout;

  useEffect(() => {
    setCurrentPage('workouts');

    const loadPrograms = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await apiClient.getWorkoutPrograms({ limit: 50 });
        if (response.data) {
          setPrograms(response.data);
        } else if (response.error) {
          setError(response.error);
        }
      } catch (err) {
        console.error('Failed to load saved workouts', err);
        setError('Unable to load saved programs right now.');
        addNotification({
          type: 'error',
          title: 'Unable to load workouts',
          message: 'We could not retrieve your saved workouts. Please try again shortly.',
        });
      } finally {
        setLoading(false);
      }
    };

    loadPrograms();
  }, [addNotification, setCurrentPage]);

  const storedPrograms = useMemo(() => programs ?? [], [programs]);

  const activePlan = useMemo(() => {
    if (!recentGeneratedWorkout) return null;
    const steps = buildStepsFromPlan(recentGeneratedWorkout);
    if (steps.length === 0) return null;

    const durationMinutes = recentGeneratedWorkout.duration_minutes
      ? Number(recentGeneratedWorkout.duration_minutes)
      : Math.round(sumDurationSeconds(steps) / 60);

    return {
      name: recentGeneratedWorkout.name ?? 'Strength Training',
      type: (recentGeneratedWorkout.workout_type ?? 'strength').replace(/_/g, ' '),
      difficulty: recentGeneratedWorkout.difficulty_level ?? 'intermediate',
      steps,
      warmupCount: steps.filter((step) => step.section === 'warmup').length,
      mainCount: steps.filter((step) => step.section === 'main').length,
      cooldownCount: steps.filter((step) => step.section === 'cooldown').length,
      estimatedDuration: durationMinutes,
      equipment: safeArray(recentGeneratedWorkout.equipment_needed).filter(Boolean),
      estimatedCalories: recentGeneratedWorkout.estimated_calories ?? estimateCaloriesBurned(steps),
    };
  }, [recentGeneratedWorkout]);

  const handleGenerate = () => {
    router.push('/generate');
  };

  const handleStartActivePlan = () => {
    if (!activePlan) {
      addNotification({
        type: 'warning',
        title: 'No workout ready',
        message: 'Generate a workout to start a guided session.',
      });
      return;
    }

    setActiveSteps(activePlan.steps);
    setActiveProgramName(activePlan.name);
    setSummary(null);
    setView('player');
  };

  const handleStartStoredProgram = (program: any) => {
    const steps = buildStepsFromProgramSchedule(program);
    if (steps.length === 0) {
      addNotification({
        type: 'warning',
        title: 'No session available',
        message: 'This program does not include a detailed schedule yet.',
      });
      return;
    }
    setActiveSteps(steps);
    setActiveProgramName(program.name ?? 'Active Program');
    setSummary(null);
    setView('player');
  };

  const handlePlayerComplete = (result: WorkoutSummary) => {
    setSummary(result);
    setView('complete');
  };

  const handleExitPlayer = () => {
    setActiveSteps([]);
    setSummary(null);
    setView('overview');
  };

  const renderScheduleDetails = (schedule: any) => {
    if (!schedule) return null;

    const warmup = safeArray(schedule.warmup_exercises);
    const main = safeArray(schedule.main_exercises);
    const cooldown = safeArray(schedule.cooldown_exercises);

    const buildSection = (label: string, items: any[], section: WorkoutStep['section']) => (
      <div className="rounded-2xl border border-border/60 bg-card/70 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <span className={`rounded-full px-3 py-1 text-xs font-semibold ${SectionBadgeMap[section]}`}>
              {label}
            </span>
            <span className="text-muted-foreground">{items.length} drills</span>
          </div>
        </div>
        <div className="mt-3 space-y-3 text-sm">
          {items.map((item, index) => (
            <div
              key={`${label}-${index}`}
              className="rounded-xl border border-border/50 bg-background/80 p-3 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">{item.name ?? 'Exercise'}</span>
                <span className="text-xs uppercase tracking-wide text-muted-foreground">
                  {item.intensity_level ?? item.category ?? ''}
                </span>
              </div>
              <div className="mt-2 flex flex-wrap gap-3 text-xs text-muted-foreground">
                {item.sets && item.reps && (
                  <span>{item.sets} sets x {item.reps} reps</span>
                )}
                {item.duration && (
                  <span>Duration {formatSeconds(item.duration)}</span>
                )}
                {item.rest_time && (
                  <span>Rest {formatSeconds(item.rest_time)}</span>
                )}
                {Array.isArray(item.equipment) && item.equipment.length > 0 && (
                  <span>Equipment: {item.equipment.join(', ')}</span>
                )}
              </div>
              {item.instructions && (
                <p className="mt-2 text-xs text-muted-foreground/80">
                  {item.instructions}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    );

    return (
      <div className="mt-4 space-y-4">
        {warmup.length > 0 && buildSection('Warm-up', warmup, 'warmup')}
        {main.length > 0 && buildSection('Main Session', main, 'main')}
        {cooldown.length > 0 && buildSection('Cooldown', cooldown, 'cooldown')}
      </div>
    );
  };

  const renderOverview = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <section>
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-800 text-white shadow-xl"
        >
          <div className="pointer-events-none absolute inset-0">
            <div className="absolute -left-16 top-12 h-72 w-72 rounded-full bg-primary/40 blur-3xl" />
            <div className="absolute -right-10 bottom-0 h-64 w-64 rounded-full bg-purple-500/30 blur-3xl" />
          </div>
          <div className="relative px-6 py-8 md:px-10 md:py-12">
            <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
              <div className="space-y-4">
                <span className="inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-1 text-xs font-semibold uppercase tracking-widest">
                  <Sparkles className="h-3.5 w-3.5" /> Active Program
                </span>
                <div>
                  <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">
                    {activePlan ? activePlan.name : 'Let’s build your next breakthrough workout'}
                  </h1>
                  <p className="mt-3 max-w-2xl text-sm text-white/70 md:text-base">
                    {activePlan
                      ? 'Jump back into your AI-crafted session and follow the guided flow with timers, rest, and coaching cues.'
                      : 'Generate a personalized strength session and take it one exercise at a time with guided pacing and smart rest timers.'}
                  </p>
                </div>
                {activePlan && (
                  <div className="flex flex-wrap items-center gap-4 text-sm text-white/80">
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {activePlan.estimatedDuration || 45} min
                    </span>
                    <span className="flex items-center gap-1">
                      <Activity className="h-4 w-4" />
                      {activePlan.mainCount} main sets
                    </span>
                    <Badge variant="secondary" className="bg-white/15 text-white">
                      {activePlan.difficulty}
                    </Badge>
                  </div>
                )}
              </div>
              <div className="flex flex-col items-start gap-3 md:items-end">
                <Button size="lg" onClick={activePlan ? handleStartActivePlan : handleGenerate} className="shadow-lg">
                  <Sparkles className="mr-2 h-4 w-4" />
                  {activePlan ? 'Start Guided Workout' : 'Generate New Workout'}
                </Button>
                {activePlan && (
                  <div className="rounded-2xl border border-white/15 bg-white/10 px-4 py-3 text-xs text-white/80">
                    <div className="flex items-center gap-3">
                      <div>
                        <div>{activePlan.warmupCount} warm-up</div>
                        <div>{activePlan.cooldownCount} cooldown</div>
                      </div>
                      <Separator orientation="vertical" className="h-10 bg-white/20" />
                      <div>
                        <div>{activePlan.mainCount} main drills</div>
                        {activePlan.estimatedCalories && (
                          <div>{activePlan.estimatedCalories} kcal est.</div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      <section>
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.05 }}>
          <Card className="border-border/60">
            <CardHeader>
              <CardTitle>Program Library</CardTitle>
              <CardDescription>Your collected AI workouts, ready whenever you are.</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center py-12 text-sm text-muted-foreground">
                  <Loader2 className="mr-3 h-5 w-5 animate-spin" />
                  Loading saved programs...
                </div>
              ) : error ? (
                <div className="rounded-xl border border-destructive/40 bg-destructive/10 p-6 text-center text-sm text-destructive">
                  {error}
                </div>
              ) : storedPrograms.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-border/60 bg-muted/30 p-8 text-center text-sm text-muted-foreground">
                  No saved programs yet. Generate a workout to add your first training plan.
                  <div className="mt-4">
                    <Button onClick={handleGenerate} variant="outline">
                      <Sparkles className="mr-2 h-4 w-4" /> Generate Workout
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {storedPrograms.map((program, index) => {
                    const programId = program.id?.toString() ?? `program-${index}`;
                    const schedule = getFirstSchedule(program);
                    const phaseSummary = formatPhaseSummary(program);
                    const steps = buildStepsFromProgramSchedule(program);
                    const hasSteps = steps.length > 0;
                    const createdAt = formatDateLabel(
                      program.ai_generation_metadata?.generation_timestamp || program.created_at
                    );

                    return (
                      <motion.div
                        key={programId}
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.04 }}
                        className="rounded-3xl border border-border/60 bg-card/80 p-5 shadow-sm"
                      >
                        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                          <div className="space-y-3">
                            <div className="flex items-center gap-3">
                              <Badge variant="outline" className="capitalize">
                                {program.difficulty_level}
                              </Badge>
                              {program.is_active && (
                                <Badge variant="secondary" className="bg-emerald-500/15 text-emerald-700">
                                  Active
                                </Badge>
                              )}
                            </div>
                            <div>
                              <h3 className="text-lg font-semibold">{program.name}</h3>
                              <p className="mt-1 text-sm text-muted-foreground">
                                {program.description || 'Structured AI program with warm-up, main sets, and cooldown.'}
                              </p>
                            </div>
                            <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
                              <span>{program.duration_days} day plan</span>
                              {program.sessions_per_week && <span>{program.sessions_per_week} sessions/week</span>}
                              {phaseSummary && <span>{phaseSummary}</span>}
                              {createdAt && <span>Generated {createdAt}</span>}
                            </div>
                          </div>
                          <div className="flex flex-col items-start gap-3 md:items-end">
                            <div className="flex gap-2 text-xs text-muted-foreground">
                              <div className="flex items-center gap-1 rounded-full bg-primary/10 px-3 py-1 font-medium text-primary">
                                <Dumbbell className="h-3.5 w-3.5" /> {steps.filter((step) => step.section === 'main').length} exercises
                              </div>
                              <div className="flex items-center gap-1 rounded-full bg-amber-500/10 px-3 py-1 font-medium text-amber-700">
                                <Clock className="h-3.5 w-3.5" />
                                {Math.max(1, Math.round(sumDurationSeconds(steps) / 60))} min est.
                              </div>
                            </div>
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                onClick={() => setExpandedProgramId(expandedProgramId === programId ? null : programId)}
                                variant="outline"
                              >
                                Details
                                <ChevronRight className={`ml-1 h-4 w-4 transition-transform ${expandedProgramId === programId ? 'rotate-90' : ''}`} />
                              </Button>
                              <Button size="sm" disabled={!hasSteps} onClick={() => handleStartStoredProgram(program)}>
                                <Sparkles className="mr-2 h-4 w-4" /> Start Session
                              </Button>
                            </div>
                          </div>
                        </div>

                        {expandedProgramId === programId && renderScheduleDetails(schedule)}
                      </motion.div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </section>
    </motion.div>
  );

  const renderSummary = () => (
    <motion.div
      key="summary"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 16 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <Card className="overflow-hidden border-border/60">
        <div className="bg-gradient-to-r from-emerald-500 via-teal-500 to-sky-500 px-6 py-10 text-white">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <span className="inline-flex items-center gap-2 rounded-full bg-white/15 px-4 py-1 text-xs font-semibold uppercase tracking-widest">
                <CheckCircle2 className="h-4 w-4" /> Session Complete
              </span>
              <h2 className="mt-4 text-3xl font-semibold">Nice work!</h2>
              <p className="mt-2 max-w-xl text-sm text-white/80">
                You powered through {summary?.completedSteps ?? 0} of {summary?.totalSteps ?? activeSteps.length} steps. Keep the streak alive!
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="rounded-2xl border border-white/15 bg-white/10 p-4 text-center">
                <div className="text-xs uppercase tracking-wide text-white/70">Total Time</div>
                <div className="mt-2 text-2xl font-semibold">
                  {summary
                    ? `${Math.floor(summary.totalElapsedSeconds / 60)}m ${summary.totalElapsedSeconds % 60}s`
                    : '—'}
                </div>
              </div>
              <div className="rounded-2xl border border-white/15 bg-white/10 p-4 text-center">
                <div className="text-xs uppercase tracking-wide text-white/70">Calories</div>
                <div className="mt-2 text-2xl font-semibold">
                  {summary?.estimatedCalories ?? estimateCaloriesBurned(activeSteps) ?? '—'} kcal
                </div>
              </div>
            </div>
          </div>
        </div>
        <CardContent className="space-y-4 py-6">
          <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
            <span>
              <strong className="text-foreground">Completed</strong> {summary?.completedSteps ?? 0} steps
            </span>
            <span>
              <strong className="text-foreground">Skipped</strong> {summary?.skippedSteps ?? 0}
            </span>
          </div>
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-end">
            <Button variant="outline" onClick={handleExitPlayer}>
              Back to Programs
            </Button>
            <Button onClick={() => setView('player')}>
              Replay Session
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <div className="relative min-h-screen bg-gradient-to-b from-background via-background/95 to-background">
      <div className="mx-auto flex w-full max-w-5xl flex-col px-4 pb-24 pt-6 sm:px-6 md:pt-10">
        <AnimatePresence mode="wait">
          {view === 'overview' && <motion.div key="overview">{renderOverview()}</motion.div>}
          {view === 'player' && activeSteps.length > 0 && (
            <motion.div
              key="player"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 16 }}
              transition={{ duration: 0.4 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-semibold">{activeProgramName}</h2>
                  <p className="text-sm text-muted-foreground">Guided session • {activeSteps.length} total exercises</p>
                </div>
                <Button variant="ghost" onClick={handleExitPlayer}>
                  Exit
                </Button>
              </div>
              <ActiveWorkoutPlayer steps={activeSteps} onComplete={handlePlayerComplete} onExit={handleExitPlayer} />
            </motion.div>
          )}
          {view === 'complete' && renderSummary()}
        </AnimatePresence>
      </div>

      <MobileBottomNav current="programs" />
    </div>
  );
};

export default ActiveProgramsPage;

