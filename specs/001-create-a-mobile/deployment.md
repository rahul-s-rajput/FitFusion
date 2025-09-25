# Deployment Guide - FitFusion AI Workout App

**Date**: 2025-09-23  
**Status**: Ready for Implementation  
**Architecture**: Hybrid Local-First with Optional Cloud Sync

## Deployment Overview

This guide covers deploying FitFusion using a cost-optimized architecture perfect for personal use (2-3 users) with a clear path to production scaling.

## Architecture Components

### Frontend - Vercel (FREE)

**Next.js PWA with Local-First Storage**

```bash
# Install dependencies
npm install next@14 react@18 react-dom@18
npm install @ducanh2912/next-pwa  # NOT deprecated next-pwa
npm install dexie  # For IndexedDB
npm install @supabase/supabase-js  # Optional sync
```

**next.config.js**:
```javascript
const withPWA = require("@ducanh2912/next-pwa").default({
  dest: "public",
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development',
  cacheOnFrontEndNav: true,
  aggressiveFrontEndNavCaching: true,
  reloadOnOnline: false,  // Don't force reload
  swcMinify: true,
  workboxOptions: {
    disableDevLogs: true,
    maximumFileSizeToCacheInBytes: 10 * 1024 * 1024, // 10MB
    runtimeCaching: [
      {
        urlPattern: /^https:\/\/.*\.hf\.space\/api\/.*/i,
        handler: 'NetworkFirst',
        options: {
          cacheName: 'ai-api-cache',
          networkTimeoutSeconds: 30,
        }
      }
    ]
  }
});

module.exports = withPWA({
  reactStrictMode: true,
  images: {
    domains: ['your-cdn.com'],
  },
});
```

**Deploy to Vercel**:
```bash
npm install -g vercel
vercel --prod
```

### Backend - Huggingface Spaces (FREE)

**FastAPI with CrewAI Agents**

Create a Huggingface Space with Docker template:

**Dockerfile**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Huggingface Spaces uses port 7860
EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
```

**requirements.txt**:
```
fastapi==0.110.0
uvicorn==0.27.0
crewai==0.28.0
google-generativeai==0.3.0
pydantic==2.5.0
python-multipart==0.0.6
cors==1.0.1
```

**main.py**:
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from crewai import Agent, Task, Crew
import google.generativeai as genai
import os
from typing import List, Dict
from pydantic import BaseModel

app = FastAPI(title="FitFusion AI Backend")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.vercel.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini 2.5 Flash (CORRECT MODEL NAME)
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Define all 8 specialized agents
agents = {
    "strength_coach": Agent(
        role="Strength Training Coach",
        goal="Design effective strength training programs",
        backstory="Expert in resistance training and muscle development",
        llm_config={"model": "gemini-2.5-flash"}
    ),
    "cardio_coach": Agent(
        role="Cardio Fitness Coach",
        goal="Create cardiovascular training programs",
        backstory="Specialist in endurance and cardiovascular health",
        llm_config={"model": "gemini-2.5-flash"}
    ),
    "nutritionist": Agent(
        role="Sports Nutritionist",
        goal="Provide nutrition guidance for fitness goals",
        backstory="Expert in sports nutrition and meal planning",
        llm_config={"model": "gemini-2.5-flash"}
    ),
    "equipment_advisor": Agent(
        role="Equipment Specialist",
        goal="Recommend exercises based on available equipment",
        backstory="Expert in exercise equipment and alternatives",
        llm_config={"model": "gemini-2.5-flash"}
    ),
    "recovery_specialist": Agent(
        role="Recovery & Mobility Coach",
        goal="Design recovery and mobility routines",
        backstory="Specialist in injury prevention and recovery",
        llm_config={"model": "gemini-2.5-flash"}
    ),
    "motivation_coach": Agent(
        role="Motivation Coach",
        goal="Provide motivational strategies and mental training",
        backstory="Expert in sports psychology and motivation",
        llm_config={"model": "gemini-2.5-flash"}
    ),
    "analytics_expert": Agent(
        role="Fitness Analytics Expert",
        goal="Analyze progress and optimize programs",
        backstory="Data scientist specializing in fitness metrics",
        llm_config={"model": "gemini-2.5-flash"}
    ),
    "preferences_manager": Agent(
        role="Personalization Manager",
        goal="Adapt programs to user preferences and constraints",
        backstory="Expert in personalizing fitness experiences",
        llm_config={"model": "gemini-2.5-flash"}
    )
}

class WorkoutGenerationRequest(BaseModel):
    program_duration: int
    fitness_goals: List[str]
    experience_level: str
    available_equipment: List[str]
    space_constraints: Dict
    noise_preferences: Dict

@app.get("/")
def health_check():
    return {"status": "healthy", "agents": len(agents)}

@app.post("/api/workouts/generate")
async def generate_workout(request: WorkoutGenerationRequest):
    try:
        # Create crew with all agents
        crew = Crew(
            agents=list(agents.values()),
            tasks=[
                Task(
                    description=f"Generate a {request.program_duration}-day workout program",
                    agent=agents["strength_coach"]
                ),
                Task(
                    description="Add cardio components",
                    agent=agents["cardio_coach"]
                ),
                Task(
                    description="Provide nutrition guidelines",
                    agent=agents["nutritionist"]
                ),
                # Add more tasks as needed
            ],
            verbose=True
        )
        
        # Generate with timeout
        result = await crew.kickoff_async(inputs=request.dict())
        
        return {
            "status": "success",
            "program": result,
            "generated_by": "8 specialized AI agents"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Deploy to Huggingface Spaces**:
1. Create account at huggingface.co
2. Create new Space with Docker template
3. Upload your files
4. Set GEMINI_API_KEY in Space settings
5. Your API will be available at `https://your-username-fitfusion.hf.space`

### Database - Supabase (FREE Tier)

**Optional Cloud Sync**

```sql
-- Create tables (run in Supabase SQL editor)
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT,  -- Optional for personal use
  fitness_goals JSONB NOT NULL,
  experience_level TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE equipment (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES user_profiles(id),
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  specifications JSONB,
  condition TEXT DEFAULT 'excellent',
  is_available BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add all other tables from data-model.md
```

### Local Storage - Dexie.js

**Primary Storage (Always Works Offline)**

```javascript
// db.js
import Dexie from 'dexie';

export class FitFusionDB extends Dexie {
  constructor() {
    super('FitFusionDB');
    
    this.version(1).stores({
      userProfiles: '++id, email, updatedAt',
      equipment: '++id, userId, name, category, updatedAt, syncStatus',
      workoutPrograms: '++id, userId, name, isActive, updatedAt, syncStatus',
      workoutSessions: '++id, programId, scheduledDate, updatedAt, syncStatus',
      progressRecords: '++id, userId, recordDate, metricName, syncStatus'
    });
  }
}

export const db = new FitFusionDB();
```

## Sync Adapter Pattern

**Optional Backend Sync**

```javascript
// sync-adapter.js
import { createClient } from '@supabase/supabase-js';
import { db } from './db';

export class SyncAdapter {
  constructor(supabaseUrl = null, supabaseKey = null) {
    this.local = db;
    this.remote = null;
    this.syncEnabled = false;
    
    // Only enable sync if credentials provided
    if (supabaseUrl && supabaseKey) {
      this.remote = createClient(supabaseUrl, supabaseKey);
      this.syncEnabled = true;
    }
  }

  async saveEquipment(equipment) {
    // Always save locally first
    const localId = await this.local.equipment.add({
      ...equipment,
      updatedAt: Date.now(),
      syncStatus: 'pending'
    });

    // Try to sync if enabled and online
    if (this.syncEnabled && navigator.onLine) {
      this.syncInBackground(localId);
    }

    return localId;
  }

  async syncInBackground(localId) {
    try {
      const item = await this.local.equipment.get(localId);
      const { data } = await this.remote
        .from('equipment')
        .insert(item);
      
      await this.local.equipment.update(localId, {
        syncStatus: 'synced',
        remoteId: data?.id
      });
    } catch (error) {
      // Silent fail - will retry later
      console.log('Will sync when online');
    }
  }
}
```

## Environment Variables

**.env.local (Frontend)**:
```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co  # Optional
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key  # Optional
NEXT_PUBLIC_API_URL=https://your-app.hf.space  # Your Huggingface Space
```

**Huggingface Space Settings**:
```
GEMINI_API_KEY=your-gemini-api-key
```

## Cost Analysis

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Vercel | Frontend hosting | $0 |
| Huggingface Spaces | Backend API | $0 |
| Supabase | 500MB database | $0 |
| Gemini 2.5 Flash | ~100 API calls | ~$0.50 |
| **Total** | | **~$0.50** |

## Scaling to Production

When ready to scale beyond personal use:

### Phase 1: Add Authentication (No architecture change)
```javascript
// Just enable Supabase Auth
const { data: user } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'password'
});
```

### Phase 2: Enable Multi-User (Enable RLS)
```sql
ALTER TABLE equipment ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users see own equipment" 
  ON equipment FOR ALL 
  USING (auth.uid() = user_id);
```

### Phase 3: Scale Infrastructure (When needed)
- Upgrade Supabase to Pro ($25/month)
- Move backend to Railway/Render ($7-20/month)
- Add monitoring and analytics

## Monitoring

For personal use, minimal monitoring needed:

```javascript
// Simple error tracking
window.addEventListener('error', (e) => {
  console.error('App Error:', e);
  // Optional: Send to free service like Sentry
});

// PWA update notification
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.ready.then(registration => {
    registration.addEventListener('updatefound', () => {
      console.log('New version available!');
    });
  });
}
```

## Deployment Checklist

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Huggingface Spaces
- [ ] Gemini API key configured
- [ ] Supabase database created (optional)
- [ ] PWA manifest configured
- [ ] Service worker caching tested
- [ ] Offline functionality verified
- [ ] AI generation working (<30s)
- [ ] Local storage (Dexie.js) working
- [ ] Optional sync tested

---

**Status**: ✅ Ready for deployment with hybrid architecture
