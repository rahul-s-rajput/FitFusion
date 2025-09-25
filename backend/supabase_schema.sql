-- FitFusion AI Workout App Database Schema
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User Profiles Table
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE,
  fitness_goals JSONB NOT NULL DEFAULT '[]'::jsonb,
  experience_level TEXT NOT NULL CHECK (experience_level IN ('beginner', 'intermediate', 'advanced')),
  physical_attributes JSONB DEFAULT '{}'::jsonb,
  space_constraints JSONB DEFAULT '{}'::jsonb,
  noise_preferences JSONB DEFAULT '{}'::jsonb,
  scheduling_preferences JSONB DEFAULT '{}'::jsonb,
  ai_coaching_settings JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Equipment Table
CREATE TABLE equipment (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  specifications JSONB DEFAULT '{}'::jsonb,
  condition TEXT DEFAULT 'excellent' CHECK (condition IN ('excellent', 'good', 'fair', 'needs_repair')),
  is_available BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Exercises Table (Pre-populated exercise library)
CREATE TABLE exercises (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL UNIQUE,
  category TEXT NOT NULL,
  muscle_groups TEXT[] NOT NULL DEFAULT '{}',
  equipment_required TEXT[] DEFAULT '{}',
  difficulty_level TEXT NOT NULL CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
  instructions TEXT NOT NULL,
  demonstration_media JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Workout Programs Table
CREATE TABLE workout_programs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  duration_days INTEGER NOT NULL CHECK (duration_days > 0),
  difficulty_level TEXT NOT NULL CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
  daily_schedules JSONB NOT NULL DEFAULT '{}'::jsonb,
  ai_generation_metadata JSONB DEFAULT '{}'::jsonb,
  is_active BOOLEAN DEFAULT false,
  completion_percentage DECIMAL(5,2) DEFAULT 0.0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Workout Sessions Table
CREATE TABLE workout_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  program_id UUID REFERENCES workout_programs(id) ON DELETE CASCADE,
  user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
  scheduled_date DATE NOT NULL,
  warmup_exercises JSONB DEFAULT '[]'::jsonb,
  main_exercises JSONB NOT NULL DEFAULT '[]'::jsonb,
  cooldown_exercises JSONB DEFAULT '[]'::jsonb,
  estimated_duration INTEGER, -- in minutes
  completion_status TEXT DEFAULT 'not_started' CHECK (completion_status IN ('not_started', 'in_progress', 'completed', 'skipped')),
  performance_data JSONB DEFAULT '{}'::jsonb,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Progress Records Table
CREATE TABLE progress_records (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
  session_id UUID REFERENCES workout_sessions(id) ON DELETE SET NULL,
  record_date DATE NOT NULL DEFAULT CURRENT_DATE,
  metric_name TEXT NOT NULL,
  metric_value DECIMAL(10,2) NOT NULL,
  metric_unit TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_equipment_user_id ON equipment(user_id);
CREATE INDEX idx_equipment_category ON equipment(category);
CREATE INDEX idx_exercises_category ON exercises(category);
CREATE INDEX idx_exercises_difficulty ON exercises(difficulty_level);
CREATE INDEX idx_workout_programs_user_id ON workout_programs(user_id);
CREATE INDEX idx_workout_programs_active ON workout_programs(is_active);
CREATE INDEX idx_workout_sessions_program_id ON workout_sessions(program_id);
CREATE INDEX idx_workout_sessions_user_id ON workout_sessions(user_id);
CREATE INDEX idx_workout_sessions_date ON workout_sessions(scheduled_date);
CREATE INDEX idx_progress_records_user_id ON progress_records(user_id);
CREATE INDEX idx_progress_records_date ON progress_records(record_date);

-- Updated at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_equipment_updated_at BEFORE UPDATE ON equipment FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_exercises_updated_at BEFORE UPDATE ON exercises FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workout_programs_updated_at BEFORE UPDATE ON workout_programs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workout_sessions_updated_at BEFORE UPDATE ON workout_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) Policies
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE equipment ENABLE ROW LEVEL SECURITY;
ALTER TABLE workout_programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE workout_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE progress_records ENABLE ROW LEVEL SECURITY;

-- Policies for user_profiles
CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON user_profiles FOR INSERT WITH CHECK (auth.uid() = id);

-- Policies for equipment
CREATE POLICY "Users can view own equipment" ON equipment FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own equipment" ON equipment FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own equipment" ON equipment FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own equipment" ON equipment FOR DELETE USING (auth.uid() = user_id);

-- Policies for workout_programs
CREATE POLICY "Users can view own programs" ON workout_programs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own programs" ON workout_programs FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own programs" ON workout_programs FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own programs" ON workout_programs FOR DELETE USING (auth.uid() = user_id);

-- Policies for workout_sessions
CREATE POLICY "Users can view own sessions" ON workout_sessions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own sessions" ON workout_sessions FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own sessions" ON workout_sessions FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own sessions" ON workout_sessions FOR DELETE USING (auth.uid() = user_id);

-- Policies for progress_records
CREATE POLICY "Users can view own progress" ON progress_records FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own progress" ON progress_records FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own progress" ON progress_records FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own progress" ON progress_records FOR DELETE USING (auth.uid() = user_id);

-- Exercises table is public (read-only for users)
ALTER TABLE exercises ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can view exercises" ON exercises FOR SELECT USING (true);

-- Insert some sample exercises
INSERT INTO exercises (name, category, muscle_groups, equipment_required, difficulty_level, instructions) VALUES
('Push-ups', 'strength', ARRAY['chest', 'shoulders', 'triceps'], ARRAY['bodyweight'], 'beginner', 'Start in plank position, lower body to ground, push back up'),
('Squats', 'strength', ARRAY['quadriceps', 'glutes', 'hamstrings'], ARRAY['bodyweight'], 'beginner', 'Stand with feet shoulder-width apart, lower hips back and down, return to standing'),
('Dumbbell Rows', 'strength', ARRAY['back', 'biceps'], ARRAY['dumbbells'], 'intermediate', 'Bend forward, pull dumbbells to chest, squeeze shoulder blades'),
('Jumping Jacks', 'cardio', ARRAY['full_body'], ARRAY['bodyweight'], 'beginner', 'Jump feet apart while raising arms overhead, return to starting position'),
('Plank', 'core', ARRAY['core', 'shoulders'], ARRAY['bodyweight'], 'beginner', 'Hold straight line from head to heels, engage core muscles'),
('Burpees', 'cardio', ARRAY['full_body'], ARRAY['bodyweight'], 'advanced', 'Squat down, jump back to plank, do push-up, jump feet forward, jump up'),
('Dumbbell Chest Press', 'strength', ARRAY['chest', 'shoulders', 'triceps'], ARRAY['dumbbells'], 'intermediate', 'Lie on back, press dumbbells up from chest level'),
('Mountain Climbers', 'cardio', ARRAY['core', 'shoulders'], ARRAY['bodyweight'], 'intermediate', 'Start in plank, alternate bringing knees to chest rapidly'),
('Resistance Band Rows', 'strength', ARRAY['back', 'biceps'], ARRAY['resistance_bands'], 'beginner', 'Pull resistance band to chest, squeeze shoulder blades together'),
('Yoga Flow', 'flexibility', ARRAY['full_body'], ARRAY['yoga_mat'], 'beginner', 'Flow through sun salutation sequence, hold poses for 30 seconds each');
