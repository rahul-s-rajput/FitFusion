'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Zap, 
  Clock, 
  Target, 
  Dumbbell, 
  Heart, 
  Flame, 
  Users, 
  Settings, 
  Play,
  Pause,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  Sparkles,
  Brain,
  Activity,
  Timer,
  Shield
} from 'lucide-react';

import { useWorkout, useUser, useEquipment, useWorkoutActions, useUIActions } from '../../store';
import { apiClient, GenerationTask } from '../../lib/api-client';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Progress } from '../../components/ui/progress';
import { PageHero, type HeroStat } from '../../components/workouts/page-hero';
import { SectionHeader } from '../../components/workouts/section-header';
import { QuickStatCard } from '../../components/workouts/quick-stat-card';
import { MobileBottomNav } from '../../components/workouts/mobile-bottom-nav';

export default function GeneratePage() {
  const router = useRouter();
  const workout = useWorkout();
  const user = useUser();
  const equipment = useEquipment();
  const { setGenerationState, startWorkoutGeneration, setGenerationTaskId, completeWorkoutGeneration, setGenerationError } = useWorkoutActions();
  const { setCurrentPage, addNotification } = useUIActions();

  const [currentStep, setCurrentStep] = useState(1);
  const [generationRequest, setGenerationRequest] = useState({
    workout_type: 'mixed',
    duration_minutes: 45,
    difficulty_level: 'intermediate',
    focus_areas: [] as string[],
    equipment_preference: 'available',
    special_requirements: [] as string[]
  });
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [agentInfo, setAgentInfo] = useState<any>(null);
  const generatedWorkout = workout.generatedWorkout?.workout;
  const generatedAgentContributions = workout.generatedWorkout?.agentContributions || [];

  const capitalize = (value?: string | null) => {
    if (!value) return '';
    return value
      .toString()
      .trim()
      .split(/[\s_-]+/)
      .filter(Boolean)
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(' ');
  };

  const formatSeconds = (value?: number | string | null) => {
    if (value === undefined || value === null) return null;
    const numeric = typeof value === 'number' ? value : Number(value);
    if (!Number.isFinite(numeric) || numeric <= 0) return null;
    const total = Math.round(numeric);
    const minutes = Math.floor(total / 60);
    const seconds = total % 60;
    if (minutes > 0 && seconds > 0) return `${minutes}m ${seconds}s`;
    if (minutes > 0) return `${minutes}m`;
    return `${seconds}s`;
  };

  const buildExerciseMeta = (exercise: any) => {
    const parts: string[] = [];
    if (exercise?.sets) parts.push(`${exercise.sets} sets`);
    if (exercise?.reps) parts.push(`${exercise.reps} reps`);
    const workDisplay = formatSeconds(exercise?.work_seconds || exercise?.duration_seconds_per_set);
    if (!exercise?.reps && workDisplay) parts.push(workDisplay);
    const restDisplay = formatSeconds(exercise?.rest_seconds);
    if (restDisplay) parts.push(`Rest ${restDisplay}`);
    return parts.join(' | ');
  };

  const normalizeCues = (value: any): string[] => {
    if (!value) return [];
    if (Array.isArray(value)) return value.filter(Boolean).map((cue) => String(cue));
    return [String(value)];
  };

  const workoutTypes = [
    { value: 'strength', label: 'Strength Training', icon: Dumbbell, description: 'Build muscle and power' },
    { value: 'cardio', label: 'Cardio', icon: Heart, description: 'Improve cardiovascular health' },
    { value: 'hiit', label: 'HIIT', icon: Flame, description: 'High-intensity intervals' },
    { value: 'mixed', label: 'Mixed Training', icon: Activity, description: 'Balanced workout approach' },
  ];

  const difficultyLevels = [
    { value: 'beginner', label: 'Beginner', description: 'New to fitness' },
    { value: 'intermediate', label: 'Intermediate', description: 'Some experience' },
    { value: 'advanced', label: 'Advanced', description: 'Experienced athlete' }
  ];

  const focusAreas = [
    'upper_body', 'lower_body', 'core', 'full_body', 'flexibility', 'balance', 'endurance', 'power'
  ];

  const specialRequirements = [
    'low_impact', 'quiet_workout', 'no_equipment', 'time_efficient', 'injury_recovery', 'beginner_friendly'
  ];

  useEffect(() => {
    setCurrentPage('generate');
    loadAgentInfo();
  }, []);

  const loadAgentInfo = async () => {
    try {
      const response = await apiClient.getAgentInfo();
      if (response.data) {
        setAgentInfo(response.data);
      }
    } catch (error) {
      console.error('Failed to load agent info:', error);
    }
  };

  const handleStartGeneration = async () => {
    try {
      startWorkoutGeneration();
      setCurrentStep(4);

      const resolvedUserId = user.profile?.id;
      const generationPayload: Record<string, any> = {
        ...generationRequest,
        user_context: {
          user_id: resolvedUserId || 'temp-user',
          fitness_goals: user.profile?.fitness_goals || ['general_fitness'],
          experience_level: user.profile?.experience_level || 'beginner',
          available_equipment: equipment.availableEquipment,
          space_constraints: user.profile?.space_constraints || {},
          time_constraints: { duration: generationRequest.duration_minutes },
          physical_attributes: user.profile?.physical_attributes || {},
          preferences: user.preferences || {}
        }
      };

      if (resolvedUserId) {
        generationPayload.user_id = resolvedUserId;
      }

      const response = await apiClient.startWorkoutGeneration(generationPayload);

      if (response.data?.task_id) {
        setCurrentTaskId(response.data.task_id);
        setGenerationTaskId(response.data.task_id);
        setGenerationState(true, 5, 'Task queued. Coordinating AI agents...');
        pollGenerationStatus(response.data.task_id);
      } else {
        throw new Error('No task ID received');
      }
    } catch (error) {
      console.error('Failed to start generation:', error);
      addNotification({
        type: 'error',
        title: 'Generation Failed',
        message: 'Failed to start workout generation. Please try again.',
      });
      setGenerationState(false);
      setGenerationError('Failed to start workout generation. Please try again.');
    }
  };

  const pollGenerationStatus = async (taskId: string) => {
    let hasFinished = false;

    const timeoutId = setTimeout(() => {
      if (hasFinished) {
        return;
      }

      hasFinished = true;
      setGenerationTaskId(null);
      setGenerationState(false, workout.generationProgress, 'Workout generation timed out. Please try again.');
      setGenerationError('Workout generation timed out. Please try again.');
      addNotification({
        type: 'warning',
        title: 'Generation Timeout',
        message: 'Workout generation is taking longer than expected. Please try again.',
      });
      setCurrentStep(3);
    }, 300000);

    const pollInterval = setInterval(async () => {
      try {
        const response = await apiClient.getGenerationStatus(taskId);
        if (response.data) {
          const task: GenerationTask = response.data;

          const isInProgress = task.status === 'in_progress' || task.status === 'started';
          const progressValue = typeof task.progress === 'number' ? task.progress : workout.generationProgress;
          const messageValue = task.message || workout.generationMessage || 'Processing your workout...';

          setGenerationState(isInProgress, progressValue, messageValue);

          if (task.status === 'completed' && task.workout) {
            hasFinished = true;
            clearInterval(pollInterval);
            clearTimeout(timeoutId);
            setGenerationTaskId(null);
            setCurrentTaskId(null);
            completeWorkoutGeneration({
              workout: task.workout,
              agentContributions: task.agent_contributions || [],
              executionTime: task.execution_time,
              completedAt: task.completed_at,
            });
            addNotification({
              type: 'success',
              title: 'Workout Generated!',
              message: "Your personalized workout is ready. Let's get started!",
            });
            setCurrentStep(5);
          } else if (task.status === 'failed') {
            hasFinished = true;
            clearInterval(pollInterval);
            clearTimeout(timeoutId);
            setGenerationTaskId(null);
            const errorMessage = task.error || 'Workout generation failed. Please try again.';
            setGenerationState(false, progressValue, messageValue);
            setGenerationError(errorMessage);
            addNotification({
              type: 'error',
              title: 'Generation Failed',
              message: errorMessage,
            });
            setCurrentStep(3);
          } else if (task.status === 'cancelled') {
            hasFinished = true;
            clearInterval(pollInterval);
            clearTimeout(timeoutId);
            setGenerationTaskId(null);
            setGenerationState(false, progressValue, 'Generation cancelled.');
            setGenerationError('Workout generation was cancelled.');
            addNotification({
              type: 'info',
              title: 'Generation Cancelled',
              message: 'Workout generation was cancelled.',
            });
            setCurrentStep(1);
          }
        }
      } catch (error) {
        hasFinished = true;
        clearInterval(pollInterval);
        clearTimeout(timeoutId);
        console.error('Failed to poll generation status:', error);
        setGenerationTaskId(null);
        setGenerationState(false);
        setGenerationError('Lost connection to the AI agents while generating your workout. Please try again.');
        addNotification({
          type: 'error',
          title: 'Connection Issue',
          message: 'We lost contact with the AI agents. Please try generating again.',
        });
        setCurrentStep(3);
      }
    }, 2000);
  };

  const handleCancelGeneration = async () => {
    if (currentTaskId) {
      try {
        await apiClient.cancelGeneration(currentTaskId);
        setGenerationState(false, workout.generationProgress, 'Generation cancelled.');
        setGenerationTaskId(null);
        setGenerationError('Workout generation was cancelled.');
        setCurrentTaskId(null);
        setCurrentStep(1);
        addNotification({
          type: 'info',
          title: 'Generation Cancelled',
          message: 'Workout generation has been cancelled.',
        });
      } catch (error) {
        console.error('Failed to cancel generation:', error);
      }
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div>
              <h2 className="text-2xl font-bold mb-2">Choose Your Workout Type</h2>
              <p className="text-muted-foreground">Select the type of training you want to focus on</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {workoutTypes.map((type) => {
                const Icon = type.icon;
                return (
                  <Card
                    key={type.value}
                    className={`cursor-pointer transition-all hover:shadow-md ${
                      generationRequest.workout_type === type.value 
                        ? 'ring-2 ring-primary bg-primary/5' 
                        : ''
                    }`}
                    onClick={() => setGenerationRequest(prev => ({ ...prev, workout_type: type.value }))}
                  >
                    <CardHeader>
                      <div className="flex items-center space-x-3">
                        <Icon className="h-6 w-6 text-primary" />
                        <div>
                          <CardTitle className="text-lg">{type.label}</CardTitle>
                          <CardDescription>{type.description}</CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                  </Card>
                );
              })}
            </div>
          </motion.div>
        );

      case 2:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div>
              <h2 className="text-2xl font-bold mb-2">Workout Details</h2>
              <p className="text-muted-foreground">Set your duration and difficulty level</p>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-3">Duration</label>
                <div className="grid grid-cols-3 gap-3">
                  {[30, 45, 60].map((duration) => (
                    <Button
                      key={duration}
                      variant={generationRequest.duration_minutes === duration ? "default" : "outline"}
                      onClick={() => setGenerationRequest(prev => ({ ...prev, duration_minutes: duration }))}
                      className="flex items-center space-x-2"
                    >
                      <Clock className="h-4 w-4" />
                      <span>{duration} min</span>
                    </Button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-3">Difficulty Level</label>
                <div className="space-y-2">
                  {difficultyLevels.map((level) => (
                    <Card
                      key={level.value}
                      className={`cursor-pointer transition-all ${
                        generationRequest.difficulty_level === level.value 
                          ? 'ring-2 ring-primary bg-primary/5' 
                          : ''
                      }`}
                      onClick={() => setGenerationRequest(prev => ({ ...prev, difficulty_level: level.value }))}
                    >
                      <CardHeader className="py-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <CardTitle className="text-base">{level.label}</CardTitle>
                            <CardDescription className="text-sm">{level.description}</CardDescription>
                          </div>
                          <Target className="h-5 w-5 text-muted-foreground" />
                        </div>
                      </CardHeader>
                    </Card>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        );

      case 3:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div>
              <h2 className="text-2xl font-bold mb-2">Customize Your Workout</h2>
              <p className="text-muted-foreground">Add focus areas and special requirements</p>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-3">Focus Areas (Optional)</label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {focusAreas.map((area) => (
                    <Button
                      key={area}
                      variant={generationRequest.focus_areas.includes(area) ? "default" : "outline"}
                      size="sm"
                      onClick={() => {
                        setGenerationRequest(prev => ({
                          ...prev,
                          focus_areas: prev.focus_areas.includes(area)
                            ? prev.focus_areas.filter(a => a !== area)
                            : [...prev.focus_areas, area]
                        }));
                      }}
                      className="capitalize"
                    >
                      {area.replace('_', ' ')}
                    </Button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-3">Special Requirements (Optional)</label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {specialRequirements.map((req) => (
                    <Button
                      key={req}
                      variant={generationRequest.special_requirements.includes(req) ? "default" : "outline"}
                      size="sm"
                      onClick={() => {
                        setGenerationRequest(prev => ({
                          ...prev,
                          special_requirements: prev.special_requirements.includes(req)
                            ? prev.special_requirements.filter(r => r !== req)
                            : [...prev.special_requirements, req]
                        }));
                      }}
                      className="capitalize text-left justify-start"
                    >
                      {req.replace('_', ' ')}
                    </Button>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium mb-3">Available Equipment</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {equipment.availableEquipment.length > 0 ? (
                    equipment.availableEquipment.map((item) => (
                      <div key={item.id} className="flex items-center space-x-2 p-2 border rounded">
                        <Dumbbell className="h-4 w-4 text-primary" />
                        <span className="text-sm">{item.name}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-muted-foreground col-span-full">No equipment available - bodyweight workout will be generated</p>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        );

      case 4:
        return (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center space-y-6"
          >
            <div className="relative">
              <div className="w-24 h-24 mx-auto mb-6 relative">
                <div className="absolute inset-0 rounded-full border-4 border-primary/20"></div>
                <div 
                  className="absolute inset-0 rounded-full border-4 border-primary border-t-transparent animate-spin"
                  style={{ animationDuration: '1s' }}
                ></div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <Brain className="h-8 w-8 text-primary" />
                </div>
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-bold mb-2">AI Agents Working</h2>
              <p className="text-muted-foreground mb-4">{workout.generationMessage}</p>
              <Progress value={workout.generationProgress} className="w-full max-w-md mx-auto" />
              <p className="text-sm text-muted-foreground mt-2">{workout.generationProgress}% Complete</p>
            </div>

            {agentInfo && (
              <div className="max-w-md mx-auto">
                <h3 className="text-lg font-medium mb-3">Active AI Agents</h3>
                <div className="grid grid-cols-2 gap-2">
                  {Object.keys(agentInfo.agents).slice(0, 4).map((agentName) => (
                    <div key={agentName} className="flex items-center space-x-2 p-2 bg-muted rounded">
                      <Sparkles className="h-4 w-4 text-primary" />
                      <span className="text-sm capitalize">{agentName.replace('_', ' ')}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <Button variant="outline" onClick={handleCancelGeneration}>
              <Pause className="h-4 w-4 mr-2" />
              Cancel Generation
            </Button>
          </motion.div>
        );

      case 5:
        return (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="space-y-8"
          >
            <div className="text-center space-y-6">
              <div className="w-24 h-24 mx-auto bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle className="h-12 w-12 text-green-600" />
              </div>

              <div>
                <h2 className="text-2xl font-bold mb-2">Workout Generated!</h2>
                <p className="text-muted-foreground max-w-xl mx-auto">
                  {generatedWorkout?.description || 'Your personalized workout is ready. Our AI agents have crafted the perfect session for you.'}
                </p>
              </div>
            </div>

            {generatedWorkout ? (
              <div className="max-w-3xl mx-auto space-y-8 text-left">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div className="p-4 bg-muted rounded">
                    <div className="font-medium text-muted-foreground">Workout Name</div>
                    <div className="text-base font-semibold">{generatedWorkout.name || 'AI Generated Workout'}</div>
                  </div>
                  <div className="p-4 bg-muted rounded">
                    <div className="font-medium text-muted-foreground">Duration</div>
                    <div>{generatedWorkout.duration_minutes || generationRequest.duration_minutes} minutes</div>
                  </div>
                  <div className="p-4 bg-muted rounded">
                    <div className="font-medium text-muted-foreground">Difficulty</div>
                    <div className="capitalize">{generatedWorkout.difficulty_level || generationRequest.difficulty_level}</div>
                  </div>
                  <div className="p-4 bg-muted rounded">
                    <div className="font-medium text-muted-foreground">Workout Type</div>
                    <div className="capitalize">{generatedWorkout.workout_type || generationRequest.workout_type}</div>
                  </div>
                  {generatedWorkout.estimated_calories && (
                    <div className="p-4 bg-muted rounded">
                      <div className="font-medium text-muted-foreground">Estimated Calories</div>
                      <div>{generatedWorkout.estimated_calories} kcal</div>
                    </div>
                  )}
                  {Array.isArray(generatedWorkout.equipment_needed) && generatedWorkout.equipment_needed.length > 0 && (
                    <div className="p-4 bg-muted rounded">
                      <div className="font-medium text-muted-foreground">Equipment Needed</div>
                      <div>{generatedWorkout.equipment_needed.join(', ')}</div>
                    </div>
                  )}
                </div>

                {Array.isArray(generatedWorkout.warmup) && generatedWorkout.warmup.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="text-lg font-semibold flex items-center"><Activity className="h-5 w-5 mr-2 text-primary" />Warm-up</h3>
                    <div className="space-y-2">
                      {generatedWorkout.warmup.slice(0, 5).map((item: any, index: number) => (
                        <div key={`warmup-${index}`} className="p-3 border rounded">
                          <div className="font-medium">{item.name}</div>
                          {formatSeconds(item.duration_seconds ?? item.duration) && (
                            <div className="text-sm text-muted-foreground">
                              {formatSeconds(item.duration_seconds ?? item.duration)}
                            </div>
                          )}
                          {item.focus && (
                            <div className="text-sm text-muted-foreground">Focus: {item.focus.replace(/_/g, ' ')}</div>
                          )}
                          {item.description && (
                            <div className="text-sm text-muted-foreground">{item.description}</div>
                          )}
                          {normalizeCues(item.coaching_cues).length > 0 && (
                            <ul className="text-xs text-muted-foreground mt-1 list-disc list-inside space-y-1">
                              {normalizeCues(item.coaching_cues).map((cue, cueIdx) => (
                                <li key={`warmup-cue-${index}-${cueIdx}`}>{cue}</li>
                              ))}
                            </ul>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {Array.isArray(generatedWorkout.exercises) && generatedWorkout.exercises.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="text-lg font-semibold flex items-center"><Dumbbell className="h-5 w-5 mr-2 text-primary" />Main Workout</h3>
                    <div className="space-y-2">
                      {generatedWorkout.exercises.slice(0, 8).map((exercise: any, index: number) => (
                        <div key={`exercise-${index}`} className="p-3 border rounded">
                          <div className="font-medium flex justify-between">
                            <span>{exercise.name}</span>
                            {buildExerciseMeta(exercise) && (
                              <span className="text-sm text-muted-foreground text-right">
                                {buildExerciseMeta(exercise)}
                              </span>
                            )}
                          </div>
                          {exercise.description && (
                            <div className="text-sm text-muted-foreground mt-1">{exercise.description}</div>
                          )}
                          {exercise.target_muscles && Array.isArray(exercise.target_muscles) && exercise.target_muscles.length > 0 && (
                            <div className="text-xs text-muted-foreground mt-1">Targets: {exercise.target_muscles.join(', ')}</div>
                          )}
                          {normalizeCues(exercise.coaching_cues).length > 0 && (
                            <ul className="text-xs text-muted-foreground mt-1 list-disc list-inside space-y-1">
                              {normalizeCues(exercise.coaching_cues).map((cue, cueIdx) => (
                                <li key={`exercise-cue-${index}-${cueIdx}`}>{cue}</li>
                              ))}
                            </ul>
                          )}
                          {exercise.tips && !normalizeCues(exercise.coaching_cues).length && (
                            <div className="text-xs text-muted-foreground mt-1">Tips: {exercise.tips}</div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {Array.isArray(generatedWorkout.cooldown) && generatedWorkout.cooldown.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="text-lg font-semibold flex items-center"><Timer className="h-5 w-5 mr-2 text-primary" />Cooldown</h3>
                    <div className="space-y-2">
                      {generatedWorkout.cooldown.slice(0, 5).map((item: any, index: number) => (
                        <div key={`cooldown-${index}`} className="p-3 border rounded">
                          <div className="font-medium">{item.name}</div>
                          {formatSeconds(item.duration_seconds ?? item.duration) && (
                            <div className="text-sm text-muted-foreground">
                              {formatSeconds(item.duration_seconds ?? item.duration)}
                            </div>
                          )}
                          {item.focus && (
                            <div className="text-sm text-muted-foreground">Focus: {item.focus.replace(/_/g, ' ')}</div>
                          )}
                          {item.description && (
                            <div className="text-sm text-muted-foreground">{item.description}</div>
                          )}
                          {normalizeCues(item.coaching_cues).length > 0 && (
                            <ul className="text-xs text-muted-foreground mt-1 list-disc list-inside space-y-1">
                              {normalizeCues(item.coaching_cues).map((cue, cueIdx) => (
                                <li key={`cooldown-cue-${index}-${cueIdx}`}>{cue}</li>
                              ))}
                            </ul>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {Array.isArray(generatedWorkout.safety_notes) && generatedWorkout.safety_notes.length > 0 && (
                  <div className="space-y-2">
                    <h3 className="text-lg font-semibold flex items-center"><Shield className="h-5 w-5 mr-2 text-primary" />Safety Notes</h3>
                    <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                      {generatedWorkout.safety_notes.map((note: string, index: number) => (
                        <li key={`safety-${index}`}>{note}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {generatedAgentContributions.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="text-lg font-semibold flex items-center"><Sparkles className="h-5 w-5 mr-2 text-primary" />Agent Highlights</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {generatedAgentContributions.slice(0, 4).map((contribution: any, index: number) => (
                        <div key={`contrib-${index}`} className="p-3 border rounded">
                          <div className="font-medium capitalize">{contribution.agent_name?.replace(/_/g, ' ') || 'Agent'}</div>
                          {contribution.content?.summary && (
                            <div className="text-sm text-muted-foreground mt-1">{contribution.content.summary}</div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="max-w-md mx-auto text-center space-y-4">
                <p className="text-muted-foreground">
                  We generated a workout but couldn't load the details. Please try generating again.
                </p>
              </div>
            )}

            <div className="flex flex-col md:flex-row md:space-x-3 space-y-3 md:space-y-0 justify-center">
              <Button
                className="md:flex-1"
                onClick={() => router.push('/workout/generated')}
              >
                <Play className="h-4 w-4 mr-2" />
                View Full Workout
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setCurrentStep(1);
                  setGenerationState(false, 0, 'Ready to generate your next workout.');
                  setGenerationTaskId(null);
                  setGenerationError(undefined);
                }}
              >
                Generate Another
              </Button>
            </div>
          </motion.div>
        );


      default:
        return null;
    }
  };



  const stepLabels = ['Setup', 'Focus', 'Preview', 'Result'];

  const agentCount = agentInfo ? Object.keys(agentInfo).length : 0;

  const heroStats: HeroStat[] = [

    {

      label: 'Step',

      value: `${Math.min(currentStep, 4)}/4`,

      helper: 'Generation flow',

      icon: Sparkles,

    },

    {

      label: 'Equipment',

      value: `${equipment.inventory.length} items`,

      helper: `${equipment.availableEquipment.length} ready`,

      icon: Dumbbell,

    },

    {

      label: 'Programs',

      value: String(workout.recentPrograms.length),

      helper: 'Saved sessions',

      icon: Target,

    },

    {

      label: 'AI Coaches',

      value: agentCount ? String(agentCount) : '�',

      helper: agentCount ? 'Specialists online' : 'Fetching agents',

      icon: Users,

    },

  ];



  const quickStatsCards = [

    {

      title: 'Duration',

      value: `${generationRequest.duration_minutes} min`,

      helper: 'Session length',

      icon: Clock,

    },

    {

      title: 'Difficulty',

      value: capitalize(generationRequest.difficulty_level),

      helper: 'Adjust in step two',

      icon: Activity,

    },

    {

      title: 'Focus areas',

      value: generationRequest.focus_areas.length > 0 ? `${generationRequest.focus_areas.length} selected` : 'Not selected',

      helper: 'Pick targets in step two',

      icon: Target,

    },

    {

      title: 'Special cues',

      value: generationRequest.special_requirements.length > 0 ? `${generationRequest.special_requirements.length} chosen` : 'None',

      helper: 'Optional constraints',

      icon: Shield,

    },

  ];



  const showStepIndicator = currentStep < 4;

  const hasGeneratedResult = currentStep === 4 && !!generatedWorkout;



  const heroActions = (

    <>

      <Button size="lg" onClick={() => setCurrentStep(1)}>

        <Sparkles className="mr-2 h-4 w-4" />

        Start Fresh

      </Button>

      {generatedWorkout && (

        <Button size="lg" variant="secondary" onClick={() => router.push('/workout/generated')}>

          <Play className="mr-2 h-4 w-4" />

          Open Last Result

        </Button>

      )}

    </>

  );



  return (

    <div className="relative min-h-screen bg-gradient-to-b from-background via-background/95 to-background">

      <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 pb-24 pt-6 sm:px-6 lg:pt-10">

        <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>

          <PageHero

            eyebrow="AI Generator"

            title="Design your next smart session"

            description="Tune the focus, difficulty, and equipment so our coaching team can craft the perfect workout."

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



        {showStepIndicator && (

          <motion.div

            initial={{ opacity: 0, y: 20 }}

            animate={{ opacity: 1, y: 0 }}

            transition={{ duration: 0.4, delay: 0.15 }}

          >

            <div className="rounded-3xl border border-border/60 bg-card/80 px-4 py-3 shadow-sm sm:px-6">

              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

                <div className="flex items-center gap-3 overflow-x-auto">

                  {stepLabels.map((label, index) => {

                    const stepNumber = index + 1;

                    const isComplete = stepNumber < currentStep;

                    const isActive = stepNumber === currentStep;

                    return (

                      <div key={label} className="flex items-center gap-2">

                        <div

                          className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold ${

                            isActive

                              ? 'bg-primary text-primary-foreground shadow'

                              : isComplete

                                ? 'bg-primary/20 text-primary'

                                : 'bg-muted text-muted-foreground'

                          }`}

                        >

                          {stepNumber}

                        </div>

                        <span className={`text-xs font-medium ${isActive ? 'text-foreground' : 'text-muted-foreground'}`}>

                          {label}

                        </span>

                        {stepNumber < stepLabels.length && (

                          <div className="hidden h-px w-6 bg-border sm:block" />

                        )}

                      </div>

                    );

                  })}

                </div>

                <div className="text-xs font-medium uppercase tracking-wide text-muted-foreground">

                  Step {currentStep} of 4

                </div>

              </div>

            </div>

          </motion.div>

        )}



        <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">

          <motion.div

            initial={{ opacity: 0, y: 20 }}

            animate={{ opacity: 1, y: 0 }}

            transition={{ duration: 0.4, delay: 0.2 }}

          >

            <Card className="border-border/60">

              <CardContent className="space-y-8 p-6 sm:p-8">

                <AnimatePresence mode="wait">

                  {renderStepContent()}

                </AnimatePresence>



                {currentStep < 4 && (

                  <motion.div

                    className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"

                    initial={{ opacity: 0, y: 12 }}

                    animate={{ opacity: 1, y: 0 }}

                    transition={{ duration: 0.3 }}

                  >

                    <Button

                      variant="outline"

                      onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}

                      disabled={currentStep === 1}

                    >

                      Back

                    </Button>

                    {currentStep < 3 ? (

                      <Button onClick={() => setCurrentStep(currentStep + 1)}>

                        Next

                        <ChevronRight className="ml-2 h-4 w-4" />

                      </Button>

                    ) : (

                      <Button onClick={handleStartGeneration} disabled={workout.isGenerating}>

                        <Sparkles className="mr-2 h-4 w-4" />

                        Generate Workout

                      </Button>

                    )}

                  </motion.div>

                )}



                {hasGeneratedResult && (

                  <div className="flex flex-col gap-3 rounded-2xl border border-border/60 bg-muted/20 p-4 text-sm text-muted-foreground">

                    <span>Great work! Review the quick summary or jump into the guided session.</span>

                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">

                      <Button size="sm" onClick={() => router.push('/workout/generated')}>

                        <Play className="mr-2 h-4 w-4" />

                        View Full Workout

                      </Button>

                      <Button

                        size="sm"

                        variant="outline"

                        onClick={() => {

                          setCurrentStep(1);

                          setGenerationState(false, 0, 'Ready to generate your next workout.');

                          setGenerationTaskId(null);

                          setGenerationError(undefined);

                        }}

                      >

                        Generate Another

                      </Button>

                    </div>

                  </div>

                )}

              </CardContent>

            </Card>

          </motion.div>



          <motion.div

            initial={{ opacity: 0, y: 20 }}

            animate={{ opacity: 1, y: 0 }}

            transition={{ duration: 0.4, delay: 0.25 }}

            className="space-y-6"

          >

            <Card className="border-border/60">

              <CardHeader>

                <CardTitle>Session Overview</CardTitle>

                <CardDescription>Live preview of your selections.</CardDescription>

              </CardHeader>

              <CardContent className="space-y-3">

                {quickStatsCards.map((stat) => (

                  <QuickStatCard

                    key={stat.title}

                    title={stat.title}

                    value={stat.value}

                    helper={stat.helper}

                    icon={stat.icon}

                  />

                ))}

              </CardContent>

            </Card>



            <Card className="border-border/60">

              <CardHeader>

                <CardTitle>Agent Team</CardTitle>

                <CardDescription>The specialists assisting this plan.</CardDescription>

              </CardHeader>

              <CardContent className="space-y-3 text-sm text-muted-foreground">

                {agentInfo ? (

                  Object.entries(agentInfo)

                    .slice(0, 4)

                    .map(([key, value]) => (

                      <div key={key} className="rounded-2xl border border-border/60 bg-muted/20 p-3">

                        <div className="text-sm font-semibold capitalize">{key.replace(/_/g, ' ')}</div>

                        {typeof value === 'string' && value && (

                          <p className="mt-1 text-xs text-muted-foreground">{value}</p>

                        )}

                        {typeof value === 'object' && value && (value as any).description && (

                          <p className="mt-1 text-xs text-muted-foreground">{(value as any).description}</p>

                        )}

                      </div>

                    ))

                ) : (

                  <div className="text-sm text-muted-foreground">Loading agent insights...</div>

                )}

              </CardContent>

            </Card>



            <Card className="border-border/60">

              <CardHeader>

                <CardTitle>Helpful tips</CardTitle>

              </CardHeader>

              <CardContent className="space-y-3 text-sm text-muted-foreground">

                <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">

                  Use focus areas to balance strength and mobility work.

                </div>

                <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">

                  Update equipment preference so the AI respects what you have on hand.

                </div>

                <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">

                  Special requirements keep intensity appropriate for recovery days.

                </div>

              </CardContent>

            </Card>

          </motion.div>

        </div>

      </div>



      <MobileBottomNav current="generate" />

    </div>

  );

}

