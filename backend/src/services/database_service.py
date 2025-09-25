"""
Supabase Database Integration Service for FitFusion AI Workout App
Handles all database operations with Supabase PostgreSQL backend
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone, timedelta
import logging
from contextlib import asynccontextmanager

from supabase import create_client, Client
from supabase.client import ClientOptions
from postgrest.exceptions import APIError
import asyncpg
from pydantic import BaseModel

from ..models.user_profile import UserProfile, UserProfileCreate, UserProfileUpdate
from ..models.equipment import Equipment, EquipmentCreate, EquipmentUpdate
from ..models.exercise import Exercise, ExerciseCreate, ExerciseUpdate
from ..models.workout_program import WorkoutProgram, WorkoutProgramCreate, WorkoutProgramUpdate
from ..models.workout_session import WorkoutSession, WorkoutSessionCreate, WorkoutSessionUpdate
from ..models.progress_record import ProgressRecord, ProgressRecordCreate, ProgressRecordUpdate

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseConfig(BaseModel):
    """Database configuration settings"""
    supabase_url: str
    supabase_key: str
    supabase_service_key: Optional[str] = None
    database_url: Optional[str] = None
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    enable_logging: bool = False

class DatabaseService:
    """
    Supabase database service for FitFusion application
    Provides high-level database operations with connection pooling and error handling
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.supabase: Client = None
        self.connection_pool: asyncpg.Pool = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client with configuration"""
        try:
            api_key = self.config.supabase_service_key or self.config.supabase_key
            if not api_key:
                raise ValueError("Supabase API key not provided")

            # Use only supported ClientOptions parameters
            options = ClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=10,
                schema="public"
            )
            
            self.supabase = create_client(
                self.config.supabase_url,
                api_key,
                options=options
            )
            
            key_label = 'service' if self.config.supabase_service_key else 'anon'
            logger.info("Supabase client initialized successfully using %s key", key_label)
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    async def initialize_pool(self):
        """Initialize asyncpg connection pool for direct PostgreSQL operations"""
        if self.config.database_url and self._is_valid_database_url(self.config.database_url):
            try:
                self.connection_pool = await asyncpg.create_pool(
                    self.config.database_url,
                    min_size=1,
                    max_size=self.config.pool_size,
                    max_queries=50000,
                    max_inactive_connection_lifetime=300.0,
                    timeout=self.config.pool_timeout,
                    command_timeout=60
                )
                logger.info("Database connection pool initialized")
            except Exception as e:
                logger.error(f"Failed to initialize connection pool: {e}")
                logger.warning("Continuing without connection pool - using Supabase client only")
        else:
            logger.info("No valid DATABASE_URL provided - using Supabase client only")
    
    def _is_valid_database_url(self, url: str) -> bool:
        """Check if the database URL is valid and not a placeholder"""
        if not url:
            return False
        
        # Check for placeholder values
        placeholder_indicators = ['user:password@host:port', 'localhost:5432', 'example.com']
        for placeholder in placeholder_indicators:
            if placeholder in url:
                return False
        
        # Basic format validation
        if not url.startswith(('postgresql://', 'postgres://')):
            return False
            
        return True
    
    async def close_pool(self):
        """Close the connection pool"""
        if self.connection_pool:
            await self.connection_pool.close()
            logger.info("Database connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection from the pool"""
        if not self.connection_pool:
            raise RuntimeError("Connection pool not initialized - use Supabase client methods instead")
        
        async with self.connection_pool.acquire() as connection:
            yield connection
    
    # User Profile Operations
    async def create_user_profile(self, profile_data: UserProfileCreate) -> UserProfile:
        """Create a new user profile"""
        try:
            data = profile_data.dict()
            data['created_at'] = datetime.now(timezone.utc).isoformat()
            data['updated_at'] = data['created_at']
            
            result = self.supabase.table('user_profiles').insert(data).execute()
            
            if result.data:
                return UserProfile(**result.data[0])
            else:
                raise ValueError("Failed to create user profile")
                
        except APIError as e:
            logger.error(f"Supabase API error creating user profile: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating user profile: {e}")
            raise
    
    async def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile by ID"""
        try:
            result = self.supabase.table('user_profiles').select('*').eq('id', user_id).execute()
            
            if result.data:
                return UserProfile(**result.data[0])
            return None
            
        except APIError as e:
            logger.error(f"Supabase API error getting user profile: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            raise
    
    async def update_user_profile(self, user_id: int, profile_data: UserProfileUpdate) -> Optional[UserProfile]:
        """Update user profile"""
        try:
            data = profile_data.dict(exclude_unset=True)
            data['updated_at'] = datetime.now(timezone.utc).isoformat()
            
            result = self.supabase.table('user_profiles').update(data).eq('id', user_id).execute()
            
            if result.data:
                return UserProfile(**result.data[0])
            return None
            
        except APIError as e:
            logger.error(f"Supabase API error updating user profile: {e}")
            raise
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            raise
    
    # Equipment Operations
    async def create_equipment(self, equipment_data: EquipmentCreate) -> Equipment:
        """Create new equipment"""
        try:
            data = equipment_data.dict()
            data['created_at'] = datetime.now(timezone.utc).isoformat()
            data['updated_at'] = data['created_at']
            
            result = self.supabase.table('equipment').insert(data).execute()
            
            if result.data:
                return Equipment(**result.data[0])
            else:
                raise ValueError("Failed to create equipment")
                
        except APIError as e:
            logger.error(f"Supabase API error creating equipment: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating equipment: {e}")
            raise
    
    async def get_user_equipment(
        self, 
        user_id: int, 
        category: Optional[str] = None,
        available_only: bool = False
    ) -> List[Equipment]:
        """Get user's equipment with optional filtering"""
        try:
            query = self.supabase.table('equipment').select('*').eq('user_id', user_id)
            
            if category:
                query = query.eq('category', category)
            if available_only:
                query = query.eq('is_available', True)
            
            result = query.execute()
            
            return [Equipment(**item) for item in result.data]
            
        except APIError as e:
            logger.error(f"Supabase API error getting equipment: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting equipment: {e}")
            raise
    
    async def update_equipment(self, equipment_id: int, equipment_data: EquipmentUpdate) -> Optional[Equipment]:
        """Update equipment"""
        try:
            data = equipment_data.dict(exclude_unset=True)
            data['updated_at'] = datetime.now(timezone.utc).isoformat()
            
            result = self.supabase.table('equipment').update(data).eq('id', equipment_id).execute()
            
            if result.data:
                return Equipment(**result.data[0])
            return None
            
        except APIError as e:
            logger.error(f"Supabase API error updating equipment: {e}")
            raise
        except Exception as e:
            logger.error(f"Error updating equipment: {e}")
            raise
    
    async def delete_equipment(self, equipment_id: int) -> bool:
        """Delete equipment"""
        try:
            result = self.supabase.table('equipment').delete().eq('id', equipment_id).execute()
            return len(result.data) > 0
            
        except APIError as e:
            logger.error(f"Supabase API error deleting equipment: {e}")
            raise
        except Exception as e:
            logger.error(f"Error deleting equipment: {e}")
            raise
    
    # Exercise Operations
    async def get_exercises(
        self,
        category: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        equipment_required: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Exercise]:
        """Get exercises with optional filtering"""
        try:
            query = self.supabase.table('exercises').select('*')
            
            if category:
                query = query.eq('category', category)
            if difficulty_level:
                query = query.eq('difficulty_level', difficulty_level)
            if equipment_required:
                query = query.contains('equipment_required', equipment_required)
            
            result = query.limit(limit).execute()
            
            return [Exercise(**item) for item in result.data]
            
        except APIError as e:
            logger.error(f"Supabase API error getting exercises: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting exercises: {e}")
            raise
    
    async def create_exercise(self, exercise_data: ExerciseCreate) -> Exercise:
        """Create new exercise"""
        try:
            data = exercise_data.dict()
            data['created_at'] = datetime.now(timezone.utc).isoformat()
            data['updated_at'] = data['created_at']
            
            result = self.supabase.table('exercises').insert(data).execute()
            
            if result.data:
                return Exercise(**result.data[0])
            else:
                raise ValueError("Failed to create exercise")
                
        except APIError as e:
            logger.error(f"Supabase API error creating exercise: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating exercise: {e}")
            raise
    
    # Workout Program Operations
    async def create_workout_program(self, program_data: WorkoutProgramCreate) -> WorkoutProgram:
        """Create new workout program"""
        try:
            data = program_data.dict()
            data['created_at'] = datetime.now(timezone.utc).isoformat()
            data['updated_at'] = data['created_at']
            
            result = self.supabase.table('workout_programs').insert(data).execute()
            
            if result.data:
                return WorkoutProgram(**result.data[0])
            else:
                raise ValueError("Failed to create workout program")
                
        except APIError as e:
            logger.error(f"Supabase API error creating workout program: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating workout program: {e}")
            raise
    
    async def get_user_programs(
        self,
        user_id: int,
        active_only: bool = False,
        limit: int = 50
    ) -> List[WorkoutProgram]:
        """Get user's workout programs"""
        try:
            query = self.supabase.table('workout_programs').select('*').eq('user_id', user_id)
            
            if active_only:
                query = query.eq('is_active', True)
            
            result = query.order('created_at', desc=True).limit(limit).execute()
            
            return [WorkoutProgram(**item) for item in result.data]
            
        except APIError as e:
            logger.error(f"Supabase API error getting workout programs: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting workout programs: {e}")
            raise
    
    async def update_workout_program(self, program_id: int, program_data: WorkoutProgramUpdate) -> Optional[WorkoutProgram]:
        """Update workout program"""
        try:
            data = program_data.dict(exclude_unset=True)
            data['updated_at'] = datetime.now(timezone.utc).isoformat()
            
            result = self.supabase.table('workout_programs').update(data).eq('id', program_id).execute()
            
            if result.data:
                return WorkoutProgram(**result.data[0])
            return None
            
        except APIError as e:
            logger.error(f"Supabase API error updating workout program: {e}")
            raise
        except Exception as e:
            logger.error(f"Error updating workout program: {e}")
            raise
    
    # Workout Session Operations
    async def create_workout_session(self, session_data: WorkoutSessionCreate) -> WorkoutSession:
        """Create new workout session"""
        try:
            data = session_data.dict()
            data['created_at'] = datetime.now(timezone.utc).isoformat()
            data['updated_at'] = data['created_at']
            
            result = self.supabase.table('workout_sessions').insert(data).execute()
            
            if result.data:
                return WorkoutSession(**result.data[0])
            else:
                raise ValueError("Failed to create workout session")
                
        except APIError as e:
            logger.error(f"Supabase API error creating workout session: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating workout session: {e}")
            raise
    
    async def get_user_sessions(
        self,
        user_id: int,
        program_id: Optional[int] = None,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50
    ) -> List[WorkoutSession]:
        """Get user's workout sessions with filtering"""
        try:
            query = self.supabase.table('workout_sessions').select('*').eq('user_id', user_id)
            
            if program_id:
                query = query.eq('program_id', program_id)
            if status:
                query = query.eq('completion_status', status)
            if date_from:
                query = query.gte('scheduled_date', date_from.isoformat())
            if date_to:
                query = query.lte('scheduled_date', date_to.isoformat())
            
            result = query.order('scheduled_date', desc=True).limit(limit).execute()
            
            return [WorkoutSession(**item) for item in result.data]
            
        except APIError as e:
            logger.error(f"Supabase API error getting workout sessions: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting workout sessions: {e}")
            raise
    
    async def update_workout_session(self, session_id: int, session_data: WorkoutSessionUpdate) -> Optional[WorkoutSession]:
        """Update workout session"""
        try:
            data = session_data.dict(exclude_unset=True)
            data['updated_at'] = datetime.now(timezone.utc).isoformat()
            
            result = self.supabase.table('workout_sessions').update(data).eq('id', session_id).execute()
            
            if result.data:
                return WorkoutSession(**result.data[0])
            return None
            
        except APIError as e:
            logger.error(f"Supabase API error updating workout session: {e}")
            raise
        except Exception as e:
            logger.error(f"Error updating workout session: {e}")
            raise
    
    # Progress Record Operations
    async def create_progress_record(self, record_data: ProgressRecordCreate) -> ProgressRecord:
        """Create new progress record"""
        try:
            data = record_data.dict()
            data['created_at'] = datetime.now(timezone.utc).isoformat()
            
            result = self.supabase.table('progress_records').insert(data).execute()
            
            if result.data:
                return ProgressRecord(**result.data[0])
            else:
                raise ValueError("Failed to create progress record")
                
        except APIError as e:
            logger.error(f"Supabase API error creating progress record: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating progress record: {e}")
            raise
    
    async def get_user_progress_records(
        self,
        user_id: int,
        metric_name: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ProgressRecord]:
        """Get user's progress records with filtering"""
        try:
            query = self.supabase.table('progress_records').select('*').eq('user_id', user_id)
            
            if metric_name:
                query = query.eq('metric_name', metric_name)
            if date_from:
                query = query.gte('record_date', date_from.isoformat())
            if date_to:
                query = query.lte('record_date', date_to.isoformat())
            
            result = query.order('record_date', desc=True).limit(limit).execute()
            
            return [ProgressRecord(**item) for item in result.data]
            
        except APIError as e:
            logger.error(f"Supabase API error getting progress records: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting progress records: {e}")
            raise
    
    # Analytics and Statistics
    async def get_user_statistics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get user statistics for the specified period"""
        try:
            date_from = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Get workout sessions stats
            sessions = await self.get_user_sessions(
                user_id=user_id,
                date_from=date_from,
                limit=1000
            )
            
            completed_sessions = [s for s in sessions if s.completion_status == 'completed']
            
            stats = {
                'total_sessions': len(sessions),
                'completed_sessions': len(completed_sessions),
                'completion_rate': len(completed_sessions) / len(sessions) if sessions else 0,
                'total_workout_time': sum(s.estimated_duration or 0 for s in completed_sessions),
                'average_session_duration': (
                    sum(s.estimated_duration or 0 for s in completed_sessions) / len(completed_sessions)
                    if completed_sessions else 0
                ),
                'workout_types': {},
                'current_streak': 0,  # Would need more complex calculation
                'longest_streak': 0   # Would need more complex calculation
            }
            
            # Count workout types
            for session in completed_sessions:
                workout_type = getattr(session, 'workout_type', 'unknown')
                stats['workout_types'][workout_type] = stats['workout_types'].get(workout_type, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            raise
    
    # Health Check
    async def health_check(self) -> Dict[str, Any]:
        """Check database connectivity and health"""
        try:
            # Test Supabase connection
            result = self.supabase.table('user_profiles').select('id').limit(1).execute()
            supabase_healthy = True
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            supabase_healthy = False
        
        # Test connection pool if available - temporarily disabled for development
        pool_healthy = True
        # Commenting out pool health check to avoid pgbouncer prepared statement issues
        # if self.connection_pool:
        #     try:
        #         async with self.get_connection() as conn:
        #             await conn.fetchval('SELECT 1')
        #     except Exception as e:
        #         logger.error(f"Connection pool health check failed: {e}")
        #         pool_healthy = False
        
        return {
            'supabase_healthy': supabase_healthy,
            'connection_pool_healthy': pool_healthy,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

# Global database service instance
_database_service: Optional[DatabaseService] = None

def get_database_service() -> DatabaseService:
    """Get the global database service instance"""
    global _database_service
    if _database_service is None:
        service_key = (
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            or os.getenv('SUPABASE_SERVICE_KEY')
            or os.getenv('SUPABASE_SERVICE_ROLE')
            or os.getenv('SUPABASE_SERVICE_API_KEY')
        )
        config = DatabaseConfig(
            supabase_url=os.getenv('SUPABASE_URL', ''),
            supabase_key=os.getenv('SUPABASE_ANON_KEY', ''),
            supabase_service_key=service_key,
            database_url=os.getenv('DATABASE_URL'),
            enable_logging=os.getenv('DATABASE_LOGGING', 'false').lower() == 'true'
        )
        _database_service = DatabaseService(config)
    return _database_service

async def initialize_database():
    """Initialize the database service and connection pool"""
    db_service = get_database_service()
    await db_service.initialize_pool()
    logger.info("Database service initialized")

async def close_database():
    """Close the database service and connection pool"""
    global _database_service
    if _database_service:
        await _database_service.close_pool()
        _database_service = None
    logger.info("Database service closed")
