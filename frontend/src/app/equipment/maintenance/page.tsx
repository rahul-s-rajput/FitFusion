'use client';

import { useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Wrench, AlertTriangle, Clock, CheckCircle, Droplet, Shield, Sparkles, ArrowLeft, Calendar } from 'lucide-react';

import { useEquipment, useUIActions } from '../../../store';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { PageHero, type HeroStat } from '../../../components/workouts/page-hero';
import { SectionHeader } from '../../../components/workouts/section-header';
import { MobileBottomNav } from '../../../components/workouts/mobile-bottom-nav';

interface MaintenanceItem {
  id: string;
  name: string;
  condition: string;
  lastMaintenance?: Date;
  nextMaintenance?: Date;
  notes?: string;
}

const CONDITION_LABELS: Record<string, { label: string; tone: 'default' | 'secondary' | 'outline' | 'destructive' }> = {
  excellent: { label: 'Excellent', tone: 'secondary' },
  good: { label: 'Good', tone: 'outline' },
  needs_repair: { label: 'Needs repair', tone: 'destructive' },
  fair: { label: 'Fair', tone: 'outline' },
};

export default function EquipmentMaintenancePage() {
  const router = useRouter();
  const equipment = useEquipment();
  const { setCurrentPage } = useUIActions();

  useEffect(() => {
    setCurrentPage('equipment');
  }, [setCurrentPage]);

  const maintenanceItems = useMemo<MaintenanceItem[]>(() =>
    equipment.inventory.map((item, index) => ({
      id: String(item.id ?? `equipment-${index}`),
      name: item.name ?? 'Equipment item',
      condition: item.condition ?? 'good',
      lastMaintenance: item.last_maintenance
        ? new Date(item.last_maintenance)
        : item.updated_at
        ? new Date(item.updated_at)
        : undefined,
      nextMaintenance: item.next_maintenance ? new Date(item.next_maintenance) : undefined,
      notes: item.maintenance_notes ?? undefined,
    })),
  [equipment.inventory]);

  const conditionGroups = useMemo(() => {
    return maintenanceItems.reduce(
      (acc, item) => {
        const key = item.condition ?? 'unknown';
        acc[key] = acc[key] ? [...acc[key], item] : [item];
        return acc;
      },
      {} as Record<string, MaintenanceItem[]>,
    );
  }, [maintenanceItems]);

  const criticalCount = conditionGroups.needs_repair?.length ?? 0;
  const readyCount = (conditionGroups.excellent?.length ?? 0) + (conditionGroups.good?.length ?? 0);
  const upcomingService = maintenanceItems
    .filter((item) => item.nextMaintenance)
    .sort((a, b) => (a.nextMaintenance?.getTime() ?? 0) - (b.nextMaintenance?.getTime() ?? 0))[0];

  const heroStats = useMemo<HeroStat[]>(
    () => [
      {
        label: 'Next service',
        value: upcomingService?.nextMaintenance
          ? upcomingService.nextMaintenance.toLocaleDateString()
          : 'Plan upcoming',
        helper: upcomingService ? upcomingService.name : 'No service scheduled',
        icon: Calendar,
      },
      {
        label: 'Needs attention',
        value: `${criticalCount}`,
        helper: 'Repair soon',
        icon: AlertTriangle,
      },
      {
        label: 'Ready to train',
        value: `${readyCount}`,
        helper: 'Excellent or good condition',
        icon: CheckCircle,
      },
    ],
    [criticalCount, readyCount, upcomingService],
  );

  const quickInsights = useMemo(
    () => [
      {
        title: 'Hydration & cleaning',
        value: `${equipment.inventory.filter((item) => item.category === 'cardio').length}`,
        helper: 'Cardio gear to wipe down',
        icon: Droplet,
      },
      {
        title: 'Safety checks',
        value: `${criticalCount + (conditionGroups.fair?.length ?? 0)}`,
        helper: 'Items to inspect this week',
        icon: Shield,
      },
      {
        title: 'AI suggestions',
        value: `${equipment.suggestions.length}`,
        helper: 'Upgrades to consider',
        icon: Sparkles,
      },
    ],
    [conditionGroups, criticalCount, equipment.inventory, equipment.suggestions.length],
  );

  return (
    <div className="relative min-h-screen bg-gradient-to-b from-background via-background/95 to-background">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-4 pb-24 pt-6 sm:px-6 lg:pt-10">
        <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
          <PageHero
            eyebrow="Equipment maintenance"
            title="Keep your training space dialled in"
            description="Review service status, plan tune-ups, and ensure every session starts with reliable gear."
            actions={
              <div className="flex flex-wrap gap-2">
                <Button variant="outline" onClick={() => router.push('/equipment')}>
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Back to equipment
                </Button>
                <Button onClick={() => router.push('/equipment/suggestions')}>
                  <Sparkles className="mr-2 h-4 w-4" />
                  See upgrade ideas
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
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {quickInsights.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={stat.title}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.05 * index }}
                >
                  <Card className="border-border/60">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">{stat.title}</CardTitle>
                    </CardHeader>
                    <CardContent className="flex items-center gap-3">
                      <span className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-primary">
                        <Icon className="h-4 w-4" />
                      </span>
                      <div>
                        <p className="text-lg font-semibold text-foreground">{stat.value}</p>
                        <p className="text-xs text-muted-foreground">{stat.helper}</p>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
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
                    title="Service schedule"
                    description="Upcoming tune-ups and reminders for your inventory."
                  />
                </CardHeader>
                <CardContent className="space-y-4">
                  {maintenanceItems.length ? (
                    maintenanceItems.map((item) => {
                      const condition = CONDITION_LABELS[item.condition] ?? { label: item.condition, tone: 'outline' };
                      return (
                        <motion.div
                          key={item.id}
                          initial={{ opacity: 0, y: 12 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="rounded-2xl border border-border/60 bg-card/70 p-4"
                        >
                          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                            <div>
                              <div className="flex items-center gap-2">
                                <h3 className="text-sm font-semibold">{item.name}</h3>
                                <Badge variant={condition.tone} className="capitalize text-xs">
                                  {condition.label}
                                </Badge>
                              </div>
                              <p className="text-xs text-muted-foreground">
                                {item.notes ?? 'Log recent maintenance notes to keep everything in sync.'}
                              </p>
                            </div>
                            <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                              <div className="flex items-center gap-1">
                                <Clock className="h-3.5 w-3.5" />
                                Last {item.lastMaintenance ? item.lastMaintenance.toLocaleDateString() : 'session logged'}
                              </div>
                              <div className="flex items-center gap-1">
                                <Wrench className="h-3.5 w-3.5" />
                                Next {item.nextMaintenance ? item.nextMaintenance.toLocaleDateString() : 'schedule upcoming'}
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      );
                    })
                  ) : (
                    <div className="rounded-2xl border border-dashed border-border/60 bg-muted/20 p-8 text-center text-sm text-muted-foreground">
                      No equipment tracked yet. Add your gear to start scheduling maintenance.
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
                  <CardTitle>Reminders</CardTitle>
                  <CardDescription>Quick actions to keep your setup safe.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 text-sm text-muted-foreground">
                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                    Schedule a calendar reminder for items marked &ldquo;needs repair&rdquo; to avoid downtime.
                  </div>
                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                    Use the AI equipment advisor to get replacement suggestions for aging gear.
                  </div>
                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                    Sanitize high-touch equipment (handles, mats) after each session to extend lifespan.
                  </div>
                  <Button variant="outline" className="w-full" onClick={() => router.push('/generate')}>
                    Generate recovery session
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>

      <MobileBottomNav current="equipment" />
    </div>
  );
}
