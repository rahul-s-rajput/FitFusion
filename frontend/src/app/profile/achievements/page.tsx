'use client';

import { useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Trophy, Medal, Award, Star, Flame, Target, Sparkles, Calendar, type LucideIcon } from 'lucide-react';

import { useProgress, useUIActions } from '../../../store';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Progress } from '../../../components/ui/progress';
import { PageHero, type HeroStat } from '../../../components/workouts/page-hero';
import { SectionHeader } from '../../../components/workouts/section-header';
import { QuickStatCard } from '../../../components/workouts/quick-stat-card';
import { MobileBottomNav } from '../../../components/workouts/mobile-bottom-nav';

interface AchievementItem {
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

const CATEGORY_COPY: Record<AchievementItem['category'], { label: string; badgeVariant: 'default' | 'secondary' | 'outline' }> = {
  strength: { label: 'Strength', badgeVariant: 'secondary' },
  endurance: { label: 'Endurance', badgeVariant: 'secondary' },
  consistency: { label: 'Consistency', badgeVariant: 'outline' },
  milestone: { label: 'Milestone', badgeVariant: 'default' },
};

const FALLBACK_ACHIEVEMENTS: AchievementItem[] = [
  {
    id: 'starter',
    title: 'Momentum Starter',
    description: 'Logged your first AI-guided workout session.',
    icon: Trophy,
    unlockedAt: new Date('2024-02-10'),
    category: 'milestone',
  },
  {
    id: 'streak-7',
    title: 'Streak Builder',
    description: 'Maintained a 7 day workout streak.',
    icon: Medal,
    unlockedAt: new Date('2024-02-22'),
    category: 'consistency',
  },
  {
    id: 'strength-10',
    title: 'Strength Apprentice',
    description: 'Complete 10 strength-focused sessions.',
    icon: Award,
    progress: 6,
    target: 10,
    category: 'strength',
  },
  {
    id: 'cardio-5h',
    title: 'Cardio Explorer',
    description: 'Clock 5 hours of endurance training.',
    icon: Star,
    progress: 3,
    target: 5,
    category: 'endurance',
  },
];

export default function ProfileAchievementsPage() {
  const router = useRouter();
  const progress = useProgress();
  const { setCurrentPage } = useUIActions();

  useEffect(() => {
    setCurrentPage('profile');
  }, [setCurrentPage]);

  const achievements = useMemo<AchievementItem[]>(() => {
    if (progress.achievements && progress.achievements.length > 0) {
      return progress.achievements.map((achievement: StoreAchievement, index: number) => ({
        id: String(achievement.id ?? `achievement-${index}`),
        title: achievement.title ?? achievement.name ?? 'Milestone achieved',
        description: achievement.description ?? 'Keep building momentum to unlock this milestone.',
        icon: (achievement.icon as AchievementItem['icon']) ?? Trophy,
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
        category: (achievement.category ?? 'milestone') as AchievementItem['category'],
      }));
    }
    return FALLBACK_ACHIEVEMENTS;
  }, [progress.achievements]);

  const unlockedCount = achievements.filter((item) => item.unlockedAt).length;
  const inProgressCount = achievements.length - unlockedCount;
  const bestStreak = progress.stats.longestStreak ?? 0;

  const favouriteFocus = progress.stats.favoriteWorkoutType
    ? progress.stats.favoriteWorkoutType.replace(/_/g, ' ')
    : 'Balanced training';

  const heroStats = useMemo<HeroStat[]>(
    () => [
      {
        label: 'Badges unlocked',
        value: `${unlockedCount}/${achievements.length}`,
        helper: 'Lifetime recognition',
        icon: Trophy,
      },
      {
        label: 'Current streak',
        value: `${progress.stats.currentStreak ?? 0} days`,
        helper: `Best ${bestStreak} days`,
        icon: Flame,
      },
      {
        label: 'Focus area',
        value: favouriteFocus,
        helper: 'Most completed style',
        icon: Target,
      },
    ],
    [achievements.length, bestStreak, favouriteFocus, progress.stats.currentStreak, unlockedCount],
  );

  const quickStats = useMemo(
    () => [
      {
        title: 'In progress',
        value: `${inProgressCount}`,
        helper: 'Badges close to completion',
        icon: Star,
      },
      {
        title: 'Consistency wins',
        value: `${progress.stats.currentStreak ?? 0} day streak`,
        helper: 'Keep it alive today',
        icon: Flame,
      },
      {
        title: 'Upcoming event',
        value: progress.recentRecords[0]?.record_date
          ? new Date(progress.recentRecords[0].record_date).toLocaleDateString()
          : 'Log a record',
        helper: 'Latest milestone',
        icon: Calendar,
      },
    ],
    [inProgressCount, progress.recentRecords, progress.stats.currentStreak],
  );

  return (
    <div className="relative min-h-screen bg-gradient-to-b from-background via-background/95 to-background">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-4 pb-24 pt-6 sm:px-6 lg:pt-10">
        <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
          <PageHero
            eyebrow="Achievements"
            title="Celebrate every milestone"
            description="Track badges, celebrate streaks, and see what’s next on your fitness journey."
            actions={
              <div className="flex flex-wrap gap-2">
                <Button variant="outline" onClick={() => router.push('/profile/progress')}>
                  <Sparkles className="mr-2 h-4 w-4" />
                  View analytics
                </Button>
                <Button onClick={() => router.push('/profile/history')}>
                  <Target className="mr-2 h-4 w-4" />
                  See workout history
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
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
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
              transition={{ duration: 0.45, delay: 0.12 }}
            >
              <Card className="border-border/60">
                <CardHeader>
                  <SectionHeader
                    title="Badge collection"
                    description="Unlockable achievements tailored to your training preferences."
                  />
                </CardHeader>
                <CardContent>
                  {achievements.length ? (
                    <div className="grid gap-4 md:grid-cols-2">
                      {achievements.map((achievement) => {
                        const Icon = achievement.icon ?? Trophy;
                        const category = CATEGORY_COPY[achievement.category] ?? CATEGORY_COPY.milestone;
                        const progressValue = achievement.progress && achievement.target
                          ? Math.min(100, Math.round((achievement.progress / achievement.target) * 100))
                          : achievement.progress
                          ? Math.min(100, Math.round(achievement.progress))
                          : achievement.unlockedAt
                          ? 100
                          : undefined;

                        return (
                          <motion.div
                            key={achievement.id}
                            initial={{ opacity: 0, y: 16 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.35 }}
                            className="flex flex-col gap-3 rounded-2xl border border-border/60 bg-card/70 p-4"
                          >
                            <div className="flex items-start justify-between gap-3">
                              <div className="flex items-center gap-3">
                                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
                                  <Icon className="h-5 w-5" />
                                </span>
                                <div>
                                  <p className="font-semibold leading-tight">{achievement.title}</p>
                                  <p className="text-xs text-muted-foreground">{achievement.description}</p>
                                </div>
                              </div>
                              <Badge variant={category.badgeVariant}>{category.label}</Badge>
                            </div>
                            {achievement.unlockedAt ? (
                              <div className="inline-flex items-center rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700">
                                <Award className="mr-2 h-3 w-3" />
                                Unlocked {achievement.unlockedAt.toLocaleDateString()}
                              </div>
                            ) : progressValue !== undefined ? (
                              <div className="space-y-2">
                                <div className="flex items-center justify-between text-xs text-muted-foreground">
                                  <span>Progress</span>
                                  <span>{progressValue}%</span>
                                </div>
                                <Progress value={progressValue} className="h-2" />
                              </div>
                            ) : (
                              <p className="text-xs text-muted-foreground">Start logging sessions to unlock this badge.</p>
                            )}
                          </motion.div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="rounded-2xl border border-dashed border-border/60 bg-muted/20 p-8 text-center text-sm text-muted-foreground">
                      Achievements will appear here once you start logging progress.
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
              transition={{ duration: 0.45, delay: 0.16 }}
            >
              <Card className="border-border/60">
                <CardHeader>
                  <CardTitle>Streak insights</CardTitle>
                  <CardDescription>Motivation tailored to your current momentum.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 text-sm text-muted-foreground">
                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                    <span className="font-medium text-foreground">{progress.stats.currentStreak ?? 0} day streak</span> — keep the rhythm by scheduling tomorrow’s session now.
                  </div>
                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                    Personalise your next AI workout to target {favouriteFocus.toLowerCase()} and unlock your next badge quicker.
                  </div>
                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                    Celebrate every win: share unlocked badges with training partners for accountability.
                  </div>
                  <Button variant="outline" className="w-full" onClick={() => router.push('/generate')}>
                    Generate next workout
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
