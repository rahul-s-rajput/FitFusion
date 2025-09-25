'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  Activity,
  Dumbbell,
  Target,
  TrendingUp,
  Calendar,
  Play,
  Settings,
  Zap,
  Clock,
  Award,
  ChevronRight,
  Sparkles,
  CheckCircle,
} from 'lucide-react';

import { useWorkout, useProgress, useUser, useWorkoutActions, useUIActions } from '../store';
import { apiClient } from '../lib/api-client';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { PageHero, type HeroStat } from '../components/workouts/page-hero';
import { SectionHeader } from '../components/workouts/section-header';
import { QuickStatCard } from '../components/workouts/quick-stat-card';
import { MobileBottomNav } from '../components/workouts/mobile-bottom-nav';

const capitalize = (value?: string | null) => {
  if (!value) return '';
  return value.charAt(0).toUpperCase() + value.slice(1);
};

const formatStatusLabel = (value?: string | null) => {
  if (!value) return 'Not started';
  return value
    .split('_')
    .map((part) => capitalize(part))
    .join(' ');
};

export default function Home() {
  const router = useRouter();
  const user = useUser();
  const workout = useWorkout();
  const progress = useProgress();
  const { updateTodaySessions, updateRecentPrograms } = useWorkoutActions();
  const { setCurrentPage, addNotification } = useUIActions();

  const [isLoading, setIsLoading] = useState(true);
  const [todayStats, setTodayStats] = useState({
    scheduledSessions: 0,
    completedSessions: 0,
    totalDuration: 0,
  });

  const isMountedRef = useRef(true);
  const hasNotifiedRef = useRef(false);

  const loadDashboardData = useCallback(async () => {
    if (!isMountedRef.current) {
      return;
    }

    setIsLoading(true);

    try {
      const todayResponse = await apiClient.getTodaySessions();
      if (isMountedRef.current && todayResponse.data) {
        updateTodaySessions(todayResponse.data);

        const completed = todayResponse.data.filter((session) => session.completion_status === 'completed');
        setTodayStats({
          scheduledSessions: todayResponse.data.length,
          completedSessions: completed.length,
          totalDuration: completed.reduce((sum, session) => sum + (session.estimated_duration || 0), 0),
        });
      }

      const programsResponse = await apiClient.getWorkoutPrograms({ limit: 5 });
      if (isMountedRef.current && programsResponse.data) {
        updateRecentPrograms(programsResponse.data);
      }

      if (isMountedRef.current && !progress.stats.totalWorkouts) {
        const statsResponse = await apiClient.getSessionStats(30);
        if (statsResponse.data) {
          // Reserved for future store integration.
        }
      }
    } catch (error) {
      if (!isMountedRef.current || hasNotifiedRef.current) {
        return;
      }

      hasNotifiedRef.current = true;
      console.error('Failed to load dashboard data:', error);
      addNotification({
        type: 'error',
        title: 'Loading Error',
        message: 'Failed to load dashboard data. Some features may be limited.',
      });
    } finally {
      if (isMountedRef.current) {
        setIsLoading(false);
      }
    }
  }, [addNotification, progress.stats.totalWorkouts, updateRecentPrograms, updateTodaySessions]);

  useEffect(() => {
    isMountedRef.current = true;
    hasNotifiedRef.current = false;

    setCurrentPage('home');
    loadDashboardData();

    return () => {
      isMountedRef.current = false;
    };
  }, [setCurrentPage, loadDashboardData]);

  const handleStartWorkout = (sessionId?: string) => {
    if (sessionId) {
      router.push(`/workout/${sessionId}`);
    } else {
      router.push('/generate');
    }
  };

  const handleViewProgress = () => {
    router.push('/profile/progress');
  };

  const handleManageEquipment = () => {
    router.push('/equipment');
  };

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
    return dateValue.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getFirstSchedule = (program: any) => {
    if (!program?.daily_schedules) {
      return null;
    }
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

  const nextSession = useMemo(() => {
    const upcoming = workout.todaySessions.find((session) => session.completion_status !== 'completed');
    return upcoming ?? workout.todaySessions[0];
  }, [workout.todaySessions]);

  const completionPercent = todayStats.scheduledSessions > 0
    ? Math.round((todayStats.completedSessions / todayStats.scheduledSessions) * 100)
    : 0;

  const totalWorkoutMinutes = progress.stats.totalWorkoutTime ?? 0;
  const workoutTimeLabel = totalWorkoutMinutes >= 60
    ? `${Math.round(totalWorkoutMinutes / 60)} hr`
    : `${totalWorkoutMinutes} min`;

  const heroStats = useMemo<HeroStat[]>(() => [
    {
      label: 'Today',
      value: `${todayStats.completedSessions}/${todayStats.scheduledSessions}`,
      helper: todayStats.scheduledSessions > 0 ? `${completionPercent}% complete` : 'No sessions scheduled',
      icon: Calendar,
    },
    {
      label: 'Streak',
      value: `${progress.stats.currentStreak ?? 0} days`,
      helper: `Best ${progress.stats.longestStreak ?? 0} days`,
      icon: Activity,
    },
    {
      label: 'Total Workouts',
      value: String(progress.stats.totalWorkouts ?? 0),
      helper: 'All time completed',
      icon: Dumbbell,
    },
    {
      label: 'Workout Time',
      value: workoutTimeLabel,
      helper: 'Lifetime volume',
      icon: Clock,
    },
  ], [completionPercent, progress.stats.currentStreak, progress.stats.longestStreak, progress.stats.totalWorkouts, workoutTimeLabel, todayStats.completedSessions, todayStats.scheduledSessions]);

  const quickStats = useMemo(() => [
    {
      title: 'Next Session',
      value: nextSession ? `${capitalize(nextSession.workout_type ?? 'Workout')} training` : 'Not scheduled',
      helper: nextSession ? `${nextSession.estimated_duration ?? 0} min planned` : 'Generate your next session',
      icon: Play,
    },
    {
      title: 'Today Minutes',
      value: `${todayStats.totalDuration} min`,
      helper: 'Completed today',
      icon: Clock,
    },
    {
      title: 'Active Program',
      value: workout.activeProgram ? `${Math.round(workout.activeProgram.completion_percentage ?? 0)}%` : 'None',
      helper: workout.activeProgram ? workout.activeProgram.name : 'Browse programs to get started',
      icon: Target,
    },
    {
      title: 'Saved AI Workouts',
      value: String(workout.recentPrograms.length),
      helper: 'Stored sessions',
      icon: Sparkles,
    },
  ], [nextSession, todayStats.totalDuration, workout.activeProgram, workout.recentPrograms.length]);

  const heroActions = (
    <>
      <Button
        size="lg"
        onClick={() => handleStartWorkout(nextSession?.id?.toString())}
      >
        <Play className="mr-2 h-4 w-4" />
        {nextSession ? 'Start Next Session' : 'Generate Workout'}
      </Button>
      <Button size="lg" variant="secondary" onClick={handleViewProgress}>
        <TrendingUp className="mr-2 h-4 w-4" />
        View Progress
      </Button>
    </>
  );

  const userDisplayName = user.profile?.email?.split('@')[0] ?? 'Athlete';

  if (isLoading) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-indigo-950 via-slate-950 to-black text-white">
        <div className="h-12 w-12 animate-spin rounded-full border-2 border-white/30 border-t-white" />
        <p className="mt-4 text-sm text-white/70">Loading your fitness dashboard...</p>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-gradient-to-b from-background via-background/95 to-background">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 pb-24 pt-6 sm:px-6 lg:pt-10">
        <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
          <PageHero
            eyebrow="Welcome back"
            title={`Let's train, ${capitalize(userDisplayName)}`}
            description="Stay focused on today's plan while FitFusion handles tracking, programs, and AI coaching."
            actions={heroActions}
            stats={heroStats}
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {quickStats.map((stat, index) => (
              <motion.div
                key={stat.title}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.05 * index }}
              >
                <QuickStatCard
                  title={stat.title}
                  value={stat.value}
                  helper={stat.helper}
                  icon={stat.icon}
                />
              </motion.div>
            ))}
          </div>
        </motion.div>

        <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.15 }}
            >
              <Card className="border-border/60">
                <CardHeader>
                  <SectionHeader
                    title="Today's Sessions"
                    description="Follow the plan one workout at a time."
                    action={
                      <Button size="sm" variant="outline" onClick={() => handleStartWorkout()}>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Generate
                      </Button>
                    }
                  />
                </CardHeader>
                <CardContent>
                  {workout.todaySessions.length > 0 ? (
                    <div className="space-y-3">
                      {workout.todaySessions.map((session, index) => {
                        const statusLabel = formatStatusLabel(session.completion_status);
                        const statusVariant = session.completion_status === 'completed'
                          ? 'default'
                          : session.completion_status === 'in_progress'
                            ? 'secondary'
                            : 'outline';

                        return (
                          <motion.div
                            key={session.id ?? `session-${index}`}
                            initial={{ opacity: 0, y: 16 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3, delay: index * 0.05 }}
                          >
                            <div className="rounded-2xl border border-border/60 bg-card/80 p-4 shadow-sm">
                              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                                <div className="flex items-start gap-3">
                                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                                    <Dumbbell className="h-6 w-6" />
                                  </div>
                                  <div>
                                    <h4 className="text-base font-semibold capitalize">
                                      {session.workout_type || 'Training'}
                                    </h4>
                                    <p className="text-sm text-muted-foreground">
                                      {session.estimated_duration || 0} min session
                                      {session.scheduled_date
                                        ? ` - ${new Date(session.scheduled_date).toLocaleTimeString('en-US', {
                                            hour: 'numeric',
                                            minute: '2-digit',
                                          })}`
                                        : ''}
                                    </p>
                                  </div>
                                </div>
                                <div className="flex flex-col items-end gap-2 sm:flex-row sm:items-center sm:gap-3">
                                  <Badge variant={statusVariant}>{statusLabel}</Badge>
                                  <Button
                                    size="sm"
                                    onClick={() => handleStartWorkout(session.id?.toString())}
                                    disabled={session.completion_status === 'completed'}
                                  >
                                    {session.completion_status === 'completed' ? (
                                      <>
                                        <CheckCircle className="mr-2 h-4 w-4" />
                                        Completed
                                      </>
                                    ) : session.completion_status === 'in_progress' ? (
                                      <>
                                        <Play className="mr-2 h-4 w-4" />
                                        Continue
                                      </>
                                    ) : (
                                      <>
                                        <Play className="mr-2 h-4 w-4" />
                                        Start
                                      </>
                                    )}
                                  </Button>
                                </div>
                              </div>
                            </div>
                          </motion.div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border/60 bg-muted/30 px-6 py-12 text-center">
                      <Dumbbell className="mb-4 h-10 w-10 text-muted-foreground" />
                      <h4 className="text-lg font-semibold">No workouts scheduled</h4>
                      <p className="mt-2 text-sm text-muted-foreground">
                        Generate an AI-powered workout to jump back in.
                      </p>
                      <Button className="mt-4" onClick={() => handleStartWorkout()}>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Generate Workout
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>

            {workout.recentPrograms.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.2 }}
              >
                <Card className="border-border/60">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle>Saved AI Workouts</CardTitle>
                        <CardDescription>Your recently generated sessions</CardDescription>
                      </div>
                      <Button variant="ghost" size="sm" onClick={() => router.push('/workouts/saved')}>
                        View All
                        <ChevronRight className="ml-1 h-3 w-3" />
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {workout.recentPrograms.slice(0, 3).map((program, index) => {
                      const schedule = getFirstSchedule(program);
                      const createdAt = formatDateLabel(
                        program.ai_generation_metadata?.generation_timestamp || program.created_at
                      );
                      const phaseSummary = formatPhaseSummary(program);
                      const warmupCount = Array.isArray(schedule?.warmup_exercises) ? schedule.warmup_exercises.length : 0;
                      const mainCount = Array.isArray(schedule?.main_exercises) ? schedule.main_exercises.length : 0;
                      const cooldownCount = Array.isArray(schedule?.cooldown_exercises) ? schedule.cooldown_exercises.length : 0;

                      return (
                        <motion.div
                          key={program.id ?? `program-${index}`}
                          initial={{ opacity: 0, y: 12 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.3, delay: index * 0.05 }}
                          className="rounded-2xl border border-border/60 bg-card/70 p-4"
                        >
                          <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                            <div className="space-y-2">
                              <div className="flex items-center gap-2">
                                <Badge variant="secondary" className="capitalize">
                                  {program.difficulty_level}
                                </Badge>
                                {program.is_active && (
                                  <Badge variant="outline" className="border-emerald-500 text-emerald-600">
                                    Active
                                  </Badge>
                                )}
                              </div>
                              <div>
                                <h4 className="text-base font-semibold">{program.name}</h4>
                                {program.description && (
                                  <p className="mt-1 text-sm text-muted-foreground">{program.description}</p>
                                )}
                              </div>
                              <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                                <span>{program.duration_days} day plan</span>
                                {createdAt && <span>Generated {createdAt}</span>}
                                {phaseSummary && <span>{phaseSummary}</span>}
                              </div>
                            </div>
                            <div className="text-right text-xs text-muted-foreground">
                              <div>Warm-up: {warmupCount}</div>
                              <div>Main: {mainCount}</div>
                              <div>Cooldown: {cooldownCount}</div>
                            </div>
                          </div>
                        </motion.div>
                      );
                    })}
                  </CardContent>
                </Card>
              </motion.div>
            )}

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.25 }}
            >
              <Card className="border-border/60">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Recent Activity</CardTitle>
                      <CardDescription>Your latest fitness highlights</CardDescription>
                    </div>
                    <Button variant="ghost" size="sm" onClick={handleViewProgress}>
                      View All
                      <ChevronRight className="ml-1 h-3 w-3" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {progress.recentRecords.length > 0 ? (
                    <div className="space-y-3">
                      {progress.recentRecords.slice(0, 3).map((record, index) => (
                        <motion.div
                          key={record.id ?? `record-${index}`}
                          className="flex items-center gap-3 rounded-2xl border border-border/50 p-3 hover:bg-muted/40"
                          initial={{ opacity: 0, x: -16 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.3, delay: index * 0.05 }}
                        >
                          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
                            <Award className="h-5 w-5" />
                          </div>
                          <div className="flex-1">
                            <p className="text-sm font-medium">{record.metric_name}</p>
                            <p className="text-xs text-muted-foreground">
                              {record.record_date.toLocaleDateString()}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-semibold">
                              {record.metric_value} {record.metric_unit}
                            </p>
                            {record.notes && (
                              <p className="text-xs text-muted-foreground">{record.notes}</p>
                            )}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border/60 bg-muted/30 px-6 py-10 text-center">
                      <Activity className="mb-3 h-10 w-10 text-muted-foreground" />
                      <h4 className="text-lg font-semibold">No activity yet</h4>
                      <p className="mt-2 text-sm text-muted-foreground">
                        Complete your first workout to start building momentum.
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </div>

          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.2 }}
            >
              <Card className="overflow-hidden border-none bg-gradient-to-br from-emerald-600 via-emerald-700 to-emerald-900 text-white shadow-lg">
                <div className="px-6 py-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs uppercase tracking-wide text-white/70">Active Program</p>
                      <h3 className="mt-2 text-xl font-semibold">
                        {workout.activeProgram ? workout.activeProgram.name : 'No program active'}
                      </h3>
                    </div>
                    <Badge variant="secondary" className="bg-white/15 text-white">
                      Coach Mode
                    </Badge>
                  </div>

                  {workout.activeProgram ? (
                    <div className="mt-5 space-y-4">
                      <div className="flex items-center justify-between text-sm text-white/80">
                        <span>Completion</span>
                        <span>{Math.round(workout.activeProgram.completion_percentage ?? 0)}%</span>
                      </div>
                      <Progress value={Math.round(workout.activeProgram.completion_percentage ?? 0)} className="h-2 bg-white/20" />
                      <div className="grid grid-cols-2 gap-3 text-xs text-white/80">
                        <div>
                          <p className="text-white/60">Duration</p>
                          <p className="text-sm font-semibold">
                            {workout.activeProgram.duration_days} days
                          </p>
                        </div>
                        <div>
                          <p className="text-white/60">Focus</p>
                          <p className="text-sm font-semibold capitalize">
                            {workout.activeProgram.program_type ?? 'strength'}
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-3">
                        <Button size="sm" variant="secondary" className="bg-white text-emerald-700" onClick={() => router.push('/workouts/saved')}>
                          View Plan
                        </Button>
                        <Button size="sm" variant="ghost" className="text-white hover:bg-white/10" onClick={() => handleStartWorkout()}>
                          Start Workout
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="mt-6 rounded-2xl border border-white/20 bg-white/10 px-4 py-6 text-center text-sm text-white/80">
                      Activate a program to track your long term goals.
                      <div className="mt-4">
                        <Button size="sm" variant="secondary" className="bg-white text-emerald-700" onClick={() => router.push('/workouts/saved')}>
                          Browse Programs
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.25 }}
            >
              <Card className="border-border/60">
                <CardHeader>
                  <CardTitle>Quick Actions</CardTitle>
                  <CardDescription>Jump straight to tools you use most.</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3">
                    <Button
                      variant="outline"
                      className="h-auto flex flex-col items-center gap-2 rounded-2xl border-border/60 p-4"
                      onClick={handleViewProgress}
                    >
                      <TrendingUp className="h-5 w-5" />
                      <span className="text-sm">Progress</span>
                    </Button>
                    <Button
                      variant="outline"
                      className="h-auto flex flex-col items-center gap-2 rounded-2xl border-border/60 p-4"
                      onClick={handleManageEquipment}
                    >
                      <Dumbbell className="h-5 w-5" />
                      <span className="text-sm">Equipment</span>
                    </Button>
                    <Button
                      variant="outline"
                      className="h-auto flex flex-col items-center gap-2 rounded-2xl border-border/60 p-4"
                      onClick={() => router.push('/generate')}
                    >
                      <Zap className="h-5 w-5" />
                      <span className="text-sm">AI Generate</span>
                    </Button>
                    <Button
                      variant="outline"
                      className="h-auto flex flex-col items-center gap-2 rounded-2xl border-border/60 p-4"
                      onClick={() => router.push('/settings')}
                    >
                      <Settings className="h-5 w-5" />
                      <span className="text-sm">Settings</span>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.3 }}
            >
              <Card className="border-border/60">
                <CardHeader>
                  <CardTitle>Stay on track</CardTitle>
                  <CardDescription>Small reminders to keep the momentum.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 text-sm text-muted-foreground">
                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-4">
                    Complete {todayStats.completedSessions} of {todayStats.scheduledSessions} sessions to keep your streak alive.
                  </div>
                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-4">
                    Save new AI workouts after generation so they appear in your program library.
                  </div>
                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-4">
                    Review equipment inventory weekly to let the AI tailor workouts to what you have.
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>

      <MobileBottomNav current="home" />
    </div>
  );
}
