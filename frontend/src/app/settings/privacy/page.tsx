'use client';

import { useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Shield, KeyRound, Database, Trash2, Download, Eye, ArrowLeft } from 'lucide-react';

import { useUIActions, useUser } from '../../../store';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { PageHero, type HeroStat } from '../../../components/workouts/page-hero';
import { SectionHeader } from '../../../components/workouts/section-header';
import { MobileBottomNav } from '../../../components/workouts/mobile-bottom-nav';

export default function PrivacySettingsPage() {
  const router = useRouter();
  const user = useUser();
  const { setCurrentPage } = useUIActions();

  useEffect(() => {
    setCurrentPage('profile');
  }, [setCurrentPage]);

  const heroStats = useMemo<HeroStat[]>(
    () => [
      {
        label: 'Data cache',
        value: '12.4 MB',
        helper: 'Stored locally',
        icon: Database,
      },
      {
        label: 'AI history',
        value: user.preferences.offlineMode ? 'Local only' : 'Synced',
        helper: 'Conversation storage',
        icon: Shield,
      },
      {
        label: 'Privacy mode',
        value: user.preferences.syncEnabled ? 'Sync on' : 'Manual',
        helper: 'Cloud backup status',
        icon: KeyRound,
      },
    ],
    [user.preferences.offlineMode, user.preferences.syncEnabled],
  );

  return (
    <div className="relative min-h-screen bg-gradient-to-b from-background via-background/95 to-background">
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-8 px-4 pb-24 pt-6 sm:px-6 lg:pt-10">
        <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
          <PageHero
            eyebrow="Privacy"
            title="Control how your data travels"
            description="Export workout history, manage synced content, and review AI usage policies."
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
                title="Data controls"
                description="Decide what stays on-device and what syncs to the cloud."
              />
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                Offline mode keeps generated workouts on your device until you manually sync.
              </div>
              <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                Syncing enables cross-device access and backs up your personalised plans.
              </div>
              <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                Export files are encrypted and expire 24 hours after download for security.
              </div>
              <div className="flex flex-wrap gap-2">
                <Button variant="outline" onClick={() => router.push('/profile/history')}>
                  View history timeline
                </Button>
                <Button variant="outline" onClick={() => router.push('/profile/achievements')}>
                  Review badges
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/60">
            <CardHeader>
              <CardTitle>Downloads</CardTitle>
              <CardDescription>Request a copy of your data anytime.</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2 text-sm">
              <Button variant="outline">
                <Download className="mr-2 h-4 w-4" />
                Export workout history
              </Button>
              <Button variant="outline">
                <Eye className="mr-2 h-4 w-4" />
                Review AI policy
              </Button>
            </CardContent>
          </Card>

          <Card className="border-border/60">
            <CardHeader>
              <CardTitle>Erase data</CardTitle>
              <CardDescription>Clear cached content when you need a fresh start.</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2 text-sm">
              <Button variant="outline" className="text-destructive" onClick={() => router.push('/generate')}>
                <Trash2 className="mr-2 h-4 w-4" />
                Delete cached workouts
              </Button>
              <Button variant="outline" onClick={() => router.push('/settings/notifications')}>
                Manage notifications
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <MobileBottomNav current="profile" />
    </div>
  );
}
