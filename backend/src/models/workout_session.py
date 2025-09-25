"""
WorkoutSession model for FitFusion AI Workout App.
Represents individual workout instances with exercise sequences and timing.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator
from enum import Enum


class WorkoutType(str, Enum):
    """Types of workout sessions"""
    STRENGTH = "strength"
    CARDIO = "cardio"
    REST = "rest"
    FLEXIBILITY = "flexibility"
    MIXED = "mixed"


class CompletionStatus(str, Enum):
    """Workout session completion status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class ExercisePhase(str, Enum):
    """Exercise phases within a workout"""
    WARMUP = "warmup"
    MAIN = "main"
    COOLDOWN = "cooldown"


class WorkoutExercise(BaseModel):
    """Individual exercise instance within a workout session"""
    id: UUID = Field(default_factory=uuid4, description="Unique exercise instance identifier")
    exercise_id: UUID = Field(..., description="Reference to Exercise entity")
    sequence_order: int = Field(..., ge=1, description="Order within workout")
    exercise_phase: ExercisePhase = Field(..., description="Phase of workout")
    
    # Target parameters (planned)
    target_sets: Optional[int] = Field(None, ge=1, le=20, description="Planned sets")
    target_reps: Optional[int] = Field(None, ge=1, le=1000, description="Planned repetitions")
    target_duration: Optional[int] = Field(None, ge=1, description="Planned seconds")
    target_weight: Optional[float] = Field(None, ge=0, description="Planned weight in kg")
    rest_duration: int = Field(60, ge=0, le=600, description="Rest seconds between sets")
    
    # Actual performance (completed)
    completed_sets: Optional[int] = Field(None, ge=0, description="Actually completed sets")
    actual_reps: Optional[List[int]] = Field(None, description="Actual reps per set")
    actual_duration: Optional[int] = Field(None, ge=0, description="Actual duration in seconds")
    actual_weight: Optional[float] = Field(None, ge=0, description="Actual weight used")
    performance_notes: Optional[str] = Field(None, max_length=500, description="User notes")
    completion_status: CompletionStatus = Field(CompletionStatus.SCHEDULED, description="Exercise completion status")
    
    @validator('target_reps', 'target_duration')
    def validate_duration_or_reps(cls, v, values):
        """Either target_reps or target_duration should be set, not both"""
        if 'target_reps' in values and values['target_reps'] is not None and v is not None:
            if values.get('target_reps') and v:
                raise ValueError('Cannot set both target_reps and target_duration')
        return v


class PerformanceData(BaseModel):
    """Performance data for completed workout"""
    total_duration: int = Field(..., ge=0, description="Total workout duration in seconds")
    exercises_completed: int = Field(..., ge=0, description="Number of exercises completed")
    exercises_skipped: int = Field(0, ge=0, description="Number of exercises skipped")
    average_heart_rate: Optional[int] = Field(None, ge=40, le=220, description="Average heart rate if tracked")
    calories_burned: Optional[int] = Field(None, ge=0, description="Estimated calories burned")
    perceived_exertion: Optional[int] = Field(None, ge=1, le=10, description="RPE scale 1-10")
    notes: Optional[str] = Field(None, max_length=1000, description="Overall workout notes")


class WorkoutSession(BaseModel):
    """Individual workout session with exercise sequences and timing"""
    id: UUID = Field(default_factory=uuid4, description="Unique session identifier")
    program_id: UUID = Field(..., description="Parent program reference")
    user_id: UUID = Field(..., description="Session owner")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation date")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last modification")
    scheduled_date: date = Field(..., description="Intended workout date")
    started_at: Optional[datetime] = Field(None, description="Actual start time")
    completed_at: Optional[datetime] = Field(None, description="Actual completion time")
    
    # Session details
    day_number: int = Field(..., ge=1, le=90, description="Day within program (1-based)")
    workout_type: WorkoutType = Field(..., description="Type of workout")
    estimated_duration: int = Field(..., ge=5, le=180, description="Expected minutes to complete")
    
    # Exercise sequences
    warmup_exercises: List[WorkoutExercise] = Field(default_factory=list, description="Pre-workout exercises")
    main_exercises: List[WorkoutExercise] = Field(..., min_items=1, description="Primary workout exercises")
    cooldown_exercises: List[WorkoutExercise] = Field(default_factory=list, description="Post-workout exercises")
    
    # Status and performance
    completion_status: CompletionStatus = Field(CompletionStatus.SCHEDULED, description="Session completion status")
    performance_data: Optional[PerformanceData] = Field(None, description="Actual performance data")
    
    # Sync metadata
    sync_status: str = Field("pending", description="Sync status for offline/online coordination")
    last_synced_at: Optional[datetime] = Field(None, description="Last successful sync timestamp")
    
    @validator('scheduled_date')
    def validate_scheduled_date(cls, v):
        """Scheduled date cannot be too far in the past for new sessions"""
        # Allow some flexibility for retroactive logging
        return v
    
    @validator('completed_at')
    def validate_completion_time(cls, v, values):
        """Completion time must be after start time"""
        if v and 'started_at' in values and values['started_at']:
            if v <= values['started_at']:
                raise ValueError('Completion time must be after start time')
        return v
    
    @validator('completion_status')
    def validate_status_transitions(cls, v, values):
        """Validate completion status transitions"""
        # This would be more complex in a real system with state machine
        valid_transitions = {
            CompletionStatus.SCHEDULED: [CompletionStatus.IN_PROGRESS, CompletionStatus.SKIPPED],
            CompletionStatus.IN_PROGRESS: [CompletionStatus.COMPLETED, CompletionStatus.SKIPPED],
            CompletionStatus.COMPLETED: [],  # Final state
            CompletionStatus.SKIPPED: []     # Final state
        }
        return v
    
    @validator('performance_data')
    def validate_performance_data(cls, v, values):
        """Performance data required when status is completed"""
        if values.get('completion_status') == CompletionStatus.COMPLETED and v is None:
            raise ValueError('Performance data required when workout is completed')
        return v
    
    def get_all_exercises(self) -> List[WorkoutExercise]:
        """Get all exercises in the session in order"""
        return self.warmup_exercises + self.main_exercises + self.cooldown_exercises
    
    def get_total_exercises(self) -> int:
        """Get total number of exercises in the session"""
        return len(self.warmup_exercises) + len(self.main_exercises) + len(self.cooldown_exercises)
    
    def calculate_completion_percentage(self) -> float:
        """Calculate percentage of exercises completed"""
        all_exercises = self.get_all_exercises()
        if not all_exercises:
            return 0.0
        
        completed = sum(1 for ex in all_exercises if ex.completion_status == CompletionStatus.COMPLETED)
        return completed / len(all_exercises)
    
    def start_session(self) -> None:
        """Mark session as started"""
        self.completion_status = CompletionStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def complete_session(self, performance_data: PerformanceData) -> None:
        """Mark session as completed with performance data"""
        self.completion_status = CompletionStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.performance_data = performance_data
        self.updated_at = datetime.utcnow()
    
    def skip_session(self, reason: Optional[str] = None) -> None:
        """Mark session as skipped"""
        self.completion_status = CompletionStatus.SKIPPED
        self.updated_at = datetime.utcnow()
        if reason and self.performance_data:
            self.performance_data.notes = reason


class WorkoutSessionCreate(BaseModel):
    """Schema for creating a new workout session"""
    program_id: UUID
    user_id: UUID
    scheduled_date: date
    day_number: int = Field(..., ge=1, le=90)
    workout_type: WorkoutType
    estimated_duration: int = Field(..., ge=5, le=180)
    warmup_exercises: List[WorkoutExercise] = Field(default_factory=list)
    main_exercises: List[WorkoutExercise] = Field(..., min_items=1)
    cooldown_exercises: List[WorkoutExercise] = Field(default_factory=list)


class WorkoutSessionUpdate(BaseModel):
    """Schema for updating a workout session"""
    scheduled_date: Optional[date] = None
    workout_type: Optional[WorkoutType] = None
    estimated_duration: Optional[int] = Field(None, ge=5, le=180)
    warmup_exercises: Optional[List[WorkoutExercise]] = None
    main_exercises: Optional[List[WorkoutExercise]] = None
    cooldown_exercises: Optional[List[WorkoutExercise]] = None
    completion_status: Optional[CompletionStatus] = None
    performance_data: Optional[PerformanceData] = None


class WorkoutSessionResponse(BaseModel):
    """Schema for workout session API responses"""
    id: UUID
    program_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    scheduled_date: date
    day_number: int
    workout_type: WorkoutType
    estimated_duration: int
    completion_status: CompletionStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    total_exercises: int
    completion_percentage: float
    performance_data: Optional[PerformanceData]
    
    @classmethod
    def from_workout_session(cls, session: WorkoutSession) -> "WorkoutSessionResponse":
        """Create response from WorkoutSession model"""
        return cls(
            id=session.id,
            program_id=session.program_id,
            user_id=session.user_id,
            created_at=session.created_at,
            updated_at=session.updated_at,
            scheduled_date=session.scheduled_date,
            day_number=session.day_number,
            workout_type=session.workout_type,
            estimated_duration=session.estimated_duration,
            completion_status=session.completion_status,
            started_at=session.started_at,
            completed_at=session.completed_at,
            total_exercises=session.get_total_exercises(),
            completion_percentage=session.calculate_completion_percentage(),
            performance_data=session.performance_data
        )
