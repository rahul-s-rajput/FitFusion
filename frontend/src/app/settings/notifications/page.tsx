'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Smartphone, Mail, Calendar, Target, ArrowLeft } from 'lucide-react';

import { useUIActions, useUser } from '../../../store';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { PageHero, type HeroStat } from '../../../components/workouts/page-hero';
import { SectionHeader } from '../../../components/workouts/section-header';
import { MobileBottomNav } from '../../../components/workouts/mobile-bottom-nav';

interface SettingsToggleProps {
  label: string;
  description: string;
  value: boolean;
  onToggle: (value: boolean) => void;
}

function SettingsToggle({ label, description, value, onToggle }: SettingsToggleProps) {
  return (
    <button
      type="button"
      onClick={() => onToggle(!value)}
      className="flex w-full flex-col gap-1 rounded-2xl border border-border/60 bg-muted/20 px-4 py-3 text-left transition hover:border-border"
    >
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-foreground">{label}</span>
        <span
          className={`inline-flex h-5 w-10 items-center rounded-full border border-border/40 ${value ? 'bg-primary/80' : 'bg-muted'}`}
        >
          <span
            className={`ml-1 h-4 w-4 rounded-full bg-background transition ${value ? 'translate-x-4' : ''}`}
          />
        </span>
      </div>
      <span className="text-xs text-muted-foreground">{description}</span>
    </button>
  );
}

export default function NotificationSettingsPage() {
  const router = useRouter();
  const user = useUser();
  const { setCurrentPage } = useUIActions();

  const [pushEnabled, setPushEnabled] = useState(user.preferences.notifications ?? true);
  const [emailEnabled, setEmailEnabled] = useState(true);
  const [calendarSync, setCalendarSync] = useState(true);

  useEffect(() => {
    setCurrentPage('profile');
  }, [setCurrentPage]);

  const heroStats = useMemo<HeroStat[]>(
    () => [
      {
        label: 'Push alerts',
        value: pushEnabled ? 'Enabled' : 'Muted',
        helper: 'Device reminders',
        icon: Smartphone,
      },
      {
        label: 'Email summaries',
        value: emailEnabled ? 'On' : 'Off',
        helper: 'Weekly digest',
        icon: Mail,
      },
      {
        label: 'Calendar sync',
        value: calendarSync ? 'Active' : 'Manual',
        helper: 'Sessions mirrored',
        icon: Calendar,
      },
    ],
    [calendarSync, emailEnabled, pushEnabled],
  );

  return (
    <div className="relative min-h-screen bg-gradient-to-b from-background via-background/95 to-background">
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-8 px-4 pb-24 pt-6 sm:px-6 lg:pt-10">
        <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
          <PageHero
            eyebrow="Notifications"
            title="Stay in the loop"
            description="Fine-tune workout reminders, streak nudges, and recap emails."
            actions={
              <Button variant="outline" onClick={() => router.push('/settings')}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to settings
              </Button>
            }
            stats={heroStats}
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.1 }}
          className="space-y-6"
        >
          <Card className="border-border/60">
            <CardHeader>
              <SectionHeader
                title="Channels"
                description="Choose how FitFusion reaches out."
              />
            </CardHeader>
            <CardContent className="space-y-3">
              <SettingsToggle
                label="Push notifications"
                description="Receive reminders on your mobile device before scheduled workouts."
                value={pushEnabled}
                onToggle={setPushEnabled}
              />
              <SettingsToggle
                label="Email check-ins"
                description="Weekly progress summary and upcoming plan delivered to your inbox."
                value={emailEnabled}
                onToggle={setEmailEnabled}
              />
              <SettingsToggle
                label="Calendar sync"
                description="Automatically add planned sessions to your preferred calendar."
                value={calendarSync}
                onToggle={setCalendarSync}
              />
            </CardContent>
          </Card>

          <Card className="border-border/60">
            <CardHeader>
              <SectionHeader
                title="Coaching cadence"
                description="Control how often FitFusion nudges your habits."
              />
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                Enable push reminders to get alerted 30 minutes before any AI scheduled session.
              </div>
              <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                Weekly email recaps summarise streaks, readiness, and recommended focus areas.
              </div>
              <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                Sync to your calendar to keep training time blocked alongside meetings and personal plans.
              </div>
              <Button variant="outline" onClick={() => router.push('/profile/progress')}>
                <Target className="mr-2 h-4 w-4" />
                Review analytics
              </Button>
            </CardContent>
          </Card>

          <Card className="border-border/60">
            <CardHeader>
              <CardTitle>Need fewer alerts?</CardTitle>
              <CardDescription>Adjust frequency or snooze notifications for recovery weeks.</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2 text-sm">
              <Button variant="outline" onClick={() => setPushEnabled(false)}>
                Pause push alerts
              </Button>
              <Button variant="outline" onClick={() => router.push('/settings/privacy')}>
                Privacy preferences
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <MobileBottomNav current="profile" />
    </div>
  );
}
