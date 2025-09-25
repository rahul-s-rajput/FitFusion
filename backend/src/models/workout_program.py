"""
WorkoutProgram model for FitFusion AI Workout App.
Represents complete multi-day fitness programs with daily schedules, progression logic, and AI-generated customization.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator
from enum import Enum


class ProgramType(str, Enum):
    """Types of workout programs"""
    STRENGTH_BUILDING = "strength_building"
    WEIGHT_LOSS = "weight_loss"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"
    GENERAL_FITNESS = "general_fitness"
    REHABILITATION = "rehabilitation"
    SPORT_SPECIFIC = "sport_specific"
    HYBRID = "hybrid"


class DifficultyLevel(str, Enum):
    """Program difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ProgramStatus(str, Enum):
    """Program status states"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class DaySchedule(BaseModel):
    """Schedule for a single day in the program"""
    day_number: int = Field(..., ge=1, description="Day number in the program")
    day_name: Optional[str] = Field(None, description="Optional day name (e.g., 'Upper Body')")
    workout_type: str = Field(..., description="Type of workout for this day")
    is_rest_day: bool = Field(False, description="Whether this is a rest day")
    
    # Exercise details
    warmup_exercises: List[Dict[str, Any]] = Field(default_factory=list, description="Warmup exercises")
    main_exercises: List[Dict[str, Any]] = Field(default_factory=list, description="Main workout exercises")
    cooldown_exercises: List[Dict[str, Any]] = Field(default_factory=list, description="Cooldown exercises")
    
    # Timing
    estimated_duration: int = Field(..., ge=10, le=180, description="Estimated duration in minutes")
    warmup_duration: Optional[int] = Field(None, description="Warmup duration in minutes")
    main_duration: Optional[int] = Field(None, description="Main workout duration in minutes")
    cooldown_duration: Optional[int] = Field(None, description="Cooldown duration in minutes")
    
    # Progression and notes
    intensity_level: float = Field(5.0, ge=1.0, le=10.0, description="Intensity level (1-10)")
    focus_areas: List[str] = Field(default_factory=list, description="Focus areas for this day")
    notes: Optional[str] = Field(None, description="Special notes for this day")
    equipment_needed: List[str] = Field(default_factory=list, description="Equipment needed for this day")


class ProgressionRule(BaseModel):
    """Rules for program progression"""
    rule_type: str = Field(..., description="Type of progression rule")
    trigger_condition: str = Field(..., description="Condition that triggers progression")
    adjustment: Dict[str, Any] = Field(..., description="How to adjust the program")
    description: str = Field(..., description="Human-readable description of the rule")


class AIGenerationMetadata(BaseModel):
    """Metadata about AI generation process"""
    generated_by: str = Field(..., description="AI system that generated the program")
    generation_version: str = Field(..., description="Version of the generation system")
    generation_timestamp: datetime = Field(..., description="When the program was generated")
    agents_involved: List[str] = Field(default_factory=list, description="AI agents that contributed")
    generation_parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters used for generation")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI confidence in the program")
    customization_level: str = Field("standard", description="Level of customization applied")


class WorkoutProgram(BaseModel):
    """Main workout program model"""
    id: UUID = Field(default_factory=uuid4, description="Unique program identifier")
    user_id: Optional[UUID] = Field(None, description="Owner user ID")
    
    # Basic information
    name: str = Field(..., min_length=1, max_length=100, description="Program name")
    description: Optional[str] = Field(None, max_length=500, description="Program description")
    program_type: ProgramType = Field(..., description="Type of program")
    difficulty_level: DifficultyLevel = Field(..., description="Overall difficulty level")
    
    # Duration and scheduling
    duration_days: int = Field(..., ge=1, le=365, description="Total program duration in days")
    sessions_per_week: int = Field(..., ge=1, le=7, description="Number of workout sessions per week")
    estimated_session_duration: int = Field(45, ge=15, le=180, description="Average session duration in minutes")
    
    # Program structure
    daily_schedules: Dict[str, DaySchedule] = Field(..., description="Daily workout schedules")
    rest_days: List[int] = Field(default_factory=list, description="Scheduled rest days")
    progression_rules: List[ProgressionRule] = Field(default_factory=list, description="Progression rules")
    
    # Goals and targeting
    fitness_goals: List[str] = Field(default_factory=list, description="Fitness goals addressed")
    target_muscle_groups: List[str] = Field(default_factory=list, description="Primary muscle groups targeted")
    equipment_required: List[str] = Field(default_factory=list, description="Equipment required for the program")
    
    # Status and progress
    status: ProgramStatus = Field(ProgramStatus.DRAFT, description="Current program status")
    is_active: bool = Field(False, description="Whether this program is currently active")
    completion_percentage: float = Field(0.0, ge=0.0, le=100.0, description="Completion percentage")
    
    # Dates
    start_date: Optional[date] = Field(None, description="Program start date")
    end_date: Optional[date] = Field(None, description="Program end date")
    last_workout_date: Optional[date] = Field(None, description="Date of last completed workout")
    
    # AI and customization
    ai_generation_metadata: Optional[AIGenerationMetadata] = Field(None, description="AI generation metadata")
    customizations: Dict[str, Any] = Field(default_factory=dict, description="User customizations")
    
    # Performance tracking
    total_sessions_completed: int = Field(0, ge=0, description="Total sessions completed")
    total_sessions_planned: int = Field(0, ge=0, description="Total sessions planned")
    average_session_rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Average user rating")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
        schema_extra = {
            "example": {
                "name": "28-Day Strength & Endurance Program",
                "description": "AI-generated program combining strength training and cardiovascular endurance",
                "program_type": "hybrid",
                "difficulty_level": "intermediate",
                "duration_days": 28,
                "sessions_per_week": 4,
                "estimated_session_duration": 45,
                "daily_schedules": {
                    "day_1": {
                        "day_number": 1,
                        "day_name": "Upper Body Strength",
                        "workout_type": "strength",
                        "is_rest_day": False,
                        "main_exercises": [
                            {
                                "exercise_id": "push_ups",
                                "sets": 3,
                                "reps": 12,
                                "rest_seconds": 60
                            }
                        ],
                        "estimated_duration": 45,
                        "intensity_level": 7.0,
                        "focus_areas": ["chest", "shoulders", "triceps"]
                    }
                },
                "fitness_goals": ["strength", "endurance"],
                "equipment_required": ["dumbbells", "resistance_bands"],
                "status": "active",
                "is_active": True
            }
        }
    
    @validator('name')
    def validate_name(cls, v):
        """Validate program name"""
        if not v or v.strip() == "":
            raise ValueError('Program name cannot be empty')
        return v.strip()
    
    @validator('daily_schedules')
    def validate_daily_schedules(cls, v, values):
        """Validate daily schedules consistency"""
        duration_days = values.get('duration_days')
        if duration_days and len(v) > duration_days:
            raise ValueError('Number of daily schedules cannot exceed program duration')
        
        # Validate day numbers are sequential
        day_numbers = [schedule.day_number for schedule in v.values()]
        if day_numbers and (min(day_numbers) < 1 or max(day_numbers) > duration_days):
            raise ValueError('Day numbers must be between 1 and program duration')
        
        return v
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate end date is after start date"""
        start_date = values.get('start_date')
        if start_date and v and v <= start_date:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('completion_percentage')
    def validate_completion_percentage(cls, v, values):
        """Calculate completion percentage based on completed sessions"""
        total_planned = values.get('total_sessions_planned', 0)
        total_completed = values.get('total_sessions_completed', 0)
        
        if total_planned > 0:
            calculated_percentage = (total_completed / total_planned) * 100
            # Allow manual override but warn if significantly different
            if abs(v - calculated_percentage) > 5:
                # In a real implementation, you might log this discrepancy
                pass
        
        return v
    
    @validator('updated_at', pre=True, always=True)
    def set_updated_at(cls, v):
        """Always update the timestamp when model is modified"""
        return datetime.utcnow()


class WorkoutProgramCreate(BaseModel):
    """Model for creating new workout programs"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    program_type: ProgramType = Field(...)
    difficulty_level: DifficultyLevel = Field(...)
    duration_days: int = Field(..., ge=1, le=365)
    sessions_per_week: int = Field(..., ge=1, le=7)
    estimated_session_duration: int = Field(45, ge=15, le=180)
    daily_schedules: Dict[str, DaySchedule] = Field(...)
    rest_days: List[int] = Field(default_factory=list)
    progression_rules: List[ProgressionRule] = Field(default_factory=list)
    fitness_goals: List[str] = Field(default_factory=list)
    target_muscle_groups: List[str] = Field(default_factory=list)
    equipment_required: List[str] = Field(default_factory=list)
    ai_generation_metadata: Optional[AIGenerationMetadata] = None
    
    class Config:
        use_enum_values = True


class WorkoutProgramUpdate(BaseModel):
    """Model for updating existing workout programs"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    program_type: Optional[ProgramType] = None
    difficulty_level: Optional[DifficultyLevel] = None
    status: Optional[ProgramStatus] = None
    is_active: Optional[bool] = None
    completion_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    last_workout_date: Optional[date] = None
    customizations: Optional[Dict[str, Any]] = None
    total_sessions_completed: Optional[int] = Field(None, ge=0)
    average_session_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    
    class Config:
        use_enum_values = True


class WorkoutProgramResponse(BaseModel):
    """Response model for workout program API"""
    id: UUID
    user_id: Optional[UUID]
    name: str
    description: Optional[str]
    program_type: str
    difficulty_level: str
    duration_days: int
    sessions_per_week: int
    estimated_session_duration: int
    daily_schedules: Dict[str, Any]
    rest_days: List[int]
    fitness_goals: List[str]
    target_muscle_groups: List[str]
    equipment_required: List[str]
    status: str
    is_active: bool
    completion_percentage: float
    start_date: Optional[date]
    end_date: Optional[date]
    ai_generation_metadata: Optional[Dict[str, Any]] = None
    last_workout_date: Optional[date]
    total_sessions_completed: int
    total_sessions_planned: int
    average_session_rating: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class WorkoutProgramFilter(BaseModel):
    """Model for filtering workout programs"""
    program_type: Optional[ProgramType] = None
    difficulty_level: Optional[DifficultyLevel] = None
    status: Optional[ProgramStatus] = None
    is_active: Optional[bool] = None
    fitness_goal: Optional[str] = None
    equipment: Optional[str] = None
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    search: Optional[str] = None
    
    class Config:
        use_enum_values = True
