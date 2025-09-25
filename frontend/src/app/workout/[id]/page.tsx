'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Pause, 
  SkipForward, 
  RotateCcw, 
  Clock, 
  CheckCircle, 
  Circle,
  Heart,
  Zap,
  Target,
  Award,
  Home,
  Settings,
  Volume2,
  VolumeX,
  Timer,
  Activity,
  TrendingUp
} from 'lucide-react';

import { useWorkout, useWorkoutActions, useUIActions, useProgressActions } from '../../../store';
import { apiClient } from '../../../lib/api-client';
import { WorkoutSession } from '../../../lib/db';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Progress } from '../../../components/ui/progress';

interface Exercise {
  id: string;
  name: string;
  sets?: number;
  reps?: number;
  duration?: number;
  weight?: number;
  restTime: number;
  instructions: string;
  targetMuscles: string[];
  completed: boolean;
}

export default function WorkoutExecutionPage() {
  const router = useRouter();
  const params = useParams();
  const workout = useWorkout();
  const { setCurrentSession } = useWorkoutActions();
  const { addNotification, setModalOpen } = useUIActions();
  const { addProgressRecord } = useProgressActions();

  const [session, setSession] = useState<WorkoutSession | null>(null);
  const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);
  const [currentSet, setCurrentSet] = useState(1);
  const [isResting, setIsResting] = useState(false);
  const [restTimer, setRestTimer] = useState(0);
  const [workoutTimer, setWorkoutTimer] = useState(0);
  const [isWorkoutActive, setIsWorkoutActive] = useState(false);
  const [completedSets, setCompletedSets] = useState<Record<string, number>>({});
  const [exerciseNotes, setExerciseNotes] = useState<Record<string, string>>({});
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [showInstructions, setShowInstructions] = useState(true);

  // Mock workout data - would come from API
  const defaultExercises: Exercise[] = [
    {
      id: '1',
      name: 'Push-ups',
      sets: 3,
      reps: 12,
      restTime: 60,
      instructions: 'Start in plank position, lower body until chest nearly touches floor, push back up.',
      targetMuscles: ['chest', 'shoulders', 'triceps'],
      completed: false,
    },
    {
      id: '2',
      name: 'Bodyweight Squats',
      sets: 3,
      reps: 15,
      restTime: 60,
      instructions: 'Stand with feet shoulder-width apart, lower hips back and down, return to standing.',
      targetMuscles: ['quadriceps', 'glutes', 'hamstrings'],
      completed: false,
    },
    {
      id: '3',
      name: 'Plank Hold',
      duration: 45,
      restTime: 60,
      instructions: 'Hold plank position with straight line from head to heels, engage core.',
      targetMuscles: ['core', 'shoulders'],
      completed: false,
    },
    {
      id: '4',
      name: 'Mountain Climbers',
      duration: 30,
      restTime: 60,
      instructions: 'Start in plank, alternate bringing knees to chest rapidly.',
      targetMuscles: ['core', 'shoulders', 'legs'],
      completed: false,
    },
  ];

  const [exercises, setExercises] = useState<Exercise[]>(defaultExercises);

  const buildExercisesFromPlan = (plan: any): Exercise[] => {
    if (!plan) {
      return defaultExercises;
    }

    const built: Exercise[] = [];

    const pushItems = (items: any[] | undefined, category: string) => {
      if (!Array.isArray(items)) return;
      items.forEach((item, index) => {
        built.push({
          id: `${category}-${index}`,
          name: item.name || 'Exercise',
          sets: item.sets ?? item.total_sets ?? undefined,
          reps: item.reps ?? item.target_reps ?? undefined,
          duration: typeof item.duration === 'number' ? Math.round(item.duration) : undefined,
          weight: item.weight ?? undefined,
          restTime: typeof item.rest_time === 'number' ? item.rest_time : 60,
          instructions: item.description || item.instructions || 'Follow the guided cues.',
          targetMuscles: Array.isArray(item.target_muscles) ? item.target_muscles : [],
          completed: false,
        });
      });
    };

    pushItems(plan.warmup, 'warmup');
    pushItems(plan.exercises || plan.main_exercises, 'exercise');
    pushItems(plan.cooldown, 'cooldown');

    return built.length > 0 ? built : defaultExercises;
  };

  useEffect(() => {
    loadWorkoutSession();
  }, [params.id]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isWorkoutActive) {
      interval = setInterval(() => {
        setWorkoutTimer(prev => prev + 1);
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isWorkoutActive]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isResting && restTimer > 0) {
      interval = setInterval(() => {
        setRestTimer(prev => {
          if (prev <= 1) {
            setIsResting(false);
            if (soundEnabled) {
              // Play notification sound
              playNotificationSound();
            }
            addNotification({
              type: 'info',
              title: 'Rest Complete',
              message: 'Time to start your next set!',
            });
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isResting, restTimer, soundEnabled]);

const loadWorkoutSession = async () => {
    try {
      const sessionId = params.id as string;
      if (sessionId === 'generated' || sessionId === 'session') {
        if (workout.generatedWorkout?.workout) {
          const plan = workout.generatedWorkout.workout;
          const generatedSession: WorkoutSession = {
            id: plan.workout_id || Date.now(),
            program_id: undefined,
            user_id: undefined,
            scheduled_date: new Date(),
            warmup_exercises: plan.warmup || [],
            main_exercises: plan.exercises || [],
            cooldown_exercises: plan.cooldown || [],
            workout_type: plan.workout_type,
            estimated_duration: plan.duration_minutes || 45,
            completion_status: 'not_started',
          };
          setSession(generatedSession);
          setCurrentSession(generatedSession);
          setExercises(buildExercisesFromPlan(plan));
        } else {
          const fallbackSession: WorkoutSession = {
            id: Date.now(),
            program_id: undefined,
            user_id: undefined,
            scheduled_date: new Date(),
            warmup_exercises: [],
            main_exercises: [],
            cooldown_exercises: [],
            workout_type: 'mixed',
            estimated_duration: 45,
            completion_status: 'not_started',
          };
          setSession(fallbackSession);
          setCurrentSession(fallbackSession);
          setExercises(defaultExercises);
        }
      } else {
        const response = await apiClient.getWorkoutSession(sessionId);
        if (response.data) {
          setSession(response.data);
          setCurrentSession(response.data);
          setExercises(
            buildExercisesFromPlan({
              warmup: response.data.warmup_exercises,
              exercises: response.data.main_exercises,
              cooldown: response.data.cooldown_exercises,
            })
          );
        }
      }
    } catch (error) {
      console.error('Failed to load workout session:', error);
      addNotification({
        type: 'error',
        title: 'Loading Error',
        message: 'Failed to load workout session.',
      });
    }
  };

  const playNotificationSound = () => {
    // Web Audio API notification sound
    if (typeof window !== 'undefined' && soundEnabled) {
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      oscillator.frequency.value = 800;
      oscillator.type = 'sine';
      
      gainNode.gain.setValueAtTime(0, audioContext.currentTime);
      gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.1);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
      
      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.5);
    }
  };

  const startWorkout = async () => {
    setIsWorkoutActive(true);
    setWorkoutTimer(0);
    
    if (session?.id && typeof session.id === 'number') {
      try {
        await apiClient.startSession(session.id.toString());
      } catch (error) {
        console.error('Failed to start session:', error);
      }
    }
  };

  const pauseWorkout = () => {
    setIsWorkoutActive(false);
  };

  const completeSet = () => {
    const currentExercise = exercises[currentExerciseIndex];
    const exerciseId = currentExercise.id;
    const currentCompletedSets = completedSets[exerciseId] || 0;
    
    setCompletedSets(prev => ({
      ...prev,
      [exerciseId]: currentCompletedSets + 1
    }));

    // Check if exercise is complete
    if (currentExercise.sets && currentCompletedSets + 1 >= currentExercise.sets) {
      completeExercise();
    } else if (!currentExercise.sets) {
      // Duration-based exercise
      completeExercise();
    } else {
      // Start rest timer
      setIsResting(true);
      setRestTimer(currentExercise.restTime);
      setCurrentSet(currentSet + 1);
    }
  };

  const completeExercise = () => {
    const updatedExercises = [...exercises];
    updatedExercises[currentExerciseIndex].completed = true;
    
    if (currentExerciseIndex < exercises.length - 1) {
      setCurrentExerciseIndex(currentExerciseIndex + 1);
      setCurrentSet(1);
    } else {
      completeWorkout();
    }
  };

  const skipExercise = () => {
    if (currentExerciseIndex < exercises.length - 1) {
      setCurrentExerciseIndex(currentExerciseIndex + 1);
      setCurrentSet(1);
      setIsResting(false);
      setRestTimer(0);
    } else {
      completeWorkout();
    }
  };

  const completeWorkout = async () => {
    setIsWorkoutActive(false);
    
    const performanceData = {
      total_duration: workoutTimer,
      exercises_completed: exercises.filter(e => e.completed).length,
      exercises_skipped: exercises.filter(e => !e.completed).length,
      perceived_exertion: 7, // This would come from user input
      notes: 'Great workout session!'
    };

    try {
      if (session?.id && typeof session.id === 'number') {
        await apiClient.completeSession(session.id.toString(), performanceData);
      }
      
      // Add progress record
      addProgressRecord({
        id: Date.now(),
        user_id: 1,
        record_date: new Date(),
        metric_name: 'Workout Completed',
        metric_value: 1,
        metric_unit: 'session',
        notes: `Completed ${exercises.filter(e => e.completed).length}/${exercises.length} exercises`
      });

      addNotification({
        type: 'success',
        title: 'Workout Complete!',
        message: 'Congratulations on finishing your workout!',
      });

      setModalOpen('sessionComplete', true);
    } catch (error) {
      console.error('Failed to complete session:', error);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getWorkoutProgress = () => {
    const completedExercises = exercises.filter(e => e.completed).length;
    return (completedExercises / exercises.length) * 100;
  };

  const currentExercise = exercises[currentExerciseIndex];
  const completedExercises = exercises.filter(e => e.completed).length;

  if (!session) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          <p className="text-muted-foreground">Loading workout...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => router.push('/')}
              >
                <Home className="h-4 w-4" />
              </Button>
              <div>
                <h1 className="text-xl font-bold">Workout Session</h1>
                <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                  <span className="flex items-center">
                    <Clock className="h-3 w-3 mr-1" />
                    {formatTime(workoutTimer)}
                  </span>
                  <span className="flex items-center">
                    <Target className="h-3 w-3 mr-1" />
                    {completedExercises}/{exercises.length} exercises
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSoundEnabled(!soundEnabled)}
              >
                {soundEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowInstructions(!showInstructions)}
              >
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6 space-y-6">
        {/* Progress Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Workout Progress</span>
                <span className="text-sm text-muted-foreground">
                  {Math.round(getWorkoutProgress())}%
                </span>
              </div>
              <Progress value={getWorkoutProgress()} className="h-2" />
            </CardContent>
          </Card>
        </motion.div>

        {/* Rest Timer */}
        <AnimatePresence>
          {isResting && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
            >
              <Card className="border-orange-200 bg-orange-50">
                <CardContent className="text-center p-6">
                  <Timer className="h-12 w-12 text-orange-600 mx-auto mb-4" />
                  <h3 className="text-2xl font-bold text-orange-900 mb-2">Rest Time</h3>
                  <div className="text-4xl font-mono font-bold text-orange-600 mb-4">
                    {formatTime(restTimer)}
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setIsResting(false);
                      setRestTimer(0);
                    }}
                  >
                    Skip Rest
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Current Exercise */}
        <motion.div
          key={currentExerciseIndex}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-2xl">{currentExercise.name}</CardTitle>
                  <CardDescription>
                    Exercise {currentExerciseIndex + 1} of {exercises.length}
                  </CardDescription>
                </div>
                <div className="text-right">
                  {currentExercise.sets ? (
                    <div>
                      <div className="text-2xl font-bold">
                        {completedSets[currentExercise.id] || 0}/{currentExercise.sets}
                      </div>
                      <div className="text-sm text-muted-foreground">sets</div>
                    </div>
                  ) : (
                    <div>
                      <div className="text-2xl font-bold">{currentExercise.duration}s</div>
                      <div className="text-sm text-muted-foreground">duration</div>
                    </div>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Exercise Details */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {currentExercise.reps && (
                  <div className="text-center p-3 bg-muted rounded">
                    <div className="text-xl font-bold">{currentExercise.reps}</div>
                    <div className="text-sm text-muted-foreground">reps</div>
                  </div>
                )}
                {currentExercise.weight && (
                  <div className="text-center p-3 bg-muted rounded">
                    <div className="text-xl font-bold">{currentExercise.weight}kg</div>
                    <div className="text-sm text-muted-foreground">weight</div>
                  </div>
                )}
                <div className="text-center p-3 bg-muted rounded">
                  <div className="text-xl font-bold">{currentExercise.restTime}s</div>
                  <div className="text-sm text-muted-foreground">rest</div>
                </div>
                <div className="text-center p-3 bg-muted rounded">
                  <div className="text-xl font-bold">{currentExercise.targetMuscles.length}</div>
                  <div className="text-sm text-muted-foreground">muscles</div>
                </div>
              </div>

              {/* Target Muscles */}
              <div>
                <h4 className="font-medium mb-2">Target Muscles</h4>
                <div className="flex flex-wrap gap-2">
                  {currentExercise.targetMuscles.map((muscle) => (
                    <Badge key={muscle} variant="secondary" className="capitalize">
                      {muscle}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Instructions */}
              {showInstructions && (
                <div>
                  <h4 className="font-medium mb-2">Instructions</h4>
                  <p className="text-muted-foreground">{currentExercise.instructions}</p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex space-x-3 pt-4">
                {!isWorkoutActive ? (
                  <Button onClick={startWorkout} className="flex-1">
                    <Play className="h-4 w-4 mr-2" />
                    Start Workout
                  </Button>
                ) : (
                  <>
                    <Button onClick={pauseWorkout} variant="outline">
                      <Pause className="h-4 w-4 mr-2" />
                      Pause
                    </Button>
                    <Button onClick={completeSet} className="flex-1">
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Complete {currentExercise.sets ? 'Set' : 'Exercise'}
                    </Button>
                    <Button onClick={skipExercise} variant="outline">
                      <SkipForward className="h-4 w-4 mr-2" />
                      Skip
                    </Button>
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Exercise List */}
        <Card>
          <CardHeader>
            <CardTitle>Exercise Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {exercises.map((exercise, index) => (
                <div
                  key={exercise.id}
                  className={`flex items-center justify-between p-3 rounded-lg border ${
                    index === currentExerciseIndex 
                      ? 'border-primary bg-primary/5' 
                      : exercise.completed 
                        ? 'border-green-200 bg-green-50' 
                        : 'border-muted'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                      exercise.completed 
                        ? 'bg-green-600 text-white' 
                        : index === currentExerciseIndex 
                          ? 'bg-primary text-primary-foreground' 
                          : 'bg-muted'
                    }`}>
                      {exercise.completed ? (
                        <CheckCircle className="h-4 w-4" />
                      ) : (
                        <span className="text-xs font-medium">{index + 1}</span>
                      )}
                    </div>
                    <div>
                      <div className="font-medium">{exercise.name}</div>
                      <div className="text-sm text-muted-foreground">
                        {exercise.sets ? `${exercise.sets} sets × ${exercise.reps} reps` : `${exercise.duration}s`}
                      </div>
                    </div>
                  </div>
                  {exercise.completed && (
                    <Badge variant="default">
                      <Award className="h-3 w-3 mr-1" />
                      Complete
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
