# 🚀 FitFusion Quick Start Guide

Get FitFusion running in 5 minutes!

## 📋 What You Need

1. **Python 3.11+** - [Download here](https://python.org)
2. **Node.js 18+** - [Download here](https://nodejs.org)
3. **Supabase Account** - [Sign up free](https://supabase.com)
4. **Google AI Studio** - [Get API key](https://aistudio.google.com)

## ⚡ Super Quick Setup

### 1. Get Your API Keys

**Supabase:**
1. Go to [supabase.com](https://supabase.com) → New Project
2. Copy your Project URL and anon key from Settings → API

**Google Gemini:**
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Create API key → Copy it

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your keys:
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
GEMINI_API_KEY=your_gemini_key_here
JWT_SECRET_KEY=make_this_super_secret_123
```

### 3. Setup Database

1. Go to your Supabase project → SQL Editor
2. Copy and paste this schema:

```sql
-- User Profiles
CREATE TABLE user_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    email TEXT,
    fitness_goals TEXT[],
    experience_level TEXT,
    physical_attributes JSONB,
    space_constraints JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Equipment
CREATE TABLE equipment (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    specifications JSONB,
    condition TEXT DEFAULT 'good',
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Exercises
CREATE TABLE exercises (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    difficulty_level TEXT,
    equipment_required TEXT[],
    instructions TEXT,
    target_muscles TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Workout Programs
CREATE TABLE workout_programs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    workout_type TEXT,
    difficulty_level TEXT,
    duration_weeks INTEGER,
    sessions_per_week INTEGER,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Workout Sessions
CREATE TABLE workout_sessions (
    id BIGSERIAL PRIMARY KEY,
    program_id BIGINT REFERENCES workout_programs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    scheduled_date DATE,
    warmup_exercises JSONB,
    main_exercises JSONB,
    cooldown_exercises JSONB,
    estimated_duration INTEGER,
    completion_status TEXT DEFAULT 'scheduled',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Progress Records
CREATE TABLE progress_records (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    record_date DATE NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value DECIMAL,
    metric_unit TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE equipment ENABLE ROW LEVEL SECURITY;
ALTER TABLE workout_programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE workout_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE progress_records ENABLE ROW LEVEL SECURITY;
```

### 4. Install Dependencies

**Backend:**
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 5. Test Your Setup

```bash
# Run the setup test
python test_setup.py
```

### 6. Start FitFusion

**Option 1 - Automatic (Recommended):**
```bash
python start_dev.py
```

**Option 2 - Manual:**
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

## 🎉 You're Ready!

- **App**: http://localhost:3000
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/api/docs

## 🧪 Test It Out

1. **Check Health**: Visit http://localhost:8000/api/health
2. **Browse App**: Go to http://localhost:3000
3. **Generate Workout**: Navigate to `/generate` and create an AI workout
4. **Test Offline**: Turn off your internet - the app still works!

## 🐛 Having Issues?

### Common Problems:

**"Module not found":**
```bash
# Make sure virtual environment is activated
cd backend
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
```

**"Port already in use":**
```bash
# Kill processes on ports
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9
```

**"Database connection failed":**
- Double-check your Supabase URL and keys
- Make sure you ran the SQL schema
- Verify your project is active in Supabase

**"Gemini API error":**
- Check your API key is correct
- Verify you have quota in Google AI Studio
- Make sure the key has proper permissions

## 🚀 Next Steps

- Explore the different pages (Equipment, Generate, Progress)
- Try the offline functionality
- Check out the API documentation
- Customize the AI agents in `backend/src/agents/`

**Need more help?** Check the full README.md or create an issue!

---

**Happy coding! 💪🤖**
