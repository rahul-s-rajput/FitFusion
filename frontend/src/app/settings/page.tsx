'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Moon, Sun, Bell, Wifi, Database, Shield, ArrowLeft, Settings, Smartphone } from 'lucide-react';
import { useRouter } from 'next/navigation';

import { Button } from '../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { PageHero, type HeroStat } from '../../components/workouts/page-hero';
import { SectionHeader } from '../../components/workouts/section-header';
import { QuickStatCard } from '../../components/workouts/quick-stat-card';
import { MobileBottomNav } from '../../components/workouts/mobile-bottom-nav';

const SettingsPage = () => {
  const router = useRouter();
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [syncEnabled, setSyncEnabled] = useState(true);

  const heroStats: HeroStat[] = [
    {
      label: 'Theme',
      value: theme,
      helper: 'Current appearance',
      icon: Moon,
    },
    {
      label: 'Notifications',
      value: notificationsEnabled ? 'Enabled' : 'Muted',
      helper: 'Workout reminders',
      icon: Bell,
    },
    {
      label: 'Sync',
      value: syncEnabled ? 'Active' : 'Offline',
      helper: 'Data synchronisation',
      icon: Wifi,
    },
  ];

  const quickStats = [
    {
      title: 'Data stored',
      value: '12.4 MB',
      helper: 'Local cache usage',
      icon: Database,
    },
    {
      title: 'Security level',
      value: 'High',
      helper: 'Multi-factor enabled',
      icon: Shield,
    },
    {
      title: 'Devices linked',
      value: '3 devices',
      helper: 'Last sync 2h ago',
      icon: Smartphone,
    },
  ];

  return (
    <div className="relative min-h-screen bg-gradient-to-b from-background via-background/95 to-background">
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-8 px-4 pb-24 pt-6 sm:px-6 lg:pt-10">
        <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
          <PageHero
            eyebrow="Settings"
            title="Fine-tune your FitFusion experience"
            description="Control theme, notifications, offline mode, and privacy preferences from one place."
            actions={
              <Button variant="outline" onClick={() => router.back()}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back
              </Button>
            }
            stats={heroStats}
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
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

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.15 }}
          className="space-y-6"
        >
          <Card className="border-border/60">
            <CardHeader>
              <SectionHeader
                title="Appearance"
                description="Choose how FitFusion looks across devices."
              />
            </CardHeader>
            <CardContent className="flex flex-wrap gap-3 text-sm">
              {['light', 'dark', 'system'].map((value) => (
                <Button
                  key={value}
                  variant={theme === value ? 'default' : 'outline'}
                  onClick={() => setTheme(value as 'light' | 'dark' | 'system')}
                >
                  {value === 'light' && <Sun className="mr-2 h-4 w-4" />}
                  {value === 'dark' && <Moon className="mr-2 h-4 w-4" />}
                  {value === 'system' && <Settings className="mr-2 h-4 w-4" />}
                  {value.charAt(0).toUpperCase() + value.slice(1)}
                </Button>
              ))}
            </CardContent>
          </Card>

          <Card className="border-border/60">
            <CardHeader>
              <SectionHeader
                title="Notifications"
                description="Stay on track with smart reminders and coaching nudges."
              />
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <div className="flex items-center justify-between rounded-2xl border border-border/60 bg-muted/20 px-4 py-3">
                <span>Enable notifications</span>
                <input
                  type="checkbox"
                  checked={notificationsEnabled}
                  onChange={(event) => setNotificationsEnabled(event.target.checked)}
                />
              </div>
              <p>
                You will receive reminders for scheduled workouts, recovery days, and weekly summaries. Adjust channels in the mobile app for granular control.
              </p>
            </CardContent>
          </Card>

          <Card className="border-border/60">
            <CardHeader>
              <SectionHeader
                title="Offline mode"
                description="Control background sync and cache usage for low connectivity sessions."
              />
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <div className="flex items-center justify-between rounded-2xl border border-border/60 bg-muted/20 px-4 py-3">
                <span>Sync automatically</span>
                <input
                  type="checkbox"
                  checked={syncEnabled}
                  onChange={(event) => setSyncEnabled(event.target.checked)}
                />
              </div>
              <p>
                When enabled, FitFusion syncs workouts and equipment updates whenever a connection is available. Disable to conserve data.
              </p>
            </CardContent>
          </Card>

          <Card className="border-border/60">
            <CardHeader>
              <SectionHeader
                title="Privacy controls"
                description="Manage how your data is stored and used across FitFusion services."
              />
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                Export a copy of your workout history and progression metrics at any time.
              </div>
              <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                Permanently delete cached AI conversations and generated workouts.
              </div>
              <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                Review the AI agent policy to understand how your data improves recommendations.
              </div>
              <div className="flex flex-wrap gap-2">
                <Button variant="outline">Export data</Button>
                <Button variant="outline">Delete cache</Button>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/60">
            <CardHeader>
              <CardTitle>Need help?</CardTitle>
              <CardDescription>Jump into detailed controls without leaving the app.</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2 text-sm">
              <Button variant="outline" onClick={() => router.push('/settings/notifications')}>
                <Bell className="mr-2 h-4 w-4" />
                Notification center
              </Button>
              <Button variant="outline" onClick={() => router.push('/settings/privacy')}>
                <Shield className="mr-2 h-4 w-4" />
                Privacy controls
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <MobileBottomNav current="profile" />
    </div>
  );
};

export default SettingsPage;
