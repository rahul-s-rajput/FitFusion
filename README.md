# 💪 FitFusion AI Workout App

A mobile-first PWA that uses AI agents (CrewAI + Gemini 2.5 Flash) to generate personalized workout programs with offline-first architecture.

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** and **npm/yarn**
- **Python 3.11+** and **pip**
- **Supabase account** (free tier works)
- **Google AI Studio account** for Gemini API

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd fitfusion

# Copy environment variables
cp .env.example .env
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
# Navigate to frontend (from project root)
cd frontend

# Install dependencies
npm install
# or
yarn install
```

### 4. Environment Configuration

Edit your `.env` file with your actual credentials:

```env
# Required - Get from Supabase Dashboard
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key

# Required - Get from Google AI Studio
GEMINI_API_KEY=your_gemini_api_key

# Required - Generate a secure secret
JWT_SECRET_KEY=your_super_secret_key_here

# Optional - For development
FRONTEND_URL=http://localhost:3000
```

### 5. Database Setup

1. **Create Supabase Project**: Go to [supabase.com](https://supabase.com) and create a new project
2. **Run SQL Schema**: Execute the SQL from `backend/supabase_schema.sql` in your Supabase SQL editor
3. **Enable RLS**: Row Level Security is automatically configured in the schema

### 6. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```
The API will be available at: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
The app will be available at: http://localhost:3000

## 🧪 Testing the Application

### 1. Check API Health

```bash
# Test backend health
curl http://localhost:8000/api/health

# View API documentation
open http://localhost:8000/api/docs
```

### 2. Test Frontend

1. Open http://localhost:3000
2. You should see the FitFusion dashboard
3. Try navigating to different pages:
   - Equipment Management: `/equipment`
   - Workout Generation: `/generate`
   - Progress Tracking: `/progress`

### 3. Test AI Workout Generation

1. Go to `/generate`
2. Follow the multi-step wizard
3. Generate a workout (requires valid Gemini API key)

### 4. Test Offline Functionality

1. Open Developer Tools → Network tab
2. Set to "Offline" mode
3. The app should continue working with cached data
4. Go back online to see sync in action

## 🏗️ Architecture Overview

```
FitFusion/
├── backend/                 # FastAPI Backend
│   ├── src/
│   │   ├── api/            # API endpoints
│   │   ├── agents/         # CrewAI agents
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   ├── middleware/     # CORS, auth, etc.
│   │   └── utils/          # Utilities
│   ├── main.py            # Application entry point
│   └── requirements.txt   # Python dependencies
│
├── frontend/               # Next.js Frontend
│   ├── src/
│   │   ├── app/           # Next.js 14 app router
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities & services
│   │   ├── store/         # Zustand state management
│   │   └── hooks/         # Custom React hooks
│   ├── public/            # Static assets & PWA
│   └── package.json       # Node dependencies
│
└── specs/                 # Documentation
    └── 001-create-a-mobile/
        ├── spec.md        # Feature specification
        ├── plan.md        # Implementation plan
        └── tasks.md       # Task breakdown
```

## 🔧 Key Features Implemented

### ✅ Backend (FastAPI)
- **AI Workout Generation** with Gemini 2.5 Flash
- **8 Specialized AI Agents** using CrewAI
- **Complete API Endpoints** for all features
- **Supabase Integration** with connection pooling
- **Security Middleware** (CORS, rate limiting, auth)
- **Error Handling & Logging** with Sentry integration

### ✅ Frontend (Next.js 14)
- **Offline-First Architecture** with Dexie.js
- **Real-time Sync** between local and remote data
- **PWA Functionality** with service workers
- **Responsive UI** with Tailwind CSS + shadcn/ui
- **State Management** with Zustand
- **Background Sync** for seamless offline experience

### ✅ Core Features
- **Equipment Management** - Add, edit, track your gear
- **AI Workout Generation** - Personalized workouts
- **Workout Execution** - Real-time workout tracking
- **Progress Analytics** - Track your fitness journey
- **Offline Support** - Works without internet

## 🐛 Troubleshooting

### Backend Issues

**"Module not found" errors:**
```bash
# Make sure you're in the backend directory and venv is activated
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Database connection errors:**
- Check your Supabase URL and keys in `.env`
- Ensure your Supabase project is active
- Run the database schema SQL

**Gemini API errors:**
- Verify your API key in `.env`
- Check your Google AI Studio quota
- Ensure the API key has proper permissions

### Frontend Issues

**Build errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API connection errors:**
- Ensure backend is running on port 8000
- Check CORS configuration
- Verify API endpoints in browser dev tools

### Common Issues

**Port already in use:**
```bash
# Backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Frontend (port 3000)
lsof -ti:3000 | xargs kill -9
```

## 📱 Mobile Testing

### PWA Installation
1. Open the app in Chrome/Edge on mobile
2. Look for "Add to Home Screen" prompt
3. Install as PWA for native-like experience

### Offline Testing
1. Enable airplane mode
2. App should continue working
3. Make changes offline
4. Go back online to see sync

## 🚀 Deployment

### Backend Deployment (Hugging Face Spaces)
```bash
# Create Dockerfile (already configured)
# Push to Hugging Face Spaces
# Set environment variables in Spaces settings
```

### Frontend Deployment (Vercel)
```bash
# Connect GitHub repo to Vercel
# Set environment variables
# Deploy automatically on push
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

---

**Need help?** Check the troubleshooting section or create an issue in the repository.

**Ready to get fit with AI?** 💪 Start your FitFusion journey today!
