'use client';

import { motion } from 'framer-motion';
import { ArrowLeft, Sparkles, Lightbulb, Package, Target } from 'lucide-react';
import { useRouter } from 'next/navigation';

import { useEquipment } from '../../../store';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { PageHero, type HeroStat } from '../../../components/workouts/page-hero';
import { SectionHeader } from '../../../components/workouts/section-header';
import { MobileBottomNav } from '../../../components/workouts/mobile-bottom-nav';

const SuggestedEquipmentPage = () => {
  const router = useRouter();
  const equipment = useEquipment();

  const suggestions = equipment.suggestions;

  const heroStats: HeroStat[] = [
    {
      label: 'Suggestions',
      value: String(suggestions.length),
      helper: 'AI generated ideas',
      icon: Sparkles,
    },
    {
      label: 'Inventory',
      value: String(equipment.inventory.length),
      helper: 'Items on hand',
      icon: Package,
    },
    {
      label: 'Categories',
      value: String(new Set(suggestions.map((item: any) => item.category)).size),
      helper: 'Recommended variety',
      icon: Target,
    },
  ];

  return (
    <div className="relative min-h-screen bg-gradient-to-b from-background via-background/95 to-background">
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-8 px-4 pb-24 pt-6 sm:px-6 lg:pt-10">
        <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
          <PageHero
            eyebrow="Suggestions"
            title="Smart upgrades for your setup"
            description="These recommendations take your available space, goals, and recent workouts into account."
            actions={
              <Button variant="outline" onClick={() => router.back()}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to equipment
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
          <Card className="border-border/60">
            <CardHeader>
              <SectionHeader
                title="Recommended additions"
                description="Prioritised list of equipment to expand your training possibilities."
              />
            </CardHeader>
            <CardContent>
              {suggestions.length > 0 ? (
                <div className="space-y-4">
                  {suggestions.map((suggestion: any, index: number) => (
                    <motion.div
                      key={`suggestion-${index}`}
                      className="rounded-2xl border border-border/60 bg-card/80 p-4 shadow-sm"
                      initial={{ opacity: 0, y: 12 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.05 }}
                    >
                      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <h3 className="text-base font-semibold">{suggestion.name}</h3>
                            <Badge variant="outline" className="capitalize">{suggestion.category}</Badge>
                          </div>
                          <p className="text-xs text-muted-foreground">Priority: {suggestion.priority}</p>
                          <p className="text-sm text-muted-foreground">{suggestion.rationale}</p>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          Estimated price: {suggestion.price_range}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="rounded-2xl border border-dashed border-border/60 bg-muted/20 p-8 text-center text-sm text-muted-foreground">
                  Generate a workout to unlock personalised equipment suggestions.
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.15 }}
        >
          <Card className="border-border/60">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-primary" />
                Buying tips
              </CardTitle>
              <CardDescription>Make the most of your investment.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                Prioritise versatile equipment that supports multiple workout types.
              </div>
              <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                Check compatibility with your available space and noise constraints.
              </div>
              <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">
                Mark items you adopt so the AI avoids redundant suggestions.
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <MobileBottomNav current="equipment" />
    </div>
  );
};

export default SuggestedEquipmentPage;
