"""
Workout Models for FitFusion AI Workout App
Consolidated imports for all workout-related models
"""

# Import all the workout-related models
from .user_profile import UserProfile
from .equipment import Equipment
from .exercise import Exercise
from .workout_program import WorkoutProgram
from .workout_session import WorkoutSession
from .progress_record import ProgressRecord

# Export all models for easy importing
__all__ = [
    'UserProfile',
    'Equipment', 
    'Exercise',
    'WorkoutProgram',
    'WorkoutSession',
    'ProgressRecord'
]
