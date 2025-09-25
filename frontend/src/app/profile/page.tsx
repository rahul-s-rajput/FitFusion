'use client';

import { useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  Activity,
  Calendar,
  Flame,
  Target,
  Trophy,
  Dumbbell,
  ChevronRight,
  Sparkles,
  Heart,
  Settings,
  BarChart3,
  MapPin,
  User,
  type LucideIcon,
} from 'lucide-react';

import { useUser, useWorkout, useProgress, useEquipment, useUIActions } from '../../store';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Progress } from '../../components/ui/progress';
import { PageHero, type HeroStat } from '../../components/workouts/page-hero';
import { SectionHeader } from '../../components/workouts/section-header';
import { QuickStatCard } from '../../components/workouts/quick-stat-card';
import { MobileBottomNav } from '../../components/workouts/mobile-bottom-nav';

interface ProfileAchievement {
  id: string;
  title: string;
  description: string;
  icon?: LucideIcon;
  progress?: number;
  unlockedAt?: Date | string;
}

interface StoreAchievement {
  id?: string | number;
  title?: string;
  name?: string;
  category?: string;
  description?: string;
  icon?: LucideIcon;
  progress?: number;
  progress_value?: number;
  target?: number;
  target_value?: number;
  unlockedAt?: string | Date;
  unlocked_at?: string | Date;
}

const capitalizeWords = (value?: string | null) => {
  if (!value) return '';
  return value
    .split(/[_\s]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
};

const formatMinutes = (minutes?: number | null) => {
  if (!minutes) return '0 min';
  const total = Math.max(0, Math.round(minutes));
  const hours = Math.floor(total / 60);
  const remaining = total % 60;
  if (hours && remaining) return `${hours}h ${remaining}m`;
  if (hours) return `${hours}h`;
  return `${remaining}m`;
};

const parseDate = (value?: Date | string | null) => {
  if (!value) return null;
  if (value instanceof Date) {
    return Number.isNaN(value.getTime()) ? null : value;
  }
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
};

const formatScheduleDate = (value?: Date | string | null) => {
  const date = parseDate(value);
  if (!date) return 'Flexible schedule';
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const fallbackAchievements: ProfileAchievement[] = [
  {
    id: 'momentum',
    title: 'Momentum Starter',
    description: 'Logged your first AI-guided workout session.',
    icon: Trophy,
    progress: 100,
  },
  {
    id: 'streak-builder',
    title: 'Streak Builder',
    description: 'Maintain a 3-day workout streak this week.',
    icon: Flame,
    progress: 60,
  },
  {
    id: 'time-investor',
    title: 'Time Investor',
    description: 'Accumulate five hours of deliberate training.',
    icon: Activity,
    progress: 40,
  },
];

export default function ProfilePage() {
  const router = useRouter();
  const user = useUser();
  const workout = useWorkout();
  const progress = useProgress();
  const equipment = useEquipment();
  const { setCurrentPage } = useUIActions();

  useEffect(() => {
    setCurrentPage('profile');
  }, [setCurrentPage]);

  const displayName = useMemo(() => {
    if (user.profile?.name) return user.profile.name;
    if (user.profile?.email) return user.profile.email.split('@')[0];
    return 'Athlete';
  }, [user.profile?.email, user.profile?.name]);

  const focusGoals = useMemo(() => user.profile?.fitness_goals ?? [], [user.profile?.fitness_goals]);
  const availableEquipment = useMemo(
    () => equipment.inventory.filter((item) => item.is_available),
    [equipment.inventory]
  );

  const activeProgram = workout.activeProgram;
  const todaySessions = useMemo(() => workout.todaySessions ?? [], [workout.todaySessions]);

  const upcomingSession = useMemo(() => {
    if (!todaySessions.length) {
      return undefined;
    }

    const sorted = [...todaySessions].sort((a, b) => {
      const dateA = parseDate(a.scheduled_date)?.getTime() ?? 0;
      const dateB = parseDate(b.scheduled_date)?.getTime() ?? 0;
      return dateA - dateB;
    });

    return (
      sorted.find((session) => session.completion_status !== 'completed') ?? sorted[0]
    );
  }, [todaySessions]);

  const readinessScore = useMemo(() => {
    // Blend streak momentum, program completion, and whether a session is queued
    // to produce a mobile-friendly readiness pulse for the dashboard hero.
    const streak = progress.stats.currentStreak ?? 0;
    const completionBoost = activeProgram ? Math.round(activeProgram.completion_percentage ?? 0) / 5 : 0;
    return Math.min(100, streak * 12 + completionBoost + (todaySessions.length ? 10 : 0));
  }, [activeProgram, progress.stats.currentStreak, todaySessions.length]);

  const readinessLabel = useMemo(() => {
    if (readinessScore >= 80) return 'High';
    if (readinessScore >= 50) return 'Solid';
    return 'Building';
  }, [readinessScore]);

  const heroStats = useMemo<HeroStat[]>(() => [
    {
      label: 'Workouts',
      value: String(progress.stats.totalWorkouts ?? 0),
      helper: 'All-time completed',
      icon: Activity,
    },
    {
      label: 'Streak',
      value: `${progress.stats.currentStreak ?? 0} days`,
      helper: `Best ${progress.stats.longestStreak ?? 0} days`,
      icon: Flame,
    },
    {
      label: 'Active plan',
      value: activeProgram?.name ?? 'Not selected',
      helper: activeProgram
        ? `${Math.round(activeProgram.completion_percentage ?? 0)}% complete`
        : 'Choose a program to stay on track',
      icon: Target,
    },
    {
      label: 'Readiness',
      value: readinessLabel,
      helper: `Score ${Math.round(readinessScore)}`,
      icon: Heart,
    },
  ], [activeProgram, progress.stats.currentStreak, progress.stats.longestStreak, progress.stats.totalWorkouts, readinessLabel, readinessScore]);

  const quickStats = useMemo(() => [
    {
      title: 'Training minutes',
      value: formatMinutes(progress.stats.totalWorkoutTime),
      helper: 'Logged this season',
      icon: BarChart3,
    },
    {
      title: "Today's sessions",
      value: todaySessions.length ? `${todaySessions.length} planned` : 'Recovery day',
      helper: upcomingSession?.workout_type
        ? capitalizeWords(upcomingSession.workout_type)
        : upcomingSession
        ? 'Next session queued'
        : 'No sessions scheduled',
      icon: Calendar,
    },
    {
      title: 'Primary goal',
      value: focusGoals.length ? capitalizeWords(focusGoals[0]) : 'Balanced fitness',
      helper: focusGoals.length > 1 ? `+${focusGoals.length - 1} additional goals` : 'Personalised with AI',
      icon: Target,
    },
    {
      title: 'Equipment ready',
      value: `${availableEquipment.length}/${equipment.inventory.length || availableEquipment.length}`,
      helper: 'Available right now',
      icon: Dumbbell,
    },
  ], [availableEquipment.length, equipment.inventory.length, focusGoals, progress.stats.totalWorkoutTime, todaySessions.length, upcomingSession]);

  const achievements = useMemo<ProfileAchievement[]>(() => {
    if (progress.achievements && progress.achievements.length > 0) {
      return progress.achievements.slice(0, 3).map((achievement: StoreAchievement, index: number) => ({
        id: String(achievement.id ?? `achievement-${index}`),
        title: achievement.title ?? capitalizeWords(achievement.category) ?? 'Milestone',
        description: achievement.description ?? 'Keep building momentum to unlock this milestone.',
        icon: achievement.icon ?? Trophy,
        progress: typeof achievement.progress === 'number'
          ? Math.min(100, Math.max(0, Math.round(achievement.progress)))
          : achievement.target && achievement.progress_value
          ? Math.min(100, Math.round((achievement.progress_value / achievement.target) * 100))
          : achievement.unlockedAt || achievement.unlocked_at
          ? 100
          : undefined,
        unlockedAt: achievement.unlockedAt ?? achievement.unlocked_at,
      }));
    }
    return fallbackAchievements;
  }, [progress.achievements]);

  const preferencesSummary = useMemo(() => {
    const theme = user.preferences?.theme ?? 'system';
    const notifications = user.preferences?.notifications ? 'On' : 'Muted';
    const offline = user.preferences?.offlineMode ? 'Enabled' : 'Disabled';
    return [
      { label: 'Theme', value: capitalizeWords(theme) },
      { label: 'Notifications', value: notifications },
      { label: 'Offline mode', value: offline },
    ];
  }, [user.preferences]);

  return (
    <div className="relative min-h-screen bg-gradient-to-b from-background via-background/95 to-background">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-4 pb-24 pt-6 sm:px-6 lg:pt-10">
        <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
          <PageHero
            eyebrow="Profile"
            title={`Hey ${displayName}, ready to train?`}
            description="Review your personalised plan, track your achievements, and keep your AI coaching preferences tuned."
            actions={
              <div className="flex flex-wrap gap-2">
                <Button variant="secondary" onClick={() => router.push('/profile/progress')}>
                  <BarChart3 className="mr-2 h-4 w-4" />
                  View analytics
                </Button>
                <Button variant="outline" onClick={() => router.push('/settings')}>
                  <Settings className="mr-2 h-4 w-4" />
                  Preferences
                </Button>
              </div>
            }
            stats={heroStats}
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.1 }}
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
              transition={{ duration: 0.45, delay: 0.15 }}
            >
              <Card className="border-border/60">
                <CardHeader>
                  <SectionHeader
                    title="Active program"
                    description="Stay locked in with your personalised training roadmap."
                    action={
                      activeProgram ? (
                        <Button variant="outline" size="sm" onClick={() => router.push('/workouts/saved')}>
                          Manage plan
                        </Button>
                      ) : undefined
                    }
                  />
                </CardHeader>
                <CardContent className="space-y-5">
                  {activeProgram ? (
                    <div className="space-y-5">
                      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                        <div>
                          <h3 className="text-2xl font-semibold tracking-tight">{activeProgram.name}</h3>
                          {activeProgram.description && (
                            <p className="mt-2 text-sm text-muted-foreground">{activeProgram.description}</p>
                          )}
                        </div>
                        <Badge variant="secondary" className="self-start capitalize">
                          {capitalizeWords(activeProgram.difficulty_level)}
                        </Badge>
                      </div>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between text-xs uppercase tracking-wide text-muted-foreground">
                          <span>Completion</span>
                          <span>{Math.round(activeProgram.completion_percentage ?? 0)}%</span>
                        </div>
                        <Progress value={Math.round(activeProgram.completion_percentage ?? 0)} className="h-2" />
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-xs uppercase text-muted-foreground">Duration</p>
                            <p className="mt-1 font-medium">{activeProgram.duration_days} days</p>
                          </div>
                          <div>
                            <p className="text-xs uppercase text-muted-foreground">Focus</p>
                            <p className="mt-1 font-medium">{capitalizeWords(activeProgram.program_type ?? focusGoals[0] ?? 'balanced')}</p>
                          </div>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <Button
                          onClick={() => {
                            if (upcomingSession?.id) {
                              router.push(`/workout/${upcomingSession.id}`);
                            } else {
                              router.push('/workouts/saved');
                            }
                          }}
                        >
                          <Sparkles className="mr-2 h-4 w-4" />
                          Continue session
                        </Button>
                        <Button variant="outline" onClick={() => router.push('/profile/progress')}>
                          <BarChart3 className="mr-2 h-4 w-4" />
                          View stats
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4 text-sm text-muted-foreground">
                      <p>Kickstart a tailored program to unlock guided sessions and recovery recommendations.</p>
                      <Button onClick={() => router.push('/generate')}>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Generate my plan
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: 0.2 }}
            >
              <Card className="border-border/60">
                <CardHeader>
                  <SectionHeader
                    title="Today's schedule"
                    description="Preview and adjust your sessions for the day."
                  />
                </CardHeader>
                <CardContent className="space-y-4">
                  {todaySessions.length ? (
                    <div className="space-y-3">
                      {todaySessions.map((session) => (
                        <div
                          key={session.id ?? session.scheduled_date?.toString() ?? Math.random().toString(36)}
                          className="flex flex-col gap-3 rounded-2xl border border-border/60 bg-muted/15 p-4 sm:flex-row sm:items-center sm:justify-between"
                        >
                          <div>
                            <div className="flex items-center gap-2">
                              <h4 className="text-base font-semibold">{capitalizeWords(session.workout_type ?? 'Custom session')}</h4>
                              <Badge variant="outline" className="capitalize text-xs">
                                {capitalizeWords(session.completion_status ?? 'pending')}
                              </Badge>
                            </div>
                            <p className="text-xs text-muted-foreground">{formatScheduleDate(session.scheduled_date)}</p>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => router.push(`/workout/${session.id}`)}
                            >
                              Open
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="rounded-2xl border border-dashed border-border/60 bg-muted/20 p-8 text-center text-sm text-muted-foreground">
                      Nothing scheduled today. Let the AI build a focused session for you.
                      <div className="mt-4">
                        <Button variant="outline" onClick={() => router.push('/generate')}>
                          <Sparkles className="mr-2 h-4 w-4" />
                          Create a session
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: 0.25 }}
            >
              <Card className="border-border/60">
                <CardHeader>
                  <SectionHeader
                    title="Achievement highlights"
                    description="Celebrate wins and uncover your next milestones."
                    action={
                      <Button variant="ghost" size="sm" className="text-muted-foreground" onClick={() => router.push('/profile/achievements')}>
                        See all
                        <ChevronRight className="ml-1 h-4 w-4" />
                      </Button>
                    }
                  />
                </CardHeader>
                <CardContent className="space-y-4">
                  {achievements.map((achievement) => {
                    const Icon = achievement.icon ?? Trophy;
                    return (
                      <div key={achievement.id} className="rounded-2xl border border-border/60 bg-muted/15 p-4">
                        <div className="flex items-start gap-3">
                          <div className="rounded-2xl bg-primary/10 p-2 text-primary">
                            <Icon className="h-5 w-5" />
                          </div>
                          <div className="flex-1 space-y-2">
                            <div>
                              <h4 className="text-sm font-semibold">{achievement.title}</h4>
                              <p className="text-xs text-muted-foreground">{achievement.description}</p>
                            </div>
                            {typeof achievement.progress === 'number' && achievement.progress < 100 && (
                              <div>
                                <Progress value={achievement.progress} className="h-2" />
                                <p className="mt-1 text-xs text-muted-foreground">{achievement.progress}% complete</p>
                              </div>
                            )}
                            {achievement.unlockedAt && (
                              <p className="text-xs text-muted-foreground">
                                Unlocked {formatScheduleDate(achievement.unlockedAt)}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </CardContent>
              </Card>
            </motion.div>
          </div>

          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: 0.18 }}
            >
              <Card className="border-border/60">
                <CardHeader>
                  <CardTitle>Your goals & context</CardTitle>
                  <CardDescription>What the AI knows about your priorities.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 text-sm text-muted-foreground">
                  <div className="space-y-2">
                    <p className="text-xs uppercase tracking-wide text-muted-foreground">Primary focus</p>
                    <div className="flex flex-wrap gap-2">
                      {(focusGoals.length ? focusGoals.slice(0, 4) : ['balanced_fitness']).map((goal) => (
                        <Badge key={goal} variant="secondary" className="capitalize">
                          {capitalizeWords(goal)}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <p className="text-xs uppercase tracking-wide text-muted-foreground">Training context</p>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4 text-muted-foreground" />
                        <span>Prefers {user.profile?.scheduling_preferences?.preferred_time ?? 'flexible timing'}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <User className="h-4 w-4 text-muted-foreground" />
                        <span>{capitalizeWords(user.profile?.experience_level ?? 'intermediate')} experience level</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: 0.22 }}
            >
              <Card className="border-border/60">
                <CardHeader>
                  <CardTitle>Preferences</CardTitle>
                  <CardDescription>Quick overview of your app configuration.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 text-sm">
                  {preferencesSummary.map((item) => (
                    <div key={item.label} className="flex items-center justify-between rounded-2xl border border-border/60 bg-muted/20 px-4 py-3">
                      <span className="text-muted-foreground">{item.label}</span>
                      <span className="font-medium text-foreground">{item.value}</span>
                    </div>
                  ))}
                  <Button variant="outline" className="w-full" onClick={() => router.push('/settings')}>
                    Adjust preferences
                  </Button>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: 0.26 }}
            >
              <Card className="border-border/60">
                <CardHeader>
                  <CardTitle>Quick actions</CardTitle>
                  <CardDescription>Jump straight to the tools you use most often.</CardDescription>
                </CardHeader>
                <CardContent className="grid grid-cols-2 gap-3">
                  <Button
                    variant="outline"
                    className="h-auto flex flex-col items-center gap-2 rounded-2xl border-border/60 p-4"
                    onClick={() => router.push('/profile/progress')}
                  >
                    <BarChart3 className="h-5 w-5" />
                    <span className="text-sm">Analytics</span>
                  </Button>
                  <Button
                    variant="outline"
                    className="h-auto flex flex-col items-center gap-2 rounded-2xl border-border/60 p-4"
                    onClick={() => router.push('/profile/achievements')}
                  >
                    <Trophy className="h-5 w-5" />
                    <span className="text-sm">Achievements</span>
                  </Button>
                  <Button
                    variant="outline"
                    className="h-auto flex flex-col items-center gap-2 rounded-2xl border-border/60 p-4"
                    onClick={() => router.push('/profile/history')}
                  >
                    <Calendar className="h-5 w-5" />
                    <span className="text-sm">History</span>
                  </Button>
                  <Button
                    variant="outline"
                    className="h-auto flex flex-col items-center gap-2 rounded-2xl border-border/60 p-4"
                    onClick={() => router.push('/generate')}
                  >
                    <Sparkles className="h-5 w-5" />
                    <span className="text-sm">New workout</span>
                  </Button>
                  <Button
                    variant="outline"
                    className="h-auto flex flex-col items-center gap-2 rounded-2xl border-border/60 p-4"
                    onClick={() => router.push('/equipment')}
                  >
                    <Dumbbell className="h-5 w-5" />
                    <span className="text-sm">Equipment</span>
                  </Button>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: 0.3 }}
            >
              <Card className="border-border/60">
                <CardHeader>
                  <CardTitle>Keep the streak going</CardTitle>
                  <CardDescription>Small reminders to help you stay consistent.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 text-sm text-muted-foreground">
                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                    <span className="font-medium text-foreground">Check in after each session.</span> Log how it felt to fine-tune upcoming workouts.
                  </div>
                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                    Refresh your equipment list weekly so the AI respects what you have on hand.
                  </div>
                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                    Schedule active recovery days directly from the generator when your readiness dips.
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>

      <MobileBottomNav current="profile" />
    </div>
  );
}
