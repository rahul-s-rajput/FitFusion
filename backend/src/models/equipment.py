"""
Equipment model for FitFusion AI Workout App.
Represents available exercise equipment with specifications for AI matching.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator
from enum import Enum


class EquipmentCategory(str, Enum):
    """Equipment categories for organization and filtering"""
    WEIGHTS = "weights"
    CARDIO = "cardio"
    RESISTANCE = "resistance"
    FLEXIBILITY = "flexibility"
    BODYWEIGHT = "bodyweight"
    FUNCTIONAL = "functional"
    RECOVERY = "recovery"


class EquipmentCondition(str, Enum):
    """Equipment condition states"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    NEEDS_REPAIR = "needs_repair"


class WeightSpecifications(BaseModel):
    """Specifications for weight equipment"""
    weight_range: Optional[str] = Field(None, description="Weight range (e.g., '5-50 lbs')")
    weight_unit: str = Field("lbs", description="Weight unit (lbs/kg)")
    adjustment_type: Optional[str] = Field(None, description="Type of weight adjustment")
    increment: Optional[float] = Field(None, description="Weight increment")


class CardioSpecifications(BaseModel):
    """Specifications for cardio equipment"""
    max_speed: Optional[float] = Field(None, description="Maximum speed")
    incline_range: Optional[str] = Field(None, description="Incline range")
    resistance_levels: Optional[int] = Field(None, description="Number of resistance levels")
    display_features: List[str] = Field(default_factory=list, description="Display features")


class ResistanceSpecifications(BaseModel):
    """Specifications for resistance equipment"""
    resistance_levels: List[str] = Field(default_factory=list, description="Available resistance levels")
    material: Optional[str] = Field(None, description="Material type")
    length: Optional[float] = Field(None, description="Length in meters")
    handles: bool = Field(True, description="Has handles")


class GeneralSpecifications(BaseModel):
    """General equipment specifications"""
    dimensions: Optional[Dict[str, float]] = Field(None, description="Dimensions (length, width, height)")
    weight: Optional[float] = Field(None, description="Equipment weight")
    material: Optional[str] = Field(None, description="Primary material")
    brand: Optional[str] = Field(None, description="Brand name")
    model: Optional[str] = Field(None, description="Model name")
    year_purchased: Optional[int] = Field(None, description="Year of purchase")
    warranty_until: Optional[datetime] = Field(None, description="Warranty expiration")


class Equipment(BaseModel):
    """Main equipment model"""
    id: UUID = Field(default_factory=uuid4, description="Unique equipment identifier")
    user_id: Optional[UUID] = Field(None, description="Owner user ID")
    
    # Basic information
    name: str = Field(..., min_length=1, max_length=100, description="Equipment name")
    category: EquipmentCategory = Field(..., description="Equipment category")
    condition: EquipmentCondition = Field(EquipmentCondition.EXCELLENT, description="Current condition")
    is_available: bool = Field(True, description="Whether equipment is available for use")
    
    # Specifications (category-specific)
    specifications: Optional[Dict[str, Any]] = Field(None, description="Equipment-specific specifications")
    
    # Usage and maintenance
    usage_notes: Optional[str] = Field(None, max_length=500, description="Usage notes or instructions")
    maintenance_notes: Optional[str] = Field(None, max_length=500, description="Maintenance history/notes")
    last_maintenance: Optional[datetime] = Field(None, description="Last maintenance date")
    next_maintenance: Optional[datetime] = Field(None, description="Next scheduled maintenance")
    
    # Location and storage
    location: Optional[str] = Field(None, description="Storage location")
    space_required: Optional[Dict[str, float]] = Field(None, description="Space required for use")
    setup_time: Optional[int] = Field(None, description="Setup time in minutes")
    
    # AI matching attributes
    noise_level: str = Field("moderate", description="Noise level when in use")
    skill_level_required: str = Field("beginner", description="Minimum skill level required")
    muscle_groups: List[str] = Field(default_factory=list, description="Primary muscle groups targeted")
    exercise_types: List[str] = Field(default_factory=list, description="Types of exercises possible")
    
    # Metadata
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
                "name": "Adjustable Dumbbells",
                "category": "weights",
                "condition": "excellent",
                "is_available": True,
                "specifications": {
                    "weight_range": "5-50 lbs",
                    "adjustment_type": "dial",
                    "increment": 2.5,
                    "weight_unit": "lbs"
                },
                "usage_notes": "Great for strength training, easy to adjust",
                "location": "home_gym",
                "space_required": {"length": 1.5, "width": 0.5, "height": 0.3},
                "setup_time": 1,
                "noise_level": "low",
                "skill_level_required": "beginner",
                "muscle_groups": ["chest", "shoulders", "arms", "back"],
                "exercise_types": ["strength", "isolation", "compound"]
            }
        }
    
    @validator('name')
    def validate_name(cls, v):
        """Validate equipment name"""
        if not v or v.strip() == "":
            raise ValueError('Equipment name cannot be empty')
        return v.strip()
    
    @validator('specifications')
    def validate_specifications(cls, v, values):
        """Validate specifications based on category"""
        if v is None:
            return v
        
        category = values.get('category')
        if category == EquipmentCategory.WEIGHTS:
            # Validate weight specifications
            if 'weight_range' in v and v['weight_range']:
                weight_range = v['weight_range']
                if not any(unit in weight_range.lower() for unit in ['lbs', 'kg', 'pounds', 'kilograms']):
                    raise ValueError('Weight range must include units (lbs/kg)')
        
        return v
    
    @validator('updated_at', pre=True, always=True)
    def set_updated_at(cls, v):
        """Always update the timestamp when model is modified"""
        return datetime.utcnow()
    
    @validator('muscle_groups')
    def validate_muscle_groups(cls, v):
        """Validate muscle groups list"""
        valid_groups = [
            'chest', 'back', 'shoulders', 'arms', 'biceps', 'triceps',
            'core', 'abs', 'legs', 'quadriceps', 'hamstrings', 'glutes',
            'calves', 'full_body', 'cardio'
        ]
        for group in v:
            if group.lower() not in valid_groups:
                raise ValueError(f'Invalid muscle group: {group}')
        return [group.lower() for group in v]


class EquipmentCreate(BaseModel):
    """Model for creating new equipment"""
    name: str = Field(..., min_length=1, max_length=100)
    category: EquipmentCategory = Field(...)
    condition: EquipmentCondition = Field(EquipmentCondition.EXCELLENT)
    is_available: bool = Field(True)
    specifications: Optional[Dict[str, Any]] = None
    usage_notes: Optional[str] = Field(None, max_length=500)
    maintenance_notes: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = None
    space_required: Optional[Dict[str, float]] = None
    setup_time: Optional[int] = None
    noise_level: str = Field("moderate")
    skill_level_required: str = Field("beginner")
    muscle_groups: List[str] = Field(default_factory=list)
    exercise_types: List[str] = Field(default_factory=list)
    
    class Config:
        use_enum_values = True


class EquipmentUpdate(BaseModel):
    """Model for updating existing equipment"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[EquipmentCategory] = None
    condition: Optional[EquipmentCondition] = None
    is_available: Optional[bool] = None
    specifications: Optional[Dict[str, Any]] = None
    usage_notes: Optional[str] = Field(None, max_length=500)
    maintenance_notes: Optional[str] = Field(None, max_length=500)
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    location: Optional[str] = None
    space_required: Optional[Dict[str, float]] = None
    setup_time: Optional[int] = None
    noise_level: Optional[str] = None
    skill_level_required: Optional[str] = None
    muscle_groups: Optional[List[str]] = None
    exercise_types: Optional[List[str]] = None
    
    class Config:
        use_enum_values = True


class EquipmentResponse(BaseModel):
    """Response model for equipment API"""
    id: UUID
    user_id: Optional[UUID]
    name: str
    category: str
    condition: str
    is_available: bool
    specifications: Optional[Dict[str, Any]]
    usage_notes: Optional[str]
    maintenance_notes: Optional[str]
    last_maintenance: Optional[datetime]
    next_maintenance: Optional[datetime]
    location: Optional[str]
    space_required: Optional[Dict[str, float]]
    setup_time: Optional[int]
    noise_level: str
    skill_level_required: str
    muscle_groups: List[str]
    exercise_types: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class EquipmentFilter(BaseModel):
    """Model for filtering equipment"""
    category: Optional[EquipmentCategory] = None
    condition: Optional[EquipmentCondition] = None
    is_available: Optional[bool] = None
    muscle_group: Optional[str] = None
    exercise_type: Optional[str] = None
    noise_level: Optional[str] = None
    skill_level: Optional[str] = None
    search: Optional[str] = None
    
    class Config:
        use_enum_values = True


class EquipmentRecommendation(BaseModel):
    """Model for equipment recommendations"""
    equipment_name: str
    category: EquipmentCategory
    reason: str
    priority: int = Field(..., ge=1, le=10, description="Priority score 1-10")
    estimated_cost: Optional[str] = None
    space_required: Optional[Dict[str, float]] = None
    alternatives: List[str] = Field(default_factory=list)
    
    class Config:
        use_enum_values = True
