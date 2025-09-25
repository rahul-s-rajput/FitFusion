"""
ProgressRecord model for FitFusion AI Workout App.
Represents historical tracking data for performance analysis and motivation.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, date
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator
from enum import Enum


class RecordType(str, Enum):
    """Types of progress records"""
    WORKOUT_COMPLETION = "workout_completion"
    STRENGTH_MILESTONE = "strength_milestone"
    ENDURANCE_MILESTONE = "endurance_milestone"
    STREAK_ACHIEVEMENT = "streak_achievement"
    WEIGHT_MILESTONE = "weight_milestone"
    FLEXIBILITY_MILESTONE = "flexibility_milestone"
    CONSISTENCY_MILESTONE = "consistency_milestone"


class MilestoneType(str, Enum):
    """Types of milestones achieved"""
    PERSONAL_BEST = "personal_best"
    GOAL_ACHIEVED = "goal_achieved"
    STREAK_MILESTONE = "streak_milestone"
    PROGRAM_COMPLETION = "program_completion"
    WEIGHT_TARGET = "weight_target"
    ENDURANCE_TARGET = "endurance_target"
    STRENGTH_TARGET = "strength_target"


class ContextData(BaseModel):
    """Additional context for progress records"""
    exercise_id: Optional[UUID] = Field(None, description="Related exercise if applicable")
    program_id: Optional[UUID] = Field(None, description="Related program if applicable")
    session_id: Optional[UUID] = Field(None, description="Related workout session if applicable")
    equipment_id: Optional[UUID] = Field(None, description="Equipment used if applicable")
    
    # Exercise-specific context
    exercise_name: Optional[str] = Field(None, description="Exercise name for reference")
    sets_completed: Optional[int] = Field(None, ge=0, description="Sets completed")
    reps_completed: Optional[int] = Field(None, ge=0, description="Total reps completed")
    weight_used: Optional[float] = Field(None, ge=0, description="Weight used in kg")
    duration: Optional[int] = Field(None, ge=0, description="Duration in seconds")
    
    # Program-specific context
    program_name: Optional[str] = Field(None, description="Program name for reference")
    program_day: Optional[int] = Field(None, ge=1, description="Day in program when achieved")
    
    # Additional metadata
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")


class AchievementData(BaseModel):
    """Details about achievement and comparison to previous records"""
    previous_best: Optional[float] = Field(None, description="Previous best value")
    improvement_amount: Optional[float] = Field(None, description="Amount of improvement")
    improvement_percentage: Optional[float] = Field(None, description="Percentage improvement")
    
    # Streak information
    current_streak: Optional[int] = Field(None, ge=0, description="Current streak count")
    best_streak: Optional[int] = Field(None, ge=0, description="Best streak ever")
    
    # Goal tracking
    target_value: Optional[float] = Field(None, description="Target value if goal-based")
    progress_to_goal: Optional[float] = Field(None, ge=0, le=1, description="Progress percentage to goal")
    
    # Ranking/percentile
    user_rank: Optional[int] = Field(None, ge=1, description="Rank among user's records")
    percentile: Optional[float] = Field(None, ge=0, le=100, description="Percentile among similar users")
    
    # Motivation data
    celebration_message: Optional[str] = Field(None, description="Motivational message")
    next_milestone: Optional[str] = Field(None, description="Next milestone to work towards")


class ProgressRecord(BaseModel):
    """Historical tracking data for performance analysis and motivation"""
    id: UUID = Field(default_factory=uuid4, description="Unique record identifier")
    user_id: UUID = Field(..., description="Record owner")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation date")
    record_date: date = Field(..., description="Date of tracked activity")
    
    # Record details
    record_type: RecordType = Field(..., description="Type of progress record")
    metric_name: str = Field(..., min_length=1, max_length=100, description="Specific metric being tracked")
    metric_value: float = Field(..., description="Numerical value achieved")
    metric_unit: str = Field(..., min_length=1, max_length=20, description="Unit of measurement")
    
    # Achievement details
    milestone_type: Optional[MilestoneType] = Field(None, description="Type of milestone if applicable")
    context_data: Optional[ContextData] = Field(None, description="Additional context")
    achievement_data: Optional[AchievementData] = Field(None, description="Achievement details and comparisons")
    
    # Sync metadata
    sync_status: str = Field("pending", description="Sync status for offline/online coordination")
    last_synced_at: Optional[datetime] = Field(None, description="Last successful sync timestamp")
    
    @validator('record_date')
    def validate_record_date(cls, v):
        """Record date cannot be in the future"""
        if v > date.today():
            raise ValueError('Record date cannot be in the future')
        return v
    
    @validator('metric_value')
    def validate_metric_value(cls, v, values):
        """Metric value validation based on record type"""
        record_type = values.get('record_type')
        
        # Most metrics should be positive
        if record_type in [
            RecordType.STRENGTH_MILESTONE,
            RecordType.ENDURANCE_MILESTONE,
            RecordType.STREAK_ACHIEVEMENT,
            RecordType.WEIGHT_MILESTONE,
            RecordType.FLEXIBILITY_MILESTONE
        ] and v <= 0:
            raise ValueError(f'Metric value must be positive for {record_type}')
        
        return v
    
    @validator('metric_unit')
    def validate_metric_unit(cls, v, values):
        """Validate metric unit matches the record type"""
        record_type = values.get('record_type')
        metric_name = values.get('metric_name', '').lower()
        
        # Common unit validations
        valid_units = {
            'weight': ['kg', 'lbs', 'pounds'],
            'distance': ['km', 'miles', 'meters', 'm'],
            'time': ['seconds', 'minutes', 'hours', 's', 'min', 'h'],
            'reps': ['reps', 'repetitions', 'count'],
            'sets': ['sets', 'count'],
            'streak': ['days', 'weeks', 'workouts']
        }
        
        # This is a basic validation - could be more sophisticated
        return v
    
    def calculate_improvement(self, previous_record: Optional['ProgressRecord']) -> Optional[AchievementData]:
        """Calculate improvement compared to previous record"""
        if not previous_record or previous_record.metric_name != self.metric_name:
            return None
        
        improvement_amount = self.metric_value - previous_record.metric_value
        improvement_percentage = (improvement_amount / previous_record.metric_value) * 100 if previous_record.metric_value > 0 else 0
        
        return AchievementData(
            previous_best=previous_record.metric_value,
            improvement_amount=improvement_amount,
            improvement_percentage=improvement_percentage
        )
    
    def is_personal_best(self, user_records: List['ProgressRecord']) -> bool:
        """Check if this record is a personal best for the metric"""
        same_metric_records = [
            r for r in user_records 
            if r.metric_name == self.metric_name and r.record_date <= self.record_date
        ]
        
        if not same_metric_records:
            return True
        
        # For most metrics, higher is better
        # This could be customized based on metric type
        max_value = max(r.metric_value for r in same_metric_records)
        return self.metric_value >= max_value
    
    def generate_celebration_message(self) -> str:
        """Generate a motivational celebration message"""
        if self.milestone_type == MilestoneType.PERSONAL_BEST:
            return f"🎉 New personal best! You achieved {self.metric_value} {self.metric_unit} in {self.metric_name}!"
        elif self.milestone_type == MilestoneType.STREAK_MILESTONE:
            return f"🔥 Amazing streak! {self.metric_value} {self.metric_unit} and counting!"
        elif self.milestone_type == MilestoneType.GOAL_ACHIEVED:
            return f"🎯 Goal achieved! You hit your target of {self.metric_value} {self.metric_unit}!"
        elif self.milestone_type == MilestoneType.PROGRAM_COMPLETION:
            return f"✅ Program completed! Great job finishing your workout program!"
        else:
            return f"💪 Great progress! {self.metric_value} {self.metric_unit} in {self.metric_name}!"


class ProgressRecordCreate(BaseModel):
    """Schema for creating a new progress record"""
    user_id: UUID
    record_date: date
    record_type: RecordType
    metric_name: str = Field(..., min_length=1, max_length=100)
    metric_value: float
    metric_unit: str = Field(..., min_length=1, max_length=20)
    milestone_type: Optional[MilestoneType] = None
    context_data: Optional[ContextData] = None
    achievement_data: Optional[AchievementData] = None


class ProgressRecordUpdate(BaseModel):
    """Schema for updating a progress record"""
    record_date: Optional[date] = None
    metric_value: Optional[float] = None
    metric_unit: Optional[str] = Field(None, min_length=1, max_length=20)
    milestone_type: Optional[MilestoneType] = None
    context_data: Optional[ContextData] = None
    achievement_data: Optional[AchievementData] = None


class ProgressRecordResponse(BaseModel):
    """Schema for progress record API responses"""
    id: UUID
    user_id: UUID
    created_at: datetime
    record_date: date
    record_type: RecordType
    metric_name: str
    metric_value: float
    metric_unit: str
    milestone_type: Optional[MilestoneType]
    context_data: Optional[ContextData]
    achievement_data: Optional[AchievementData]
    is_personal_best: bool = False
    celebration_message: str
    
    @classmethod
    def from_progress_record(cls, record: ProgressRecord, user_records: List[ProgressRecord] = None) -> "ProgressRecordResponse":
        """Create response from ProgressRecord model"""
        user_records = user_records or []
        is_pb = record.is_personal_best(user_records)
        
        return cls(
            id=record.id,
            user_id=record.user_id,
            created_at=record.created_at,
            record_date=record.record_date,
            record_type=record.record_type,
            metric_name=record.metric_name,
            metric_value=record.metric_value,
            metric_unit=record.metric_unit,
            milestone_type=record.milestone_type,
            context_data=record.context_data,
            achievement_data=record.achievement_data,
            is_personal_best=is_pb,
            celebration_message=record.generate_celebration_message()
        )


class ProgressSummary(BaseModel):
    """Summary of user's progress across different metrics"""
    user_id: UUID
    total_records: int
    personal_bests: int
    active_streaks: int
    completed_programs: int
    
    # Recent achievements (last 30 days)
    recent_records: List[ProgressRecordResponse]
    recent_milestones: List[ProgressRecordResponse]
    
    # Top metrics
    top_improvements: List[ProgressRecordResponse]
    longest_streaks: List[ProgressRecordResponse]
    
    # Goals progress
    goals_achieved: int
    goals_in_progress: int
    
    @classmethod
    def from_user_records(cls, user_id: UUID, records: List[ProgressRecord]) -> "ProgressSummary":
        """Create progress summary from user's records"""
        if not records:
            return cls(
                user_id=user_id,
                total_records=0,
                personal_bests=0,
                active_streaks=0,
                completed_programs=0,
                recent_records=[],
                recent_milestones=[],
                top_improvements=[],
                longest_streaks=[],
                goals_achieved=0,
                goals_in_progress=0
            )
        
        # Calculate summary statistics
        total_records = len(records)
        personal_bests = sum(1 for r in records if r.milestone_type == MilestoneType.PERSONAL_BEST)
        completed_programs = sum(1 for r in records if r.milestone_type == MilestoneType.PROGRAM_COMPLETION)
        goals_achieved = sum(1 for r in records if r.milestone_type == MilestoneType.GOAL_ACHIEVED)
        
        # Recent records (last 30 days)
        recent_date = date.today()
        recent_records = [
            ProgressRecordResponse.from_progress_record(r, records)
            for r in records
            if (recent_date - r.record_date).days <= 30
        ]
        
        # Recent milestones
        recent_milestones = [
            r for r in recent_records
            if r.milestone_type is not None
        ]
        
        return cls(
            user_id=user_id,
            total_records=total_records,
            personal_bests=personal_bests,
            active_streaks=0,  # Would need more complex calculation
            completed_programs=completed_programs,
            recent_records=recent_records[:10],  # Limit to 10 most recent
            recent_milestones=recent_milestones[:5],  # Limit to 5 most recent
            top_improvements=[],  # Would need more complex calculation
            longest_streaks=[],   # Would need more complex calculation
            goals_achieved=goals_achieved,
            goals_in_progress=0   # Would need goal tracking system
        )
