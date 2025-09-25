"""
AI Workout Generation API endpoints for FitFusion AI Workout App.
Handles AI-powered workout generation using CrewAI multi-agent system.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.responses import JSONResponse
from uuid import UUID, uuid4
import logging
import os
import asyncio
from datetime import datetime

from ..models.workout_program import DifficultyLevel
from ..models.workout_session import WorkoutType
from ..services.crew_orchestrator import CrewOrchestrator, WorkoutGenerationRequest, OrchestrationResult
from ..agents.base_agent import FitnessContext
from ..services.database_service import get_database_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/workouts", tags=["ai_generation"])

# Global orchestrator instance (would be dependency injected in production)
orchestrator = None


def get_orchestrator() -> CrewOrchestrator:
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        llm_config = _build_gemini_llm_config()
        orchestrator = CrewOrchestrator(llm_config)
    return orchestrator

def _build_gemini_llm_config() -> Dict[str, Any]:
    """Create the Gemini LLM configuration consumed by CrewAI agents."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is required for Gemini-backed CrewAI agents.")

    model_name = os.getenv("GEMINI_MODEL_TYPE", "gemini-2.0-flash-001")
    if "/" not in model_name:
        model_name = f"gemini/{model_name}"

    config: Dict[str, Any] = {
        "model": model_name,
        "api_key": api_key,
        "temperature": float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
    }

    max_tokens = os.getenv("GEMINI_MAX_TOKENS")
    if max_tokens:
        try:
            config["max_tokens"] = int(max_tokens)
        except ValueError:
            logger.warning("Invalid GEMINI_MAX_TOKENS value '%s'; ignoring", max_tokens)

    top_p = os.getenv("GEMINI_TOP_P")
    if top_p:
        try:
            config["top_p"] = float(top_p)
        except ValueError:
            logger.warning("Invalid GEMINI_TOP_P value '%s'; ignoring", top_p)

    timeout = os.getenv("GEMINI_TIMEOUT")
    if timeout:
        try:
            config["timeout"] = float(timeout)
        except ValueError:
            logger.warning("Invalid GEMINI_TIMEOUT value '%s'; ignoring", timeout)

    api_version = os.getenv("GEMINI_API_VERSION")
    if api_version:
        config["api_version"] = api_version

    return config




# Dependency for getting current user (placeholder)
async def get_current_user_id() -> UUID:
    """Get current authenticated user ID"""
    return UUID('12345678-1234-5678-9012-123456789abc')


# In-memory task storage (would use Redis or database in production)
generation_tasks: Dict[str, Dict[str, Any]] = {}


@router.post("/generate", response_model=Dict[str, Any])
async def start_workout_generation(
    generation_request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    user_id: UUID = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Start AI workout generation process.
    
    Args:
        generation_request: Workout generation parameters
        background_tasks: FastAPI background tasks
        
    Returns:
        Dict with task_id for tracking generation progress
    """
    try:
        task_id = str(uuid4())
        logger.info(f"Starting workout generation task {task_id} for user {user_id}")
        
        # Validate request
        required_fields = ["workout_type", "duration_minutes", "difficulty_level"]
        for field in required_fields:
            if field not in generation_request:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        # Allow request payload to override user id when provided (e.g. authenticated clients)
        override_user_id = (
            generation_request.get("user_id")
            or generation_request.get("user_context", {}).get("user_id")
        )
        if override_user_id:
            try:
                user_id = UUID(str(override_user_id))
            except ValueError:
                logger.warning("Received invalid user_id override %s; falling back to dependency", override_user_id)

        # Create fitness context from request
        fitness_context = FitnessContext(
            user_id=user_id,
            fitness_goals=generation_request.get("fitness_goals", ["general_fitness"]),
            experience_level=generation_request.get("experience_level", "beginner"),
            available_equipment=generation_request.get("available_equipment", []),
            space_constraints=generation_request.get("space_constraints", {}),
            time_constraints=generation_request.get("time_constraints", {}),
            physical_attributes=generation_request.get("physical_attributes", {}),
            preferences=generation_request.get("preferences", {}),
            current_program=generation_request.get("current_program"),
            recent_sessions=generation_request.get("recent_sessions", []),
            progress_history=generation_request.get("progress_history", [])
        )
        
        # Create workout generation request
        workout_request = WorkoutGenerationRequest(
            user_context=fitness_context,
            workout_type=generation_request["workout_type"],
            duration_minutes=generation_request["duration_minutes"],
            difficulty_level=generation_request["difficulty_level"],
            focus_areas=generation_request.get("focus_areas", []),
            equipment_preference=generation_request.get("equipment_preference"),
            special_requirements=generation_request.get("special_requirements", [])
        )
        
        # Initialize task status
        generation_tasks[task_id] = {
            "status": "started",
            "progress": 0,
            "message": "Initializing AI agents...",
            "started_at": datetime.now(),
            "user_id": user_id,
            "request": workout_request.dict(),
            "result": None,
            "error": None
        }
        
        # Start background generation
        background_tasks.add_task(generate_workout_background, task_id, workout_request, user_id)
        
        logger.info(f"Workout generation task {task_id} started successfully")
        return {
            "task_id": task_id,
            "status": "started",
            "message": "Workout generation started. Use the task_id to check progress.",
            "estimated_time_seconds": 30
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting workout generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start workout generation: {str(e)}"
        )


async def generate_workout_background(task_id: str, request: WorkoutGenerationRequest, user_id: UUID):
    """Background task for workout generation"""
    try:
        logger.info(f"Background generation started for task {task_id}")
        
        # Update progress
        generation_tasks[task_id].update({
            "status": "in_progress",
            "progress": 10,
            "message": "Analyzing user preferences..."
        })
        
        # Get orchestrator and generate workout
        orchestrator = get_orchestrator()
        
        # Update progress
        generation_tasks[task_id].update({
            "progress": 30,
            "message": "Consulting AI fitness experts..."
        })
        
        # Generate workout (this is the main AI processing)
        result = await orchestrator.generate_workout(request)
        
        if result.success:
            try:
                await persist_generated_workout(user_id, request, result)
            except Exception as persistence_error:
                logger.warning(f"Failed to persist generated workout for task {task_id}: {persistence_error}")
            generation_tasks[task_id].update({
                "status": "completed",
                "progress": 100,
                "message": "Workout generated successfully!",
                "result": result.dict(),
                "completed_at": datetime.now()
            })
            logger.info(f"Workout generation completed successfully for task {task_id}")
        else:
            generation_tasks[task_id].update({
                "status": "failed",
                "progress": 0,
                "message": f"Generation failed: {result.error_message}",
                "error": result.error_message,
                "completed_at": datetime.now()
            })
            logger.error(f"Workout generation failed for task {task_id}: {result.error_message}")
            
    except Exception as e:
        logger.error(f"Background generation error for task {task_id}: {str(e)}")
        generation_tasks[task_id].update({
            "status": "failed",
            "progress": 0,
            "message": f"Generation error: {str(e)}",
            "error": str(e),
            "completed_at": datetime.now()
        })




async def persist_generated_workout(user_id: UUID, request: WorkoutGenerationRequest, result: OrchestrationResult) -> None:
    """Store generated workout artifacts in Supabase tables."""
    try:
        db_service = get_database_service()
    except Exception as exc:
        logger.warning(f"Unable to access database service for workout persistence: {exc}")
        return

    supabase_client = getattr(db_service, "supabase", None)
    if supabase_client is None:
        logger.info("Supabase client not configured; skipping workout persistence")
        return

    workout = result.workout_response
    if workout is None:
        logger.info("No workout payload available to persist")
        return

    user_id_str = str(user_id)
    macro_plan = result.orchestration_metadata.get('macro_plan') if isinstance(result.orchestration_metadata, dict) else None

    def _extract_rows(response: Any) -> List[Dict[str, Any]]:
        if response is None:
            return []
        data_attr = getattr(response, 'data', None)
        if data_attr is not None:
            return data_attr or []
        if isinstance(response, dict):
            return response.get('data') or []
        return []

    try:
        profile_result = supabase_client.table('user_profiles').select('id').eq('id', user_id_str).limit(1).execute()
        profile_rows = _extract_rows(profile_result)
        if not profile_rows:
            logger.info("No user profile found for %s; attempting to create minimal profile", user_id_str)
            context = request.user_context
            preferences = context.preferences if isinstance(context.preferences, dict) else {}
            minimal_profile = {
                'id': user_id_str,
                'email': preferences.get('email'),
                'fitness_goals': context.fitness_goals,
                'experience_level': context.experience_level,
                'physical_attributes': context.physical_attributes,
                'space_constraints': context.space_constraints,
                'noise_preferences': preferences.get('noise_preferences', {}),
                'scheduling_preferences': preferences.get('scheduling_preferences', {}),
                'ai_coaching_settings': preferences.get('ai_coaching_settings', {}),
            }
            supabase_client.table('user_profiles').upsert(minimal_profile).execute()
    except Exception as exc:
        logger.warning(f"Unable to verify user profile for persistence: {exc}")
        return

    phase_breakdown = workout.phase_duration_breakdown or {}
    warmup_seconds = phase_breakdown.get('warmup')
    main_seconds = phase_breakdown.get('main')
    cooldown_seconds = phase_breakdown.get('cooldown')

    if warmup_seconds is None:
        warmup_seconds = sum(item.get('duration', 0) for item in workout.warmup or [])
    if main_seconds is None:
        main_seconds = sum(ex.get('total_duration_seconds', ex.get('duration', 0)) for ex in workout.exercises or [])
    if cooldown_seconds is None:
        cooldown_seconds = sum(item.get('duration', 0) for item in workout.cooldown or [])

    total_seconds = workout.total_estimated_duration_seconds or (warmup_seconds + main_seconds + cooldown_seconds)
    if total_seconds and total_seconds > 0:
        duration_minutes = max(1, int(round(total_seconds / 60)))
    else:
        duration_minutes = workout.duration_minutes or request.duration_minutes or 45
        total_seconds = duration_minutes * 60

    warmup = workout.warmup or []
    main_exercises = workout.exercises or []
    cooldown = workout.cooldown or []

    schedule_payload = {
        "day_number": 1,
        "workout_type": workout.workout_type or request.workout_type,
        "is_rest_day": False,
        "estimated_duration": duration_minutes,
        "warmup_exercises": warmup,
        "main_exercises": main_exercises,
        "cooldown_exercises": cooldown,
        "focus_areas": request.focus_areas,
        "notes": "Generated by FitFusion AI",
        "equipment_needed": workout.equipment_needed or [],
        "phase_duration_seconds": {
            "warmup": warmup_seconds,
            "main": main_seconds,
            "cooldown": cooldown_seconds
        }
    }

    metadata = {
        "generated_by": "fitfusion_crewai",
        "generation_version": "1.0.0",
        "generation_timestamp": datetime.utcnow().isoformat() + "Z",
        "agents_involved": [contrib.agent_name for contrib in result.agent_contributions],
        "generation_parameters": {
            "workout_type": request.workout_type,
            "duration_minutes": request.duration_minutes,
            "difficulty_level": request.difficulty_level,
            "focus_areas": request.focus_areas,
            "special_requirements": request.special_requirements,
            "equipment_preference": request.equipment_preference,
        },
        "execution_time": result.total_execution_time,
        "estimated_duration_seconds": total_seconds,
        "phase_duration_seconds": schedule_payload["phase_duration_seconds"],
        "macro_plan": macro_plan,
    }

    program_payload = {
        "user_id": user_id_str,
        "name": workout.name or f"AI Generated {request.workout_type.title()} Workout",
        "description": workout.description or "Personalized workout generated by FitFusion AI.",
        "duration_days": 1,
        "difficulty_level": (workout.difficulty_level or request.difficulty_level or "intermediate"),
        "daily_schedules": {"day_1": schedule_payload},
        "ai_generation_metadata": metadata,
        "is_active": False,
        "completion_percentage": 0.0,
    }

    try:
        program_result = supabase_client.table("workout_programs").insert(program_payload).execute()
    except Exception as exc:
        logger.warning(f"Failed to persist generated workout program: {exc}")
        return

    program_data = getattr(program_result, "data", None)
    if not program_data:
        logger.warning("Supabase did not return a workout_programs record; skipping session persistence")
        return

    program_id = program_data[0].get("id")
    if not program_id:
        logger.warning("Workout program inserted without ID; skipping session persistence")
        return

    session_payload = {
        "program_id": program_id,
        "user_id": user_id_str,
        "scheduled_date": datetime.utcnow().date().isoformat(),
        "warmup_exercises": warmup,
        "main_exercises": main_exercises,
        "cooldown_exercises": cooldown,
        "estimated_duration": duration_minutes,
        "completion_status": "not_started",
    }

    try:
        supabase_client.table("workout_sessions").insert(session_payload).execute()
        logger.info("Persisted generated workout for user %s to Supabase", user_id_str)
    except Exception as exc:
        logger.warning(f"Failed to persist generated workout session: {exc}")
@router.get("/generate/{task_id}", response_model=Dict[str, Any])
async def get_generation_status(
    task_id: str,
    user_id: UUID = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get the status of a workout generation task.
    
    Args:
        task_id: ID of the generation task
        
    Returns:
        Dict with task status, progress, and result if completed
    """
    try:
        logger.info(f"Checking status for task {task_id}")
        
        if task_id not in generation_tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Generation task not found: {task_id}"
            )
        
        task_info = generation_tasks[task_id]
        
        # Verify user owns this task
        if task_info["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this generation task"
            )
        
        response = {
            "task_id": task_id,
            "status": task_info["status"],
            "progress": task_info["progress"],
            "message": task_info["message"],
            "started_at": task_info["started_at"].isoformat()
        }
        
        if task_info["status"] == "completed" and task_info["result"]:
            response["workout"] = task_info["result"]["workout_response"]
            response["agent_contributions"] = task_info["result"]["agent_contributions"]
            response["execution_time"] = task_info["result"]["total_execution_time"]
        
        if task_info["status"] == "failed" and task_info["error"]:
            response["error"] = task_info["error"]
        
        if "completed_at" in task_info:
            response["completed_at"] = task_info["completed_at"].isoformat()
        
        logger.info(f"Status retrieved for task {task_id}: {task_info['status']}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get generation status: {str(e)}"
        )


@router.delete("/generate/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_generation_task(
    task_id: str,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Cancel a running workout generation task.
    
    Args:
        task_id: ID of the generation task to cancel
    """
    try:
        logger.info(f"Cancelling task {task_id}")
        
        if task_id not in generation_tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Generation task not found: {task_id}"
            )
        
        task_info = generation_tasks[task_id]
        
        # Verify user owns this task
        if task_info["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this generation task"
            )
        
        if task_info["status"] in ["completed", "failed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel task with status: {task_info['status']}"
            )
        
        # Update task status
        generation_tasks[task_id].update({
            "status": "cancelled",
            "message": "Task cancelled by user",
            "completed_at": datetime.now()
        })
        
        logger.info(f"Task {task_id} cancelled successfully")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel generation task: {str(e)}"
        )


@router.get("/history", response_model=List[Dict[str, Any]])
async def get_generation_history(
    user_id: UUID = Depends(get_current_user_id),
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get user's workout generation history.
    
    Args:
        limit: Maximum number of results to return
        
    Returns:
        List of recent generation tasks
    """
    try:
        logger.info(f"Fetching generation history for user {user_id}")
        
        # Filter tasks for this user
        user_tasks = [
            {
                "task_id": task_id,
                "status": task_info["status"],
                "started_at": task_info["started_at"].isoformat(),
                "completed_at": task_info.get("completed_at", {}).isoformat() if task_info.get("completed_at") else None,
                "workout_type": task_info["request"].get("workout_type"),
                "duration_minutes": task_info["request"].get("duration_minutes"),
                "difficulty_level": task_info["request"].get("difficulty_level")
            }
            for task_id, task_info in generation_tasks.items()
            if task_info["user_id"] == user_id
        ]
        
        # Sort by start time (most recent first) and limit
        user_tasks.sort(key=lambda x: x["started_at"], reverse=True)
        user_tasks = user_tasks[:limit]
        
        logger.info(f"Retrieved {len(user_tasks)} generation history items")
        return user_tasks
        
    except Exception as e:
        logger.error(f"Error fetching generation history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve generation history: {str(e)}"
        )


@router.get("/agents/info", response_model=Dict[str, Any])
async def get_agent_info() -> Dict[str, Any]:
    """
    Get information about available AI agents.
    
    Returns:
        Dict with agent information and capabilities
    """
    try:
        logger.info("Fetching AI agent information")
        
        orchestrator = get_orchestrator()
        agent_info = orchestrator.get_agent_info()
        
        # Add performance stats if available
        performance_stats = orchestrator.get_agent_performance_stats()
        
        response = {
            "agents": agent_info,
            "performance_stats": performance_stats,
            "total_agents": len(agent_info),
            "orchestrator_version": "1.0.0"
        }
        
        logger.info(f"Retrieved information for {len(agent_info)} agents")
        return response
        
    except Exception as e:
        logger.error(f"Error fetching agent info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve agent information: {str(e)}"
        )


@router.post("/quick-generate", response_model=Dict[str, Any])
async def quick_workout_generation(
    workout_type: str,
    duration_minutes: int,
    difficulty_level: str,
    user_id: UUID = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Quick workout generation for simple requests (synchronous).
    
    Args:
        workout_type: Type of workout (strength, cardio, mixed)
        duration_minutes: Workout duration in minutes
        difficulty_level: Difficulty level (beginner, intermediate, advanced)
        
    Returns:
        Dict with generated workout
    """
    try:
        logger.info(f"Quick workout generation for user {user_id}")
        
        # Validate parameters
        valid_types = ["strength", "cardio", "mixed", "flexibility"]
        if workout_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid workout type. Must be one of: {valid_types}"
            )
        
        if duration_minutes < 5 or duration_minutes > 120:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duration must be between 5 and 120 minutes"
            )
        
        valid_levels = ["beginner", "intermediate", "advanced"]
        if difficulty_level not in valid_levels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid difficulty level. Must be one of: {valid_levels}"
            )
        
        # Create simple fitness context
        fitness_context = FitnessContext(
            user_id=user_id,
            fitness_goals=["general_fitness"],
            experience_level=difficulty_level,
            available_equipment=[],
            space_constraints={},
            time_constraints={},
            physical_attributes={},
            preferences={}
        )
        
        # Create workout request
        workout_request = WorkoutGenerationRequest(
            user_context=fitness_context,
            workout_type=workout_type,
            duration_minutes=duration_minutes,
            difficulty_level=difficulty_level,
            focus_areas=[],
            special_requirements=[]
        )
        
        # Generate workout synchronously (with timeout)
        orchestrator = get_orchestrator()
        
        try:
            result = await asyncio.wait_for(
                orchestrator.generate_workout(workout_request),
                timeout=30.0  # 30 second timeout
            )
            
            if result.success:
                logger.info(f"Quick workout generated successfully for user {user_id}")
                return {
                    "success": True,
                    "workout": result.workout_response.dict(),
                    "generation_time": result.total_execution_time,
                    "agents_used": [contrib.agent_name for contrib in result.agent_contributions]
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Workout generation failed: {result.error_message}"
                )
                
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Workout generation timed out. Please try the async endpoint for complex requests."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in quick workout generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate workout: {str(e)}"
        )


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for AI generation service"""
    try:
        orchestrator = get_orchestrator()
        agent_count = len(orchestrator.get_agent_info())
        
        return {
            "status": "healthy",
            "service": "ai_generation_api",
            "version": "1.0.0",
            "agents_available": agent_count,
            "active_tasks": len(generation_tasks)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "ai_generation_api",
            "error": str(e)
        }
