'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  Calendar,
  Award,
  Target,
  Activity,
  Clock,
  Flame,
  Zap,
  BarChart3,
  LineChart,
  PieChart,
  Download,
  Share,
  Trophy,
  Medal,
  Star,
  Sparkles,
  Plus,
  type LucideIcon,
} from 'lucide-react';

import { useProgress, useProgressActions, useUIActions } from '../../../store';
import { ProgressRecord } from '../../../lib/db';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Progress } from '../../../components/ui/progress';
import { PageHero, type HeroStat } from '../../../components/workouts/page-hero';
import { SectionHeader } from '../../../components/workouts/section-header';
import { QuickStatCard } from '../../../components/workouts/quick-stat-card';
import { MobileBottomNav } from '../../../components/workouts/mobile-bottom-nav';

interface ProgressMetric {
  name: string;
  value: number;
  unit: string;
  change: number;
  changeType: 'increase' | 'decrease' | 'neutral';
  icon: LucideIcon;
  color: string;
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: LucideIcon;
  unlockedAt?: Date;
  progress?: number;
  target?: number;
  category: 'strength' | 'endurance' | 'consistency' | 'milestone';
}

interface StoreAchievement {
  id?: string | number;
  title?: string;
  name?: string;
  description?: string;
  icon?: LucideIcon;
  unlockedAt?: string | Date;
  unlocked_at?: string | Date;
  progress?: number;
  progress_value?: number;
  target?: number;
  target_value?: number;
  category?: string;
}

const TIMEFRAME_OPTIONS = [
  { value: 'week', label: 'This Week' },
  { value: 'month', label: 'This Month' },
  { value: 'quarter', label: 'This Quarter' },
  { value: 'year', label: 'This Year' },
] as const;

type TimeframeValue = (typeof TIMEFRAME_OPTIONS)[number]['value'];

const FALLBACK_ACHIEVEMENTS: Achievement[] = [
  {
    id: 'milestone-first-steps',
    title: 'First Steps',
    description: 'Complete your first workout',
    icon: Trophy,
    unlockedAt: new Date('2024-01-15'),
    category: 'milestone',
  },
  {
    id: 'consistency-week-warrior',
    title: 'Week Warrior',
    description: 'Complete 7 workouts in a week',
    icon: Medal,
    unlockedAt: new Date('2024-01-22'),
    category: 'consistency',
  },
  {
    id: 'strength-builder',
    title: 'Strength Builder',
    description: 'Complete 10 strength training sessions',
    icon: Award,
    progress: 8,
    target: 10,
    category: 'strength',
  },
  {
    id: 'endurance-master',
    title: 'Endurance Master',
    description: 'Complete 5 hours of cardio training',
    icon: Star,
    progress: 3.5,
    target: 5,
    category: 'endurance',
  },
];

export default function ProgressPage() {
  const router = useRouter();
  const progress = useProgress();
  const { setRecentRecords, updateStats, setProgressLoading } = useProgressActions();
  const { setCurrentPage, addNotification } = useUIActions();

  const [selectedTimeframe, setSelectedTimeframe] = useState<TimeframeValue>('month');
  const [selectedMetric, setSelectedMetric] = useState<string>('all');
  const [chartType, setChartType] = useState<'line' | 'bar' | 'pie'>('line');

    const progressMetrics = useMemo<ProgressMetric[]>(() => {
    const totalWorkouts = progress.stats.totalWorkouts ?? 0;
    const currentStreak = progress.stats.currentStreak ?? 0;
    const totalMinutes = progress.stats.totalWorkoutTime ?? 0;
    const caloriesEstimate = Math.max(0, Math.round(totalMinutes * 6));

    return [
      {
        name: 'Total Workouts',
        value: totalWorkouts,
        unit: 'sessions',
        change: totalWorkouts ? Math.max(1, Math.round(totalWorkouts * 0.15)) : 0,
        changeType: totalWorkouts ? 'increase' : 'neutral',
        icon: Activity,
        color: 'text-blue-600'
      },
      {
        name: 'Workout Streak',
        value: currentStreak,
        unit: 'days',
        change: currentStreak ? 1 : 0,
        changeType: currentStreak ? 'increase' : 'neutral',
        icon: Flame,
        color: 'text-orange-600'
      },
      {
        name: 'Total Duration',
        value: totalMinutes >= 60 ? Math.round(totalMinutes / 60) : totalMinutes,
        unit: totalMinutes >= 60 ? 'hours' : 'minutes',
        change: totalMinutes ? Math.max(1, Math.round(totalMinutes * 0.1)) : 0,
        changeType: totalMinutes ? 'increase' : 'neutral',
        icon: Clock,
        color: 'text-green-600'
      },
      {
        name: 'Calories Burned',
        value: caloriesEstimate,
        unit: 'kcal',
        change: caloriesEstimate ? Math.max(40, Math.round(caloriesEstimate * 0.12)) : 0,
        changeType: caloriesEstimate ? 'increase' : 'neutral',
        icon: Zap,
        color: 'text-purple-600'
      }
    ];
  }, [progress.stats.currentStreak, progress.stats.totalWorkoutTime, progress.stats.totalWorkouts]);

  const achievements = useMemo<Achievement[]>(() => {
    if (progress.achievements && progress.achievements.length > 0) {
      return progress.achievements.map((achievement: StoreAchievement, index: number) => ({
        id: String(achievement.id ?? `achievement-${index}`),
        title: achievement.title ?? achievement.name ?? 'Milestone',
        description: achievement.description ?? 'Keep building momentum to unlock this milestone.',
        icon: achievement.icon ?? Trophy,
        unlockedAt: achievement.unlockedAt
          ? new Date(achievement.unlockedAt)
          : achievement.unlocked_at
          ? new Date(achievement.unlocked_at)
          : undefined,
        progress:
          typeof achievement.progress === 'number'
            ? achievement.progress
            : typeof achievement.progress_value === 'number'
            ? achievement.progress_value
            : undefined,
        target: achievement.target ?? achievement.target_value,
        category: (achievement.category ?? 'milestone') as Achievement['category'],
      }));
    }
    return FALLBACK_ACHIEVEMENTS;
  }, [progress.achievements]);

  const loadProgressData = useCallback(async () => {
    try {
      setProgressLoading(true);

      // Load progress records
      // This would be an actual API call
      const mockRecords: ProgressRecord[] = [
        {
          id: 1,
          user_id: 1,
          record_date: new Date('2024-01-20'),
          metric_name: 'Bench Press',
          metric_value: 80,
          metric_unit: 'kg',
          notes: 'Personal best!'
        },
        {
          id: 2,
          user_id: 1,
          record_date: new Date('2024-01-18'),
          metric_name: '5K Run',
          metric_value: 22.5,
          metric_unit: 'minutes',
          notes: 'Improved by 30 seconds'
        },
        {
          id: 3,
          user_id: 1,
          record_date: new Date('2024-01-15'),
          metric_name: 'Body Weight',
          metric_value: 75.2,
          metric_unit: 'kg',
          notes: 'Weekly weigh-in'
        }
      ];

      setRecentRecords(mockRecords);

      // Update stats
      updateStats({
        totalWorkouts: 24,
        currentStreak: 7,
        longestStreak: 12,
        totalWorkoutTime: 1080, // minutes
        favoriteWorkoutType: 'strength'
      });

    } catch (error) {
      console.error('Failed to load progress data:', error);
      addNotification({
        type: 'error',
        title: 'Loading Error',
        message: 'Failed to load progress data. Please try again.',
      });
    } finally {
      setProgressLoading(false);
    }
  }, [addNotification, selectedTimeframe, setProgressLoading, setRecentRecords, updateStats]);

  useEffect(() => {
    setCurrentPage('profile');
  }, [setCurrentPage]);

  useEffect(() => {
    loadProgressData();
  }, [loadProgressData]);

  const getAchievementProgress = (achievement: Achievement) => {
    if (!achievement.progress || !achievement.target) return 100;
    return (achievement.progress / achievement.target) * 100;
  };

  const getCategoryColor = (category: Achievement['category']) => {
    switch (category) {
      case 'strength': return 'text-red-600 bg-red-100';
      case 'endurance': return 'text-blue-600 bg-blue-100';
      case 'consistency': return 'text-green-600 bg-green-100';
      case 'milestone': return 'text-purple-600 bg-purple-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };



  const totalWorkoutMinutes = progress.stats.totalWorkoutTime ?? 0;

  const workoutTimeLabel = totalWorkoutMinutes >= 60
    ? `${Math.round(totalWorkoutMinutes / 60)} hr`
    : `${totalWorkoutMinutes} min`;

  const achievementsEarned = useMemo(
    () => achievements.filter((item) => Boolean(item.unlockedAt)).length,
    [achievements],
  );

  const favoriteFocus = progress.stats.favoriteWorkoutType
    ? progress.stats.favoriteWorkoutType.replace(/_/g, ' ')
    : 'Not set';

  const activeTimeframeLabel = useMemo(
    () => TIMEFRAME_OPTIONS.find((option) => option.value === selectedTimeframe)?.label ?? 'This Month',
    [selectedTimeframe],
  );

  const heroStats = useMemo<HeroStat[]>(
    () => [
      {
        label: 'Total Workouts',
        value: String(progress.stats.totalWorkouts ?? 0),
        helper: 'All time sessions',
        icon: Activity,
      },
      {
        label: 'Current Streak',
        value: `${progress.stats.currentStreak ?? 0} days`,
        helper: `Best ${progress.stats.longestStreak ?? 0} days`,
        icon: Flame,
      },
      {
        label: 'Workout Time',
        value: workoutTimeLabel,
        helper: 'Lifetime volume',
        icon: Clock,
      },
      {
        label: 'Favourite Focus',
        value: favoriteFocus,
        helper: 'Most completed style',
        icon: Target,
      },
    ],
    [favoriteFocus, progress.stats.currentStreak, progress.stats.longestStreak, progress.stats.totalWorkouts, workoutTimeLabel],
  );

  const quickStatsCards = useMemo(
    () => [
      {
        title: 'Records logged',
        value: `${progress.recentRecords.length}`,
        helper: 'Recent metrics tracked',
        icon: BarChart3,
      },
      {
        title: 'Achievements',
        value: `${achievementsEarned}/${achievements.length}`,
        helper: 'Unlocked badges',
        icon: Trophy,
      },
      {
        title: 'Focus metric',
        value: selectedMetric === 'all' ? 'All metrics' : selectedMetric.replace(/_/g, ' '),
        helper: 'Current filter',
        icon: LineChart,
      },
      {
        title: 'Timeframe',
        value: activeTimeframeLabel,
        helper: 'Viewing window',
        icon: Calendar,
      },
    ],
    [achievements.length, achievementsEarned, activeTimeframeLabel, progress.recentRecords.length, selectedMetric],
  );

  const heroActions = (

    <>

      <Button size="lg" onClick={() => router.push('/generate')}>

        <Sparkles className="mr-2 h-4 w-4" />

        Generate Workout

      </Button>

      <Button size="lg" variant="secondary" onClick={() => router.push('/workouts/saved')}>

        <Target className="mr-2 h-4 w-4" />

        View Programs

      </Button>

    </>

  );



  if (progress.isLoading) {

    return (

      <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-indigo-950 via-slate-950 to-black text-white">

        <div className="h-12 w-12 animate-spin rounded-full border-2 border-white/30 border-t-white" />

        <p className="mt-4 text-sm text-white/70">Loading your progress...</p>

      </div>

    );

  }



  return (

    <div className="relative min-h-screen bg-gradient-to-b from-background via-background/95 to-background">

      <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 pb-24 pt-6 sm:px-6 lg:pt-10">

        <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>

          <PageHero

            eyebrow="Progress hub"

            title="Track your evolution"

            description="Review streaks, achievements, and performance trends tailored to your goals."

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

            {quickStatsCards.map((stat, index) => (

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

                    title="Performance snapshot"

                    description="Key metrics summarising your recent training volume."

                  />

                </CardHeader>

                <CardContent>

                  <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

                    {progressMetrics.map((metric, index) => {

                      const Icon = metric.icon;

                      const changeLabel = metric.changeType === 'increase' ? '+' : metric.changeType === 'decrease' ? '-' : '';

                      const changeColor = metric.changeType === 'increase' ? 'text-emerald-600' : metric.changeType === 'decrease' ? 'text-red-600' : 'text-muted-foreground';

                      return (

                        <motion.div

                          key={metric.name}

                          initial={{ opacity: 0, y: 12 }}

                          animate={{ opacity: 1, y: 0 }}

                          transition={{ duration: 0.3, delay: index * 0.05 }}

                          className="rounded-2xl border border-border/60 bg-card/80 p-4 shadow-sm"

                        >

                          <div className="flex items-center justify-between">

                            <span className="text-xs uppercase tracking-wide text-muted-foreground">{metric.name}</span>

                            <Icon className={`h-5 w-5 ${metric.color}`} />

                          </div>

                          <div className="mt-3 text-2xl font-semibold">

                            {metric.value.toLocaleString()} {metric.unit}

                          </div>

                          <div className={`mt-1 flex items-center text-xs font-medium ${changeColor}`}>

                            {changeLabel}{metric.change} since last {selectedTimeframe}

                          </div>

                        </motion.div>

                      );

                    })}

                  </div>

                </CardContent>

              </Card>

            </motion.div>



            <motion.div

              initial={{ opacity: 0, y: 20 }}

              animate={{ opacity: 1, y: 0 }}

              transition={{ duration: 0.4, delay: 0.2 }}

            >

              <Card className="border-border/60">

                <CardHeader>

                  <SectionHeader

                    title="Progress overview"

                    description="Interactive charts would visualise your selected metrics."

                  />

                </CardHeader>

                <CardContent>

                  <div className="flex h-80 items-center justify-center rounded-2xl border border-dashed border-border/60 bg-muted/20 text-sm text-muted-foreground">

                    <div className="mx-auto max-w-md text-center">

                      <BarChart3 className="mx-auto mb-4 h-14 w-14 text-muted-foreground" />

                      <p>Charts for {activeTimeframeLabel} with {chartType} visualization will appear here.</p>

                    </div>

                  </div>

                </CardContent>

              </Card>

            </motion.div>



            <motion.div

              initial={{ opacity: 0, y: 20 }}

              animate={{ opacity: 1, y: 0 }}

              transition={{ duration: 0.4, delay: 0.25 }}

            >

              <Card className="border-border/60">

                <CardHeader>

                  <SectionHeader

                    title="Achievements"

                    description="Milestones unlocked and goals in progress."

                  />

                </CardHeader>

                <CardContent>

                  <div className="space-y-3">

                    {achievements.map((achievement, index) => {

                      const Icon = achievement.icon;

                      const progressPercent = getAchievementProgress(achievement);

                      const colorClass = getCategoryColor(achievement.category);

                      return (

                        <motion.div

                          key={achievement.id}

                          initial={{ opacity: 0, y: 12 }}

                          animate={{ opacity: 1, y: 0 }}

                          transition={{ duration: 0.3, delay: index * 0.05 }}

                          className="rounded-2xl border border-border/60 bg-card/70 p-4"

                        >

                          <div className="flex items-center justify-between">

                            <div>

                              <div className="flex items-center gap-2">

                                <Icon className="h-4 w-4 text-primary" />

                                <h3 className="text-sm font-semibold">{achievement.title}</h3>

                              </div>

                              <p className="mt-1 text-xs text-muted-foreground">{achievement.description}</p>

                            </div>

                            <span className={`rounded-full px-3 py-1 text-xs font-medium ${colorClass}`}>

                              {achievement.category}

                            </span>

                          </div>

                          {achievement.unlockedAt ? (

                            <div className="mt-3 inline-flex items-center rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700">

                              <Award className="mr-2 h-3 w-3" />

                              Unlocked {achievement.unlockedAt.toLocaleDateString()}

                            </div>

                          ) : achievement.progress && achievement.target ? (

                            <div className="mt-3 space-y-2">

                              <div className="flex items-center justify-between text-xs">

                                <span>Progress</span>

                                <span>{achievement.progress}/{achievement.target}</span>

                              </div>

                              <Progress value={progressPercent} className="h-2" />

                            </div>

                          ) : (

                            <p className="mt-3 text-xs text-muted-foreground">Not started yet</p>

                          )}

                        </motion.div>

                      );

                    })}

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

                  <SectionHeader

                    title="Recent records"

                    description="Latest personal bests and tracked measurements."

                    action={

                      <Button size="sm" onClick={() => router.push('/generate')}>

                        <Plus className="mr-2 h-4 w-4" />

                        Add Record

                      </Button>

                    }

                  />

                </CardHeader>

                <CardContent>

                  {progress.recentRecords.length > 0 ? (

                    <div className="space-y-3">

                      {progress.recentRecords.slice(0, 5).map((record, index) => (

                        <motion.div

                          key={record.id ?? `record-${index}`}

                          className="flex items-center justify-between rounded-2xl border border-border/60 bg-card/70 p-3"

                          initial={{ opacity: 0, x: -20 }}

                          animate={{ opacity: 1, x: 0 }}

                          transition={{ duration: 0.3, delay: index * 0.05 }}

                        >

                          <div>

                            <p className="text-sm font-medium">{record.metric_name}</p>

                            <p className="text-xs text-muted-foreground">{record.record_date.toLocaleDateString()}</p>

                          </div>

                          <div className="text-right text-sm font-semibold">

                            {record.metric_value} {record.metric_unit}

                            {record.notes && (

                              <p className="text-xs text-muted-foreground">{record.notes}</p>

                            )}

                          </div>

                        </motion.div>

                      ))}

                    </div>

                  ) : (

                    <div className="rounded-2xl border border-dashed border-border/60 bg-muted/20 p-6 text-center text-sm text-muted-foreground">

                      No records yet. Add your first measurement to start tracking.

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

              transition={{ duration: 0.4, delay: 0.18 }}

            >

              <Card className="border-border/60">

                <CardHeader>

                  <CardTitle>Filters</CardTitle>

                  <CardDescription>Adjust timeframe and visualisation.</CardDescription>

                </CardHeader>

                <CardContent className="space-y-4 text-sm">

                  <div>

                    <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">Timeframe</p>

                    <div className="flex flex-wrap gap-2">

                      {TIMEFRAME_OPTIONS.map((option) => (

                        <Button

                          key={option.value}

                          variant={selectedTimeframe === option.value ? 'default' : 'outline'}

                          size="sm"

                          onClick={() => setSelectedTimeframe(option.value)}

                        >

                          {option.label}

                        </Button>

                      ))}

                    </div>

                  </div>

                  <div>

                    <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">Chart style</p>

                    <div className="flex gap-2">

                      <Button

                        variant={chartType === 'line' ? 'default' : 'outline'}

                        size="sm"

                        onClick={() => setChartType('line')}

                      >

                        <LineChart className="h-4 w-4" />

                      </Button>

                      <Button

                        variant={chartType === 'bar' ? 'default' : 'outline'}

                        size="sm"

                        onClick={() => setChartType('bar')}

                      >

                        <BarChart3 className="h-4 w-4" />

                      </Button>

                      <Button

                        variant={chartType === 'pie' ? 'default' : 'outline'}

                        size="sm"

                        onClick={() => setChartType('pie')}

                      >

                        <PieChart className="h-4 w-4" />

                      </Button>

                    </div>

                  </div>

                </CardContent>

              </Card>

            </motion.div>



            <motion.div

              initial={{ opacity: 0, y: 20 }}

              animate={{ opacity: 1, y: 0 }}

              transition={{ duration: 0.4, delay: 0.22 }}

            >

              <Card className="border-border/60">

                <CardHeader>

                  <CardTitle>Quick actions</CardTitle>

                  <CardDescription>Keep your progress journal up to date.</CardDescription>

                </CardHeader>

                <CardContent className="grid grid-cols-2 gap-3">

                  <Button variant="outline" className="h-auto flex flex-col items-center gap-2 rounded-2xl border-border/60 p-4" onClick={() => router.push('/profile/progress')}>

                    <Calendar className="h-5 w-5" />

                    <span className="text-sm">View calendar</span>

                  </Button>

                  <Button variant="outline" className="h-auto flex flex-col items-center gap-2 rounded-2xl border-border/60 p-4" onClick={() => setSelectedMetric('strength')}>

                    <Target className="h-5 w-5" />

                    <span className="text-sm">Set goals</span>

                  </Button>

                  <Button variant="outline" className="h-auto flex flex-col items-center gap-2 rounded-2xl border-border/60 p-4" onClick={() => setSelectedMetric('all')}>

                    <TrendingUp className="h-5 w-5" />

                    <span className="text-sm">Reset filters</span>

                  </Button>

                  <Button variant="outline" className="h-auto flex flex-col items-center gap-2 rounded-2xl border-border/60 p-4" onClick={() => router.push('/generate')}>

                    <Sparkles className="h-5 w-5" />

                    <span className="text-sm">Generate workout</span>

                  </Button>

                </CardContent>

              </Card>

            </motion.div>



            <motion.div

              initial={{ opacity: 0, y: 20 }}

              animate={{ opacity: 1, y: 0 }}

              transition={{ duration: 0.4, delay: 0.26 }}

            >

              <Card className="border-border/60">

                <CardHeader>

                  <CardTitle>Share and export</CardTitle>

                  <CardDescription>Download reports or share highlights with your coach.</CardDescription>

                </CardHeader>

                <CardContent className="flex flex-col gap-3 text-sm text-muted-foreground">

                  <Button variant="outline" className="justify-start" onClick={() => addNotification({ type: 'info', title: 'Export coming soon', message: 'Exporting progress will be available in a future update.' })}>

                    <Download className="mr-2 h-4 w-4" />

                    Export summary

                  </Button>

                  <Button variant="outline" className="justify-start" onClick={() => addNotification({ type: 'info', title: 'Share coming soon', message: 'Sharing progress will be available in a future update.' })}>

                    <Share className="mr-2 h-4 w-4" />

                    Share snapshot

                  </Button>

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

