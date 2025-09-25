"""
Exercise model for FitFusion AI Workout App.
Represents individual exercise movements with instructions, difficulty levels, and demonstration media.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator
from enum import Enum


class ExerciseCategory(str, Enum):
    """Exercise categories for organization"""
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"
    CORE = "core"
    PLYOMETRIC = "plyometric"
    FUNCTIONAL = "functional"
    REHABILITATION = "rehabilitation"
    WARMUP = "warmup"
    COOLDOWN = "cooldown"


class DifficultyLevel(str, Enum):
    """Exercise difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ExerciseType(str, Enum):
    """Types of exercise execution"""
    REPS = "reps"  # Repetition-based
    TIME = "time"  # Time-based
    DISTANCE = "distance"  # Distance-based
    HOLD = "hold"  # Static hold


class MuscleGroup(str, Enum):
    """Primary muscle groups"""
    CHEST = "chest"
    BACK = "back"
    SHOULDERS = "shoulders"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    FOREARMS = "forearms"
    CORE = "core"
    ABS = "abs"
    OBLIQUES = "obliques"
    QUADRICEPS = "quadriceps"
    HAMSTRINGS = "hamstrings"
    GLUTES = "glutes"
    CALVES = "calves"
    FULL_BODY = "full_body"
    CARDIO = "cardio"


class DemonstrationMedia(BaseModel):
    """Media for exercise demonstration"""
    image_url: Optional[str] = Field(None, description="Static image URL")
    video_url: Optional[str] = Field(None, description="Video demonstration URL")
    gif_url: Optional[str] = Field(None, description="Animated GIF URL")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail image URL")
    duration: Optional[int] = Field(None, description="Video/GIF duration in seconds")
    alt_text: Optional[str] = Field(None, description="Alternative text for accessibility")


class ExerciseInstructions(BaseModel):
    """Detailed exercise instructions"""
    setup: List[str] = Field(default_factory=list, description="Setup instructions")
    execution: List[str] = Field(default_factory=list, description="Execution steps")
    breathing: Optional[str] = Field(None, description="Breathing instructions")
    common_mistakes: List[str] = Field(default_factory=list, description="Common mistakes to avoid")
    safety_tips: List[str] = Field(default_factory=list, description="Safety considerations")
    modifications: List[str] = Field(default_factory=list, description="Exercise modifications")


class ExerciseParameters(BaseModel):
    """Default parameters for exercise execution"""
    default_sets: Optional[int] = Field(None, ge=1, le=10, description="Default number of sets")
    default_reps: Optional[int] = Field(None, ge=1, le=100, description="Default repetitions per set")
    default_duration: Optional[int] = Field(None, ge=5, le=3600, description="Default duration in seconds")
    default_rest: Optional[int] = Field(None, ge=10, le=300, description="Default rest between sets in seconds")
    rep_range_min: Optional[int] = Field(None, description="Minimum recommended reps")
    rep_range_max: Optional[int] = Field(None, description="Maximum recommended reps")
    progression_notes: Optional[str] = Field(None, description="How to progress this exercise")


class Exercise(BaseModel):
    """Main exercise model"""
    id: UUID = Field(default_factory=uuid4, description="Unique exercise identifier")
    
    # Basic information
    name: str = Field(..., min_length=1, max_length=100, description="Exercise name")
    category: ExerciseCategory = Field(..., description="Exercise category")
    difficulty_level: DifficultyLevel = Field(..., description="Difficulty level")
    exercise_type: ExerciseType = Field(..., description="Type of exercise execution")
    
    # Muscle targeting
    primary_muscles: List[MuscleGroup] = Field(..., min_items=1, description="Primary muscles worked")
    secondary_muscles: List[MuscleGroup] = Field(default_factory=list, description="Secondary muscles worked")
    
    # Equipment requirements
    equipment_required: List[str] = Field(default_factory=list, description="Required equipment")
    equipment_alternatives: List[str] = Field(default_factory=list, description="Alternative equipment options")
    
    # Instructions and media
    instructions: ExerciseInstructions = Field(..., description="Detailed exercise instructions")
    demonstration_media: Optional[DemonstrationMedia] = Field(None, description="Demonstration media")
    
    # Exercise parameters
    parameters: Optional[ExerciseParameters] = Field(None, description="Default exercise parameters")
    
    # Physical requirements
    space_required: Optional[Dict[str, float]] = Field(None, description="Space requirements in meters")
    noise_level: str = Field("moderate", description="Noise level generated")
    
    # Accessibility and modifications
    accessibility_notes: Optional[str] = Field(None, description="Accessibility considerations")
    injury_considerations: List[str] = Field(default_factory=list, description="Injury considerations")
    
    # Tags and search
    tags: List[str] = Field(default_factory=list, description="Search tags")
    keywords: List[str] = Field(default_factory=list, description="Search keywords")
    
    # Metadata
    created_by: Optional[str] = Field(None, description="Creator/source")
    verified: bool = Field(False, description="Whether exercise is verified by experts")
    popularity_score: float = Field(0.0, ge=0.0, le=10.0, description="Popularity score")
    effectiveness_rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Effectiveness rating")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
        schema_extra = {
            "example": {
                "name": "Push-ups",
                "category": "strength",
                "difficulty_level": "beginner",
                "exercise_type": "reps",
                "primary_muscles": ["chest", "shoulders", "triceps"],
                "secondary_muscles": ["core"],
                "equipment_required": ["bodyweight"],
                "instructions": {
                    "setup": [
                        "Start in a plank position with hands slightly wider than shoulders",
                        "Keep your body in a straight line from head to heels"
                    ],
                    "execution": [
                        "Lower your body until chest nearly touches the floor",
                        "Push back up to starting position",
                        "Keep core engaged throughout the movement"
                    ],
                    "breathing": "Inhale on the way down, exhale on the way up",
                    "common_mistakes": [
                        "Sagging hips",
                        "Flaring elbows too wide",
                        "Not going through full range of motion"
                    ]
                },
                "parameters": {
                    "default_sets": 3,
                    "default_reps": 12,
                    "default_rest": 60,
                    "rep_range_min": 8,
                    "rep_range_max": 20
                },
                "space_required": {"length": 2.0, "width": 1.0},
                "noise_level": "low",
                "tags": ["bodyweight", "upper_body", "compound"],
                "verified": True
            }
        }
    
    @validator('name')
    def validate_name(cls, v):
        """Validate exercise name"""
        if not v or v.strip() == "":
            raise ValueError('Exercise name cannot be empty')
        return v.strip().title()
    
    @validator('primary_muscles')
    def validate_primary_muscles(cls, v):
        """Ensure at least one primary muscle is specified"""
        if not v or len(v) == 0:
            raise ValueError('At least one primary muscle must be specified')
        return v
    
    @validator('equipment_required')
    def validate_equipment(cls, v):
        """Validate equipment requirements"""
        if not v:
            return ["bodyweight"]  # Default to bodyweight if no equipment specified
        return v
    
    @validator('instructions')
    def validate_instructions(cls, v):
        """Validate that essential instructions are provided"""
        if not v.setup and not v.execution:
            raise ValueError('Exercise must have either setup or execution instructions')
        return v
    
    @validator('updated_at', pre=True, always=True)
    def set_updated_at(cls, v):
        """Always update the timestamp when model is modified"""
        return datetime.utcnow()


class ExerciseCreate(BaseModel):
    """Model for creating new exercises"""
    name: str = Field(..., min_length=1, max_length=100)
    category: ExerciseCategory = Field(...)
    difficulty_level: DifficultyLevel = Field(...)
    exercise_type: ExerciseType = Field(...)
    primary_muscles: List[MuscleGroup] = Field(..., min_items=1)
    secondary_muscles: List[MuscleGroup] = Field(default_factory=list)
    equipment_required: List[str] = Field(default_factory=list)
    equipment_alternatives: List[str] = Field(default_factory=list)
    instructions: ExerciseInstructions = Field(...)
    demonstration_media: Optional[DemonstrationMedia] = None
    parameters: Optional[ExerciseParameters] = None
    space_required: Optional[Dict[str, float]] = None
    noise_level: str = Field("moderate")
    accessibility_notes: Optional[str] = None
    injury_considerations: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    
    class Config:
        use_enum_values = True


class ExerciseUpdate(BaseModel):
    """Model for updating existing exercises"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[ExerciseCategory] = None
    difficulty_level: Optional[DifficultyLevel] = None
    exercise_type: Optional[ExerciseType] = None
    primary_muscles: Optional[List[MuscleGroup]] = Field(None, min_items=1)
    secondary_muscles: Optional[List[MuscleGroup]] = None
    equipment_required: Optional[List[str]] = None
    equipment_alternatives: Optional[List[str]] = None
    instructions: Optional[ExerciseInstructions] = None
    demonstration_media: Optional[DemonstrationMedia] = None
    parameters: Optional[ExerciseParameters] = None
    space_required: Optional[Dict[str, float]] = None
    noise_level: Optional[str] = None
    accessibility_notes: Optional[str] = None
    injury_considerations: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    effectiveness_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    
    class Config:
        use_enum_values = True


class ExerciseResponse(BaseModel):
    """Response model for exercise API"""
    id: UUID
    name: str
    category: str
    difficulty_level: str
    exercise_type: str
    primary_muscles: List[str]
    secondary_muscles: List[str]
    equipment_required: List[str]
    equipment_alternatives: List[str]
    instructions: Dict[str, Any]
    demonstration_media: Optional[Dict[str, Any]]
    parameters: Optional[Dict[str, Any]]
    space_required: Optional[Dict[str, float]]
    noise_level: str
    accessibility_notes: Optional[str]
    injury_considerations: List[str]
    tags: List[str]
    keywords: List[str]
    verified: bool
    popularity_score: float
    effectiveness_rating: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class ExerciseFilter(BaseModel):
    """Model for filtering exercises"""
    category: Optional[ExerciseCategory] = None
    difficulty_level: Optional[DifficultyLevel] = None
    exercise_type: Optional[ExerciseType] = None
    primary_muscle: Optional[MuscleGroup] = None
    equipment: Optional[str] = None
    noise_level: Optional[str] = None
    verified_only: bool = Field(False)
    min_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    search: Optional[str] = None
    
    class Config:
        use_enum_values = True


class ExerciseSubstitution(BaseModel):
    """Model for exercise substitutions"""
    original_exercise_id: UUID
    substitute_exercise_id: UUID
    reason: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    equipment_match: bool
    muscle_group_match: bool
    difficulty_match: bool
