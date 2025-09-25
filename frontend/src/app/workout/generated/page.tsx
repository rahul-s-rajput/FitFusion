'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowLeft, Play, Activity, Dumbbell, Timer, Shield, Sparkles } from 'lucide-react';

import { useWorkout } from '../../../store';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';

export default function GeneratedWorkoutPage() {
  const router = useRouter();
  const workoutState = useWorkout();
  const generated = workoutState.generatedWorkout;

  useEffect(() => {
    if (!generated) {
      router.replace('/generate');
    }
  }, [generated, router]);

  if (!generated) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center space-y-4">
        <p className="text-muted-foreground">Loading your generated workout...</p>
        <Button variant="ghost" onClick={() => router.push('/generate')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Generator
        </Button>
      </div>
    );
  }

  const plan = generated.workout || {};
  const warmup = Array.isArray(plan.warmup) ? plan.warmup : [];
  const exercises = Array.isArray(plan.exercises) ? plan.exercises : [];
  const cooldown = Array.isArray(plan.cooldown) ? plan.cooldown : [];
  const safetyNotes = Array.isArray(plan.safety_notes) ? plan.safety_notes : [];
  const equipmentNeeded = Array.isArray(plan.equipment_needed) ? plan.equipment_needed : [];
  const modifications = plan.modifications || {};
  const agentContributions = Array.isArray(generated.agentContributions)
    ? generated.agentContributions
    : [];

  const sessionPath = '/workout/session';

  return (
    <div className="min-h-screen bg-background">
      <div className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Your AI-Generated Workout</h1>
              <p className="text-muted-foreground mt-1">
                Built collaboratively by our specialist AI coaching team.
              </p>
            </div>
            <Button variant="ghost" onClick={() => router.push('/generate')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Generate Another
            </Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8 space-y-8">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <Card className="shadow-sm">
            <CardHeader>
              <CardTitle>{plan.name || 'AI Generated Workout'}</CardTitle>
              <CardDescription>{plan.description || 'A balanced workout tailored to your inputs.'}</CardDescription>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="text-muted-foreground">Workout Type</div>
                <div className="font-semibold capitalize">{plan.workout_type || 'mixed'}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Duration</div>
                <div className="font-semibold">{plan.duration_minutes || 45} minutes</div>
              </div>
              <div>
                <div className="text-muted-foreground">Difficulty</div>
                <div className="font-semibold capitalize">{plan.difficulty_level || 'intermediate'}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Estimated Calories</div>
                <div className="font-semibold">{plan.estimated_calories ? `${plan.estimated_calories} kcal` : '-'}</div>
              </div>
              {generated.executionTime && (
                <div>
                  <div className="text-muted-foreground">AI Generation Time</div>
                  <div className="font-semibold">{generated.executionTime.toFixed(2)} s</div>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {equipmentNeeded.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.05 }}>
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center text-lg"><Dumbbell className="h-5 w-5 mr-2 text-primary" />Required Equipment</CardTitle>
                <CardDescription>Have these items ready to get the most out of your session.</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-wrap gap-2">
                {equipmentNeeded.map((item: string, index: number) => (
                  <Badge key={`equipment-${index}`} variant="secondary" className="capitalize">{item}</Badge>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {warmup.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.1 }}>
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center text-lg"><Activity className="h-5 w-5 mr-2 text-primary" />Warm-up</CardTitle>
                <CardDescription>Prime your body with these movements.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {warmup.map((item: any, index: number) => (
                  <div key={`warmup-${index}`} className="border rounded p-3">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{item.name}</span>
                      {typeof item.duration === 'number' && (
                        <span className="text-sm text-muted-foreground">{Math.round(item.duration / 60)} min</span>
                      )}
                    </div>
                    {item.description && (
                      <p className="text-sm text-muted-foreground mt-1">{item.description}</p>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {exercises.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.15 }}>
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center text-lg"><Dumbbell className="h-5 w-5 mr-2 text-primary" />Main Workout</CardTitle>
                <CardDescription>Core exercises selected by the AI team.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {exercises.map((exercise: any, index: number) => (
                  <div key={`exercise-${index}`} className="border rounded p-3">
                    <div className="flex items-center justify-between flex-wrap gap-2">
                      <span className="font-medium">{exercise.name}</span>
                      <div className="text-sm text-muted-foreground space-x-2">
                        {exercise.sets && <span>{exercise.sets} sets</span>}
                        {exercise.reps && <span>{exercise.reps} reps</span>}
                        {exercise.duration && <span>{exercise.duration}s</span>}
                      </div>
                    </div>
                    {exercise.description && (
                      <p className="text-sm text-muted-foreground mt-1">{exercise.description}</p>
                    )}
                    {exercise.tips && (
                      <p className="text-xs text-muted-foreground mt-1">Tips: {exercise.tips}</p>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {cooldown.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.2 }}>
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center text-lg"><Timer className="h-5 w-5 mr-2 text-primary" />Cooldown</CardTitle>
                <CardDescription>Finish strong and recover safely.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {cooldown.map((item: any, index: number) => (
                  <div key={`cooldown-${index}`} className="border rounded p-3">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{item.name}</span>
                      {typeof item.duration === 'number' && (
                        <span className="text-sm text-muted-foreground">{Math.round(item.duration / 60)} min</span>
                      )}
                    </div>
                    {item.description && (
                      <p className="text-sm text-muted-foreground mt-1">{item.description}</p>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {safetyNotes.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.25 }}>
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center text-lg"><Shield className="h-5 w-5 mr-2 text-primary" />Safety Notes</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                  {safetyNotes.map((note: string, index: number) => (
                    <li key={`safety-${index}`}>{note}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {Object.keys(modifications).length > 0 && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.3 }}>
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg">Exercise Modifications</CardTitle>
                <CardDescription>Alternative options tailored to your equipment and preferences.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                {Object.entries(modifications).map(([key, value]) => (
                  <div key={`mod-${key}`} className="border rounded p-3">
                    <div className="font-medium capitalize">{key.replace(/_/g, ' ')}</div>
                    {Array.isArray(value) ? (
                      <ul className="list-disc list-inside text-muted-foreground mt-1 space-y-1">
                        {(value as any[]).map((item, idx) => (
                          <li key={`mod-item-${idx}`}>{typeof item === 'string' ? item : item?.description || 'Alternative option'}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-muted-foreground mt-1">{String(value)}</p>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {agentContributions.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.35 }}>
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center text-lg"><Sparkles className="h-5 w-5 mr-2 text-primary" />Agent Contributions</CardTitle>
                <CardDescription>How each FitFusion specialist influenced this workout.</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                {agentContributions.map((contribution: any, index: number) => (
                  <div key={`contrib-${index}`} className="border rounded p-3 space-y-1">
                    <div className="font-semibold capitalize">{contribution.agent_name?.replace(/_/g, ' ') || 'Agent'}</div>
                    {contribution.contribution_type && (
                      <Badge variant="outline" className="text-xs">{contribution.contribution_type}</Badge>
                    )}
                    {contribution.content?.summary && (
                      <p className="text-muted-foreground">{contribution.content.summary}</p>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        )}

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.4 }}
          className="flex flex-col md:flex-row md:space-x-3 space-y-3 md:space-y-0 justify-center"
        >
          <Button className="md:flex-1" onClick={() => router.push(sessionPath)}>
            <Play className="h-4 w-4 mr-2" />
            Start Guided Session
          </Button>
          <Button variant="outline" className="md:flex-1" onClick={() => router.push('/')}>Return Home</Button>
        </motion.div>
      </div>
    </div>
  );
}
