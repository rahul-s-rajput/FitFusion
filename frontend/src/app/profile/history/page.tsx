'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Timeline, Calendar, Target, BarChart3, RefreshCcw, Sparkles, Activity, Clock } from 'lucide-react';

import { useProgress, useProgressActions, useUIActions } from '../../../store';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { PageHero, type HeroStat } from '../../../components/workouts/page-hero';
import { SectionHeader } from '../../../components/workouts/section-header';
import { MobileBottomNav } from '../../../components/workouts/mobile-bottom-nav';

const FILTER_OPTIONS = [
  { value: 'all', label: 'All activity' },
  { value: 'strength', label: 'Strength' },
  { value: 'endurance', label: 'Endurance' },
  { value: 'consistency', label: 'Consistency' },
  { value: 'milestone', label: 'Milestones' },
] as const;

type FilterValue = (typeof FILTER_OPTIONS)[number]['value'];

type TimelineEntry = {
  id: string;
  title: string;
  description: string;
  date: Date;
  metric?: string;
  category: FilterValue;
};

export default function ProfileHistoryPage() {
  const router = useRouter();
  const progress = useProgress();
  const { setProgressLoading } = useProgressActions();
  const { setCurrentPage } = useUIActions();
  const [selectedFilter, setSelectedFilter] = useState<FilterValue>('all');
  const loadingTimeoutRef = useRef<number>();

  useEffect(() => {
    setCurrentPage('profile');
    return () => {
      if (loadingTimeoutRef.current) {
        window.clearTimeout(loadingTimeoutRef.current);
      }
    };
  }, [setCurrentPage]);

  const timelineEntries = useMemo<TimelineEntry[]>(() => {
    const records = progress.recentRecords.length
      ? progress.recentRecords
      : [
          {
            id: 1,
            user_id: 1,
            record_date: new Date(),
            metric_name: 'First workout logged',
            metric_value: 1,
            metric_unit: 'session',
            notes: 'Kick-off entry generated for preview',
          },
        ];

    return records.map((record, index) => ({
      id: String(record.id ?? `record-${index}`),
      title: record.metric_name ?? 'Tracked metric',
      description: record.notes ?? 'Progress captured in your history timeline.',
      date: record.record_date instanceof Date ? record.record_date : new Date(record.record_date ?? Date.now()),
      metric:
        record.metric_value !== undefined && record.metric_unit
          ? `${record.metric_value} ${record.metric_unit}`
          : undefined,
      category:
        (record.metric_name && record.metric_name.toLowerCase().includes('run')) ||
        (record.metric_unit && record.metric_unit.toLowerCase().includes('min'))
          ? 'endurance'
          : record.metric_name?.toLowerCase().includes('press')
          ? 'strength'
          : 'milestone',
    }));
  }, [progress.recentRecords]);

  const filteredEntries = useMemo(() => {
    if (selectedFilter === 'all') {
      return timelineEntries;
    }
    return timelineEntries.filter((entry) => entry.category === selectedFilter);
  }, [selectedFilter, timelineEntries]);

  const heroStats = useMemo<HeroStat[]>(
    () => [
      {
        label: 'Records logged',
        value: `${progress.recentRecords.length || filteredEntries.length}`,
        helper: 'Tracked milestones',
        icon: Timeline,
      },
      {
        label: 'Active streak',
        value: `${progress.stats.currentStreak ?? 0} days`,
        helper: `Best ${progress.stats.longestStreak ?? 0} days`,
        icon: Activity,
      },
      {
        label: 'Training minutes',
        value:
          progress.stats.totalWorkoutTime >= 60
            ? `${Math.round((progress.stats.totalWorkoutTime ?? 0) / 60)} hr`
            : `${progress.stats.totalWorkoutTime ?? 0} min`,
        helper: 'Lifetime logged',
        icon: Clock,
      },
    ],
    [filteredEntries.length, progress.recentRecords.length, progress.stats.currentStreak, progress.stats.longestStreak, progress.stats.totalWorkoutTime],
  );

  const handleFilterChange = (value: FilterValue) => {
    setSelectedFilter(value);
    setProgressLoading(true);
    if (loadingTimeoutRef.current) {
      window.clearTimeout(loadingTimeoutRef.current);
    }
    loadingTimeoutRef.current = window.setTimeout(() => {
      setProgressLoading(false);
    }, 180);
  };

  return (
    <div className="relative min-h-screen bg-gradient-to-b from-background via-background/95 to-background">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-4 pb-24 pt-6 sm:px-6 lg:pt-10">
        <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
          <PageHero
            eyebrow="History"
            title="Review your training story"
            description="Scroll through logged sessions, breakthroughs, and PRs to spot trends."
            actions={
              <div className="flex flex-wrap gap-2">
                <Button variant="outline" onClick={() => router.push('/profile/progress')}>
                  <BarChart3 className="mr-2 h-4 w-4" />
                  View analytics
                </Button>
                <Button onClick={() => router.push('/generate')}>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Log new session
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
          <Card className="border-border/60">
            <CardHeader>
              <SectionHeader
                title="Filters"
                description="Highlight the moments that matter to you."
              />
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {FILTER_OPTIONS.map((option) => (
                <Button
                  key={option.value}
                  variant={selectedFilter === option.value ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => handleFilterChange(option.value)}
                >
                  {option.label}
                </Button>
              ))}
              <Button variant="ghost" size="sm" onClick={() => handleFilterChange('all')}>
                <RefreshCcw className="mr-2 h-4 w-4" />
                Reset
              </Button>
            </CardContent>
          </Card>
        </motion.div>

        <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: 0.14 }}
            >
              <Card className="border-border/60">
                <CardHeader>
                  <CardTitle>Timeline</CardTitle>
                  <CardDescription>Your logged achievements arranged chronologically.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {filteredEntries.length ? (
                    <ol className="space-y-4">
                      {filteredEntries
                        .slice()
                        .sort((a, b) => b.date.getTime() - a.date.getTime())
                        .map((entry) => (
                          <li key={entry.id} className="relative pl-6">
                            <span className="absolute left-0 top-2 h-2 w-2 rounded-full bg-primary" />
                            <div className="rounded-2xl border border-border/60 bg-card/70 p-4">
                              <div className="flex items-center justify-between gap-4">
                                <div>
                                  <p className="text-sm font-semibold">{entry.title}</p>
                                  <p className="text-xs text-muted-foreground">{entry.description}</p>
                                </div>
                                <Badge variant="outline" className="capitalize text-xs">
                                  {entry.category}
                                </Badge>
                              </div>
                              <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                                <div className="flex items-center gap-1">
                                  <Calendar className="h-3.5 w-3.5" />
                                  {entry.date.toLocaleDateString()}
                                </div>
                                {entry.metric && (
                                  <div className="flex items-center gap-1">
                                    <Target className="h-3.5 w-3.5" />
                                    {entry.metric}
                                  </div>
                                )}
                              </div>
                            </div>
                          </li>
                        ))}
                    </ol>
                  ) : (
                    <div className="rounded-2xl border border-dashed border-border/60 bg-muted/20 p-8 text-center text-sm text-muted-foreground">
                      No entries yet. Generate a workout to start building your history.
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
              transition={{ duration: 0.45, delay: 0.18 }}
            >
              <Card className="border-border/60">
                <CardHeader>
                  <CardTitle>Suggested next steps</CardTitle>
                  <CardDescription>Convert insights into action.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 text-sm text-muted-foreground">
                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                    Log a short reflection after each session to enrich your history feed.
                  </div>
                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                    Tag your workouts with goals (strength, endurance, skill) for sharper filtering.
                  </div>
                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                    Revisit milestones monthly to adjust training targets with your coach.
                  </div>
                  <Button variant="outline" className="w-full" onClick={() => router.push('/profile/achievements')}>
                    Review achievements
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
