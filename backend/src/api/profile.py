"""
User Profile API endpoints for FitFusion AI Workout App.
Handles user profile management, preferences, and settings.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from uuid import UUID
import logging

from ..models.user_profile import (
    UserProfile, 
    UserProfileCreate, 
    UserProfileUpdate, 
    UserProfileResponse,
    ExperienceLevel,
    FitnessGoal
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/profile", tags=["profile"])


# Dependency for getting current user (placeholder - would integrate with auth system)
async def get_current_user_id() -> UUID:
    """Get current authenticated user ID - placeholder for auth integration"""
    # This would be replaced with actual authentication logic
    return UUID('12345678-1234-5678-9012-123456789abc')


@router.get("/", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: UUID = Depends(get_current_user_id)
) -> UserProfileResponse:
    """
    Get the current user's profile information.
    
    Returns:
        UserProfileResponse: Complete user profile with preferences and settings
    """
    try:
        logger.info(f"Fetching profile for user {user_id}")
        
        # This would integrate with actual database service
        # For now, return a mock response
        mock_profile = UserProfile(
            id=user_id,
            fitness_goals=[FitnessGoal.GENERAL_FITNESS],
            experience_level=ExperienceLevel.BEGINNER,
            physical_attributes={
                "height": 175,
                "weight": 70.0,
                "age": 30
            },
            space_constraints={
                "available_space": "small_room",
                "ceiling_height": 240,
                "floor_type": "hardwood"
            },
            noise_preferences={
                "max_noise_level": "moderate",
                "quiet_hours": ["22:00", "07:00"]
            },
            scheduling_preferences={
                "preferred_times": ["morning", "evening"],
                "frequency": 4,
                "session_duration": 45
            },
            ai_coaching_settings={
                "coaching_style": "encouraging",
                "feedback_frequency": "moderate",
                "challenge_level": "progressive"
            }
        )
        
        response = UserProfileResponse.from_user_profile(mock_profile)
        logger.info(f"Successfully retrieved profile for user {user_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error fetching profile for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user profile: {str(e)}"
        )


@router.put("/", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    user_id: UUID = Depends(get_current_user_id)
) -> UserProfileResponse:
    """
    Update the current user's profile information.
    
    Args:
        profile_update: Updated profile information
        
    Returns:
        UserProfileResponse: Updated user profile
    """
    try:
        logger.info(f"Updating profile for user {user_id}")
        
        # Validate update data
        if profile_update.fitness_goals is not None and len(profile_update.fitness_goals) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one fitness goal must be specified"
            )
        
        # This would integrate with actual database service
        # For now, simulate update and return mock response
        updated_profile = UserProfile(
            id=user_id,
            fitness_goals=profile_update.fitness_goals or [FitnessGoal.GENERAL_FITNESS],
            experience_level=profile_update.experience_level or ExperienceLevel.BEGINNER,
            physical_attributes=profile_update.physical_attributes or {},
            space_constraints=profile_update.space_constraints or {},
            noise_preferences=profile_update.noise_preferences or {},
            scheduling_preferences=profile_update.scheduling_preferences or {},
            ai_coaching_settings=profile_update.ai_coaching_settings or {}
        )
        
        response = UserProfileResponse.from_user_profile(updated_profile)
        logger.info(f"Successfully updated profile for user {user_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user profile: {str(e)}"
        )


@router.post("/", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_user_profile(
    profile_data: UserProfileCreate,
    user_id: UUID = Depends(get_current_user_id)
) -> UserProfileResponse:
    """
    Create a new user profile (typically during onboarding).
    
    Args:
        profile_data: Initial profile information
        
    Returns:
        UserProfileResponse: Created user profile
    """
    try:
        logger.info(f"Creating profile for user {user_id}")
        
        # Validate required fields
        if not profile_data.fitness_goals or len(profile_data.fitness_goals) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one fitness goal must be specified"
            )
        
        if not profile_data.experience_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Experience level is required"
            )
        
        # Create new profile
        new_profile = UserProfile(
            id=user_id,
            fitness_goals=profile_data.fitness_goals,
            experience_level=profile_data.experience_level,
            physical_attributes=profile_data.physical_attributes or {},
            space_constraints=profile_data.space_constraints or {},
            noise_preferences=profile_data.noise_preferences or {},
            scheduling_preferences=profile_data.scheduling_preferences or {},
            ai_coaching_settings=profile_data.ai_coaching_settings or {}
        )
        
        # This would integrate with actual database service to save the profile
        
        response = UserProfileResponse.from_user_profile(new_profile)
        logger.info(f"Successfully created profile for user {user_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating profile for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user profile: {str(e)}"
        )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_profile(
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Delete the current user's profile (account deletion).
    
    This is a destructive operation that will remove all user data.
    """
    try:
        logger.info(f"Deleting profile for user {user_id}")
        
        # This would integrate with actual database service to delete the profile
        # and all associated data (workouts, progress, etc.)
        
        logger.info(f"Successfully deleted profile for user {user_id}")
        return None
        
    except Exception as e:
        logger.error(f"Error deleting profile for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user profile: {str(e)}"
        )


@router.get("/preferences", response_model=Dict[str, Any])
async def get_user_preferences(
    user_id: UUID = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get user's AI coaching and app preferences.
    
    Returns:
        Dict containing user preferences and settings
    """
    try:
        logger.info(f"Fetching preferences for user {user_id}")
        
        # This would fetch from database
        preferences = {
            "ai_coaching_settings": {
                "coaching_style": "encouraging",
                "feedback_frequency": "moderate",
                "challenge_level": "progressive"
            },
            "notification_settings": {
                "workout_reminders": True,
                "progress_updates": True,
                "motivational_messages": False
            },
            "privacy_settings": {
                "data_sharing": False,
                "analytics_tracking": True
            }
        }
        
        logger.info(f"Successfully retrieved preferences for user {user_id}")
        return preferences
        
    except Exception as e:
        logger.error(f"Error fetching preferences for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user preferences: {str(e)}"
        )


@router.put("/preferences", response_model=Dict[str, Any])
async def update_user_preferences(
    preferences: Dict[str, Any],
    user_id: UUID = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Update user's AI coaching and app preferences.
    
    Args:
        preferences: Updated preference settings
        
    Returns:
        Dict containing updated preferences
    """
    try:
        logger.info(f"Updating preferences for user {user_id}")
        
        # Validate preferences structure
        allowed_sections = ["ai_coaching_settings", "notification_settings", "privacy_settings"]
        for section in preferences.keys():
            if section not in allowed_sections:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid preference section: {section}"
                )
        
        # This would update in database
        updated_preferences = preferences
        
        logger.info(f"Successfully updated preferences for user {user_id}")
        return updated_preferences
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating preferences for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user preferences: {str(e)}"
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_user_stats(
    user_id: UUID = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get user's fitness statistics and progress summary.
    
    Returns:
        Dict containing user statistics and achievements
    """
    try:
        logger.info(f"Fetching stats for user {user_id}")
        
        # This would calculate from actual data
        stats = {
            "total_workouts": 42,
            "total_workout_time": 1890,  # minutes
            "current_streak": 7,
            "longest_streak": 14,
            "favorite_workout_type": "strength",
            "achievements": [
                {"name": "First Workout", "date": "2024-01-01", "type": "milestone"},
                {"name": "7-Day Streak", "date": "2024-01-15", "type": "streak"},
                {"name": "50 Workouts", "date": "2024-02-20", "type": "milestone"}
            ],
            "progress_metrics": {
                "strength_improvement": 15.2,  # percentage
                "endurance_improvement": 8.7,
                "consistency_score": 85.3
            }
        }
        
        logger.info(f"Successfully retrieved stats for user {user_id}")
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching stats for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user statistics: {str(e)}"
        )


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for profile service"""
    return {"status": "healthy", "service": "profile_api", "version": "1.0.0"}
