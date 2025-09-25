"""
UserProfile model for FitFusion AI Workout App.
Represents individual user with fitness goals and preferences for AI workout generation.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator
from enum import Enum


class ExperienceLevel(str, Enum):
    """User experience levels for workout difficulty"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class FitnessGoal(str, Enum):
    """Available fitness goals"""
    WEIGHT_LOSS = "weight_loss"
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"
    GENERAL_FITNESS = "general_fitness"
    MUSCLE_BUILDING = "muscle_building"


class PhysicalAttributes(BaseModel):
    """Physical attributes of the user"""
    height: Optional[int] = Field(None, description="Height in centimeters")
    weight: Optional[float] = Field(None, description="Weight in kilograms")
    age: Optional[int] = Field(None, ge=13, le=120, description="Age in years (13-120)")
    gender: Optional[str] = Field(None, description="Gender (optional)")
    
    @validator('height')
    def validate_height(cls, v):
        if v is not None and (v < 100 or v > 250):
            raise ValueError('Height must be between 100-250 cm')
        return v
    
    @validator('weight')
    def validate_weight(cls, v):
        if v is not None and (v < 20 or v > 300):
            raise ValueError('Weight must be between 20-300 kg')
        return v


class SpaceConstraints(BaseModel):
    """Available space for workouts"""
    available_space: str = Field(..., description="Type of available space")
    dimensions: Optional[Dict[str, float]] = Field(None, description="Space dimensions in meters")
    ceiling_height: Optional[str] = Field("standard", description="Ceiling height category")
    flooring: Optional[str] = Field("carpet", description="Type of flooring")
    equipment_storage: Optional[str] = Field("limited", description="Equipment storage capacity")


class NoisePreferences(BaseModel):
    """Noise level preferences and constraints"""
    quiet_hours: Optional[str] = Field(None, description="Quiet hours range (e.g., '22:00-08:00')")
    max_noise_level: str = Field("moderate", description="Maximum acceptable noise level")
    noise_sensitive_neighbors: bool = Field(False, description="Whether neighbors are noise-sensitive")


class SchedulingPreferences(BaseModel):
    """Workout scheduling preferences"""
    preferred_times: List[str] = Field(default_factory=list, description="Preferred workout times")
    frequency: int = Field(3, ge=1, le=7, description="Workouts per week (1-7)")
    session_duration: int = Field(45, ge=15, le=120, description="Preferred session duration in minutes")
    rest_days: List[str] = Field(default_factory=list, description="Preferred rest days")


class AICoachingSettings(BaseModel):
    """AI coaching behavior preferences"""
    motivation_level: str = Field("moderate", description="Motivation intensity level")
    instruction_detail: str = Field("detailed", description="Level of exercise instruction detail")
    personality: str = Field("encouraging", description="AI coach personality type")
    feedback_frequency: str = Field("regular", description="How often to provide feedback")
    adaptation_speed: str = Field("moderate", description="How quickly to adapt programs")


class UserProfile(BaseModel):
    """Main user profile model"""
    id: UUID = Field(default_factory=uuid4, description="Unique user identifier")
    email: Optional[str] = Field(None, description="User email (optional for personal use)")
    
    # Core fitness information
    fitness_goals: List[FitnessGoal] = Field(..., min_items=1, description="Selected fitness goals")
    experience_level: ExperienceLevel = Field(..., description="User's fitness experience level")
    
    # Optional detailed information
    physical_attributes: Optional[PhysicalAttributes] = Field(None, description="Physical characteristics")
    space_constraints: Optional[SpaceConstraints] = Field(None, description="Workout space limitations")
    noise_preferences: Optional[NoisePreferences] = Field(None, description="Noise level preferences")
    scheduling_preferences: Optional[SchedulingPreferences] = Field(None, description="Workout scheduling preferences")
    ai_coaching_settings: Optional[AICoachingSettings] = Field(None, description="AI behavior preferences")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Profile creation timestamp")
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
                "fitness_goals": ["strength", "endurance"],
                "experience_level": "intermediate",
                "physical_attributes": {
                    "height": 175,
                    "weight": 70,
                    "age": 28,
                    "gender": "male"
                },
                "space_constraints": {
                    "available_space": "home_gym",
                    "dimensions": {"length": 4, "width": 3, "height": 2.5},
                    "flooring": "rubber_mats"
                },
                "noise_preferences": {
                    "quiet_hours": "22:00-07:00",
                    "max_noise_level": "moderate"
                },
                "scheduling_preferences": {
                    "preferred_times": ["morning", "evening"],
                    "frequency": 4,
                    "session_duration": 45
                },
                "ai_coaching_settings": {
                    "motivation_level": "high",
                    "instruction_detail": "detailed",
                    "personality": "encouraging"
                }
            }
        }
    
    @validator('fitness_goals')
    def validate_fitness_goals(cls, v):
        """Ensure at least one fitness goal is selected"""
        if not v or len(v) == 0:
            raise ValueError('At least one fitness goal must be selected')
        return v
    
    @validator('updated_at', pre=True, always=True)
    def set_updated_at(cls, v):
        """Always update the timestamp when model is modified"""
        return datetime.utcnow()


class UserProfileCreate(BaseModel):
    """Model for creating a new user profile"""
    email: Optional[str] = None
    fitness_goals: List[FitnessGoal] = Field(..., min_items=1)
    experience_level: ExperienceLevel = Field(...)
    physical_attributes: Optional[PhysicalAttributes] = None
    space_constraints: Optional[SpaceConstraints] = None
    noise_preferences: Optional[NoisePreferences] = None
    scheduling_preferences: Optional[SchedulingPreferences] = None
    ai_coaching_settings: Optional[AICoachingSettings] = None
    
    class Config:
        use_enum_values = True


class UserProfileUpdate(BaseModel):
    """Model for updating an existing user profile"""
    email: Optional[str] = None
    fitness_goals: Optional[List[FitnessGoal]] = Field(None, min_items=1)
    experience_level: Optional[ExperienceLevel] = None
    physical_attributes: Optional[PhysicalAttributes] = None
    space_constraints: Optional[SpaceConstraints] = None
    noise_preferences: Optional[NoisePreferences] = None
    scheduling_preferences: Optional[SchedulingPreferences] = None
    ai_coaching_settings: Optional[AICoachingSettings] = None
    
    class Config:
        use_enum_values = True
    
    @validator('fitness_goals')
    def validate_fitness_goals_update(cls, v):
        """Ensure at least one fitness goal if provided"""
        if v is not None and len(v) == 0:
            raise ValueError('At least one fitness goal must be selected')
        return v


class UserProfileResponse(BaseModel):
    """Response model for user profile API"""
    id: UUID
    email: Optional[str]
    fitness_goals: List[str]
    experience_level: str
    physical_attributes: Optional[Dict[str, Any]]
    space_constraints: Optional[Dict[str, Any]]
    noise_preferences: Optional[Dict[str, Any]]
    scheduling_preferences: Optional[Dict[str, Any]]
    ai_coaching_settings: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
