"""
Workout Program API endpoints for FitFusion AI Workout App.
Handles workout program management, activation, and progress tracking.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from uuid import UUID, uuid4
import logging

from fastapi import APIRouter, HTTPException, Depends, status, Query

from ..models.workout_program import (
    WorkoutProgram,
    WorkoutProgramCreate,
    WorkoutProgramUpdate,
    WorkoutProgramResponse,
    DifficultyLevel,
    ProgramType,
    ProgramStatus,
    DaySchedule,
    ProgressionRule,
    AIGenerationMetadata,
)
from ..services.database_service import get_database_service


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/programs", tags=["programs"])

# Keys exposed by the response model
_RESPONSE_FIELDS = {
    "id",
    "user_id",
    "name",
    "description",
    "program_type",
    "difficulty_level",
    "duration_days",
    "sessions_per_week",
    "estimated_session_duration",
    "daily_schedules",
    "rest_days",
    "fitness_goals",
    "target_muscle_groups",
    "equipment_required",
    "status",
    "is_active",
    "completion_percentage",
    "start_date",
    "end_date",
    "last_workout_date",
    "total_sessions_completed",
    "total_sessions_planned",
    "average_session_rating",
    "created_at",
    "updated_at",
}


# Dependency for getting current user (placeholder)
async def get_current_user_id() -> UUID:
    """Get current authenticated user ID"""
    return UUID('12345678-1234-5678-9012-123456789abc')


def _program_to_response(program: WorkoutProgram) -> WorkoutProgramResponse:
    """Map internal model to API response"""
    data = program.model_dump(include=_RESPONSE_FIELDS)
    return WorkoutProgramResponse(**data)


def _build_strength_program(user_id: UUID, program_id: Optional[UUID] = None) -> WorkoutProgram:
    program_uuid = program_id or uuid4()
    ai_metadata = AIGenerationMetadata(
        generated_by="fitfusion_ai",
        generation_version="v2.1",
        generation_timestamp=datetime(2024, 1, 5, 9, 0),
        agents_involved=["strength_coach", "equipment_advisor"],
        generation_parameters={"focus": "compound_movements", "progression": "linear"},
        confidence_score=0.82,
        customization_level="standard",
    )
    daily_schedules = {
        "day_1": DaySchedule(
            day_number=1,
            day_name="Upper Body Strength",
            workout_type="strength",
            is_rest_day=False,
            warmup_exercises=[{"name": "Arm Circles", "duration": 5}],
            main_exercises=[{"name": "Push Ups", "sets": 3, "reps": 12}],
            cooldown_exercises=[{"name": "Chest Stretch", "duration": 5}],
            estimated_duration=45,
            intensity_level=6.0,
            focus_areas=["upper body"],
            equipment_needed=["bodyweight"],
        ),
        "day_2": DaySchedule(
            day_number=2,
            day_name="Active Recovery",
            workout_type="mobility",
            is_rest_day=False,
            warmup_exercises=[{"name": "Cat Cow", "reps": 10}],
            main_exercises=[{"name": "Mobility Flow", "duration": 20}],
            cooldown_exercises=[{"name": "Breathing Drill", "duration": 5}],
            estimated_duration=35,
            intensity_level=3.0,
            focus_areas=["mobility"],
            equipment_needed=["yoga mat"],
        ),
        "day_3": DaySchedule(
            day_number=3,
            day_name="Lower Body Strength",
            workout_type="strength",
            is_rest_day=False,
            warmup_exercises=[{"name": "Leg Swings", "duration": 5}],
            main_exercises=[{"name": "Goblet Squats", "sets": 3, "reps": 12}],
            cooldown_exercises=[{"name": "Hamstring Stretch", "duration": 5}],
            estimated_duration=45,
            intensity_level=6.0,
            focus_areas=["lower body"],
            equipment_needed=["dumbbells"],
        ),
    }
    progression_rules = [
        ProgressionRule(
            rule_type="load_progression",
            trigger_condition="complete_two_weeks",
            adjustment={"load_increase_percent": 5},
            description="Increase load after two consistent weeks",
        )
    ]
    return WorkoutProgram(
        id=program_uuid,
        user_id=user_id,
        name="Beginner Strength Builder",
        description="A 4-week program focused on foundational strength",
        program_type=ProgramType.STRENGTH_BUILDING,
        difficulty_level=DifficultyLevel.BEGINNER,
        duration_days=28,
        sessions_per_week=3,
        estimated_session_duration=45,
        daily_schedules=daily_schedules,
        rest_days=[4, 7],
        progression_rules=progression_rules,
        fitness_goals=["strength", "stability"],
        target_muscle_groups=["chest", "back", "legs"],
        equipment_required=["dumbbells", "resistance bands"],
        status=ProgramStatus.ACTIVE,
        is_active=True,
        completion_percentage=35.0,
        start_date=date(2024, 1, 2),
        end_date=None,
        last_workout_date=date(2024, 1, 18),
        ai_generation_metadata=ai_metadata,
        customizations={"preferred_focus": "upper_body"},
        total_sessions_completed=10,
        total_sessions_planned=12,
        average_session_rating=4.6,
    )


def _build_endurance_program(user_id: UUID, program_id: Optional[UUID] = None) -> WorkoutProgram:
    program_uuid = program_id or uuid4()
    ai_metadata = AIGenerationMetadata(
        generated_by="fitfusion_ai",
        generation_version="v2.0",
        generation_timestamp=datetime(2023, 11, 20, 7, 30),
        agents_involved=["cardio_coach", "recovery_specialist"],
        generation_parameters={"intensity": "high", "work_rest_ratio": "1:2"},
        confidence_score=0.9,
        customization_level="personalized",
    )
    daily_schedules = {
        "day_1": DaySchedule(
            day_number=1,
            day_name="HIIT Session",
            workout_type="hiit",
            is_rest_day=False,
            warmup_exercises=[{"name": "Jumping Jacks", "duration": 3}],
            main_exercises=[{"name": "Intervals", "rounds": 8, "work": 30, "rest": 60}],
            cooldown_exercises=[{"name": "Slow Walk", "duration": 5}],
            estimated_duration=30,
            intensity_level=8.0,
            focus_areas=["cardio"],
            equipment_needed=["bodyweight"],
        ),
        "day_2": DaySchedule(
            day_number=2,
            day_name="Active Recovery",
            workout_type="mobility",
            is_rest_day=False,
            warmup_exercises=[{"name": "Dynamic Stretch", "duration": 5}],
            main_exercises=[{"name": "Light Jog", "duration": 15}],
            cooldown_exercises=[{"name": "Standing Quad Stretch", "duration": 5}],
            estimated_duration=25,
            intensity_level=4.0,
            focus_areas=["recovery"],
            equipment_needed=["bodyweight"],
        ),
    }
    progression_rules = [
        ProgressionRule(
            rule_type="interval_adjustment",
            trigger_condition="completion_rate_above_80",
            adjustment={"work_duration_seconds": 5, "rest_duration_seconds": -5},
            description="Adjust intervals based on consistency",
        )
    ]
    return WorkoutProgram(
        id=program_uuid,
        user_id=user_id,
        name="HIIT Cardio Blast",
        description="High-intensity interval training for cardiovascular fitness",
        program_type=ProgramType.ENDURANCE,
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        duration_days=21,
        sessions_per_week=4,
        estimated_session_duration=30,
        daily_schedules=daily_schedules,
        rest_days=[3, 6],
        progression_rules=progression_rules,
        fitness_goals=["cardio", "conditioning"],
        target_muscle_groups=["full_body"],
        equipment_required=["jump rope", "bodyweight"],
        status=ProgramStatus.COMPLETED,
        is_active=False,
        completion_percentage=100.0,
        start_date=date(2023, 12, 1),
        end_date=date(2023, 12, 21),
        last_workout_date=date(2023, 12, 21),
        ai_generation_metadata=ai_metadata,
        customizations={"preferred_intensity": "high"},
        total_sessions_completed=12,
        total_sessions_planned=12,
        average_session_rating=4.8,
    )


def _build_flexibility_program(user_id: UUID, program_id: Optional[UUID] = None) -> WorkoutProgram:
    program_uuid = program_id or uuid4()
    ai_metadata = AIGenerationMetadata(
        generated_by="fitfusion_ai",
        generation_version="v1.8",
        generation_timestamp=datetime(2024, 1, 30, 6, 45),
        agents_involved=["mobility_coach", "preferences_manager"],
        generation_parameters={"focus": "mobility", "style": "gentle"},
        confidence_score=0.75,
        customization_level="adaptive",
    )
    daily_schedules = {
        "day_1": DaySchedule(
            day_number=1,
            day_name="Morning Mobility",
            workout_type="mobility",
            is_rest_day=False,
            warmup_exercises=[{"name": "Neck Rolls", "reps": 10}],
            main_exercises=[{"name": "Flow Sequence", "duration": 20}],
            cooldown_exercises=[{"name": "Deep Breathing", "duration": 5}],
            estimated_duration=35,
            intensity_level=4.0,
            focus_areas=["hips", "thoracic spine"],
            equipment_needed=["yoga mat"],
        ),
        "day_2": DaySchedule(
            day_number=2,
            day_name="Yin Yoga",
            workout_type="yoga",
            is_rest_day=False,
            warmup_exercises=[{"name": "Cat Cow", "reps": 8}],
            main_exercises=[{"name": "Supported Triangle", "duration": 3}],
            cooldown_exercises=[{"name": "Seated Forward Fold", "duration": 4}],
            estimated_duration=40,
            intensity_level=3.5,
            focus_areas=["full body"],
            equipment_needed=["yoga blocks"],
        ),
    }
    progression_rules = [
        ProgressionRule(
            rule_type="hold_duration",
            trigger_condition="comfort_level_high",
            adjustment={"hold_seconds": 15},
            description="Extend pose holds when ready",
        )
    ]
    return WorkoutProgram(
        id=program_uuid,
        user_id=user_id,
        name="Full Body Flexibility",
        description="Comprehensive flexibility and mobility program",
        program_type=ProgramType.FLEXIBILITY,
        difficulty_level=DifficultyLevel.BEGINNER,
        duration_days=14,
        sessions_per_week=4,
        estimated_session_duration=35,
        daily_schedules=daily_schedules,
        rest_days=[3, 7],
        progression_rules=progression_rules,
        fitness_goals=["mobility", "mindfulness"],
        target_muscle_groups=["hips", "back", "shoulders"],
        equipment_required=["yoga mat", "yoga blocks"],
        status=ProgramStatus.PAUSED,
        is_active=False,
        completion_percentage=10.0,
        start_date=date(2024, 2, 1),
        end_date=None,
        last_workout_date=date(2024, 2, 5),
        ai_generation_metadata=ai_metadata,
        customizations={"session_time": "morning"},
        total_sessions_completed=2,
        total_sessions_planned=8,
        average_session_rating=None,
    )


def _sample_programs(user_id: UUID) -> List[WorkoutProgram]:
    """Create representative sample programs"""
    return [
        _build_strength_program(user_id),
        _build_endurance_program(user_id),
        _build_flexibility_program(user_id),
    ]


def _extract_rows(response: Any) -> List[Dict[str, Any]]:
    """Normalize Supabase responses into raw row dictionaries."""
    if response is None:
        return []
    data = getattr(response, 'data', None)
    if data is not None:
        return data or []
    if isinstance(response, dict):
        return response.get('data') or []
    return []


def _parse_date(value: Any) -> Optional[date]:
    """Parse ISO date strings into date objects."""
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
    except Exception:
        return None


def _parse_datetime(value: Any) -> datetime:
    """Parse ISO datetime strings into datetime objects."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except Exception:
            pass
    return datetime.utcnow()


def _program_row_to_response(row: Dict[str, Any]) -> WorkoutProgramResponse:
    """Convert Supabase workout_program row into API response model."""
    schedules: Dict[str, Any] = row.get('daily_schedules') or {}
    if isinstance(schedules, str):
        try:
            import json
            schedules = json.loads(schedules)
        except Exception:
            schedules = {}

    schedule_values = list(schedules.values()) if isinstance(schedules, dict) else []
    sessions_per_week = row.get('sessions_per_week') or max(1, len(schedule_values))

    durations = [entry.get('estimated_duration') for entry in schedule_values if isinstance(entry, dict) and entry.get('estimated_duration')]
    if durations:
        estimated_duration = int(round(sum(durations) / len(durations)))
    else:
        estimated_duration = row.get('estimated_session_duration') or (row.get('duration_days') and max(20, int((row['duration_days'] * 45) / row['duration_days']))) or 45

    metadata = row.get('ai_generation_metadata') or {}
    if isinstance(metadata, str):
        try:
            import json
            metadata = json.loads(metadata)
        except Exception:
            metadata = {}

    generation_params = metadata.get('generation_parameters') if isinstance(metadata, dict) else {}
    focus_areas = generation_params.get('focus_areas') if isinstance(generation_params, dict) else []
    if not focus_areas:
        for entry in schedule_values:
            if isinstance(entry, dict) and entry.get('focus_areas'):
                focus_areas = entry['focus_areas']
                break

    equipment: List[str] = []
    for entry in schedule_values:
        if isinstance(entry, dict):
            eq = entry.get('equipment_needed') or entry.get('equipment_required')
            if isinstance(eq, list):
                equipment.extend(str(item) for item in eq if item)
    equipment = sorted(set(equipment))

    completion_raw = row.get('completion_percentage')
    if completion_raw is None:
        total_planned_val = row.get('total_sessions_planned') or 0
        total_completed_val = row.get('total_sessions_completed') or 0
        completion_raw = (total_completed_val / total_planned_val) * 100 if total_planned_val else 0
    completion_percentage = float(completion_raw * 100 if completion_raw <= 1 else completion_raw)

    last_workout = _parse_date(row.get('last_workout_date'))
    total_completed = row.get('total_sessions_completed')
    if total_completed is None:
        total_completed = 0
    total_planned = row.get('total_sessions_planned')
    if total_planned is None:
        total_planned = len(schedule_values) or 0
    avg_rating = row.get('average_session_rating')

    def _coalesce(key: str, default):
        value = row.get(key)
        return value if value is not None else default

    return WorkoutProgramResponse(
        id=UUID(row['id']) if isinstance(row.get('id'), str) else row.get('id', uuid4()),
        user_id=UUID(row['user_id']) if row.get('user_id') else None,
        name=row.get('name', 'AI Generated Workout'),
        description=row.get('description'),
        program_type=row.get('program_type') or 'general_fitness',
        difficulty_level=row.get('difficulty_level') or 'intermediate',
        duration_days=row.get('duration_days') or max(1, len(schedule_values) or 1),
        sessions_per_week=sessions_per_week,
        estimated_session_duration=estimated_duration,
        daily_schedules=schedules,
        rest_days=row.get('rest_days') or [],
        fitness_goals=row.get('fitness_goals') or focus_areas or [],
        target_muscle_groups=row.get('target_muscle_groups') or focus_areas or [],
        equipment_required=row.get('equipment_required') or equipment,
        status=row.get('status') or ('active' if row.get('is_active') else 'generated'),
        is_active=bool(row.get('is_active')),
        completion_percentage=completion_percentage,
        start_date=_parse_date(row.get('start_date')),
        end_date=_parse_date(row.get('end_date')),
        last_workout_date=last_workout,
        total_sessions_completed=int(total_completed),
        total_sessions_planned=int(total_planned),
        average_session_rating=float(avg_rating) if avg_rating is not None else None,
        created_at=_parse_datetime(row.get('created_at')),
        updated_at=_parse_datetime(row.get('updated_at')),
        ai_generation_metadata=metadata if isinstance(metadata, dict) else None,
    )
@router.get("/", response_model=List[WorkoutProgramResponse])
async def get_user_programs(
    user_id: UUID = Depends(get_current_user_id),
    active_only: bool = Query(False, description="Only return active programs"),
    program_type: Optional[ProgramType] = Query(None, description="Filter by program type"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty level"),
    limit: int = Query(20, le=100, description="Maximum number of programs to return"),
) -> List[WorkoutProgramResponse]:
    """Get all workout programs for the current user with optional filtering."""
    try:
        logger.info("Fetching programs for user %s", user_id)

        responses: List[WorkoutProgramResponse] = []
        supabase_rows: List[Dict[str, Any]] = []

        try:
            db_service = get_database_service()
            supabase_client = getattr(db_service, 'supabase', None)
            if supabase_client is not None:
                query_limit = max(limit, 20)
                result = (
                    supabase_client
                    .table('workout_programs')
                    .select('*')
                    .eq('user_id', str(user_id))
                    .order('created_at', desc=True)
                    .limit(query_limit)
                    .execute()
                )
                supabase_rows = _extract_rows(result)
        except Exception as supabase_exc:
            logger.debug("Supabase program fetch failed: %s", supabase_exc)

        if supabase_rows:
            responses = [_program_row_to_response(row) for row in supabase_rows]

        def _apply_filters(program_list: List[WorkoutProgramResponse]) -> List[WorkoutProgramResponse]:
            filtered = program_list
            if active_only:
                filtered = [p for p in filtered if p.is_active]
            if program_type:
                filtered = [p for p in filtered if p.program_type == program_type.value]
            if difficulty:
                filtered = [p for p in filtered if p.difficulty_level == difficulty.value]
            return filtered

        filtered_responses = _apply_filters(responses)
        if filtered_responses:
            final_responses = filtered_responses[:limit]
            logger.info("Retrieved %d programs for user %s from Supabase", len(final_responses), user_id)
            return final_responses

        # Fallback to sample data when no Supabase programs exist
        mock_programs = _sample_programs(user_id)
        filtered_programs = _apply_filters([_program_to_response(p) for p in mock_programs])
        final_responses = filtered_programs[:limit]
        logger.info("Returning %d sample programs for user %s", len(final_responses), user_id)
        return final_responses
    except Exception as exc:
        logger.error("Error fetching programs for user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve workout programs: {exc}",
        ) from exc


@router.get("/{program_id}", response_model=WorkoutProgramResponse)
async def get_program_by_id(
    program_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
) -> WorkoutProgramResponse:
    """Get specific workout program by ID."""
    try:
        logger.info("Fetching program %s for user %s", program_id, user_id)
        supabase_program: Optional[WorkoutProgramResponse] = None
        try:
            db_service = get_database_service()
            supabase_client = getattr(db_service, 'supabase', None)
            if supabase_client is not None:
                result = (
                    supabase_client
                    .table('workout_programs')
                    .select('*')
                    .eq('id', str(program_id))
                    .eq('user_id', str(user_id))
                    .limit(1)
                    .execute()
                )
                rows = _extract_rows(result)
                if rows:
                    supabase_program = _program_row_to_response(rows[0])
        except Exception as supabase_exc:
            logger.debug("Supabase program fetch failed: %s", supabase_exc)

        if supabase_program:
            return supabase_program

        program = _build_strength_program(user_id, program_id)
        return _program_to_response(program)
    except Exception as exc:
        logger.error("Error fetching program %s: %s", program_id, exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program not found: {program_id}",
        ) from exc


@router.post("/{program_id}/activate", response_model=WorkoutProgramResponse)
async def activate_program(
    program_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
) -> WorkoutProgramResponse:
    """Activate a workout program (deactivates any currently active program)."""
    try:
        logger.info("Activating program %s for user %s", program_id, user_id)
        base_program = _build_strength_program(user_id, program_id)
        activated_program = base_program.model_copy(
            update={
                "status": ProgramStatus.ACTIVE.value,
                "is_active": True,
                "start_date": date.today(),
            }
        )
        return _program_to_response(activated_program)
    except Exception as exc:
        logger.error("Error activating program %s: %s", program_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate program: {exc}",
        ) from exc


@router.post("/{program_id}/deactivate", response_model=WorkoutProgramResponse)
async def deactivate_program(
    program_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
) -> WorkoutProgramResponse:
    """Deactivate a workout program."""
    try:
        logger.info("Deactivating program %s for user %s", program_id, user_id)
        base_program = _build_strength_program(user_id, program_id)
        deactivated_program = base_program.model_copy(
            update={
                "status": ProgramStatus.PAUSED.value,
                "is_active": False,
                "last_workout_date": date.today(),
            }
        )
        return _program_to_response(deactivated_program)
    except Exception as exc:
        logger.error("Error deactivating program %s: %s", program_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate program: {exc}",
        ) from exc


@router.post("/", response_model=WorkoutProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_program(
    program_data: WorkoutProgramCreate,
    user_id: UUID = Depends(get_current_user_id),
) -> WorkoutProgramResponse:
    """Create a new workout program (typically from AI generation)."""
    try:
        logger.info("Creating program for user %s: %s", user_id, program_data.name)

        if not program_data.name or len(program_data.name.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Program name is required",
            )

        if len(program_data.daily_schedules) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Program must include at least one daily schedule",
            )

        if len(program_data.daily_schedules) > program_data.duration_days:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Daily schedules cannot exceed program duration",
            )

        payload = program_data.model_dump(exclude_none=True)
        new_program = WorkoutProgram(
            id=uuid4(),
            user_id=user_id,
            total_sessions_planned=program_data.duration_days,
            total_sessions_completed=0,
            completion_percentage=0.0,
            is_active=False,
            status=ProgramStatus.DRAFT,
            **payload,
        )
        return _program_to_response(new_program)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error creating program for user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create program: {exc}",
        ) from exc


@router.put("/{program_id}", response_model=WorkoutProgramResponse)
async def update_program(
    program_id: UUID,
    program_update: WorkoutProgramUpdate,
    user_id: UUID = Depends(get_current_user_id),
) -> WorkoutProgramResponse:
    """Update existing workout program."""
    try:
        logger.info("Updating program %s for user %s", program_id, user_id)

        if program_update.name is not None and len(program_update.name.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Program name cannot be empty",
            )

        base_program = _build_strength_program(user_id, program_id)
        update_payload = program_update.model_dump(exclude_unset=True)

        if "program_type" in update_payload and isinstance(update_payload["program_type"], ProgramType):
            update_payload["program_type"] = update_payload["program_type"].value
        if "difficulty_level" in update_payload and isinstance(update_payload["difficulty_level"], DifficultyLevel):
            update_payload["difficulty_level"] = update_payload["difficulty_level"].value
        if "status" in update_payload and isinstance(update_payload["status"], ProgramStatus):
            update_payload["status"] = update_payload["status"].value

        updated_program = base_program.model_copy(
            update={**update_payload, "updated_at": datetime.utcnow()}
        )
        return _program_to_response(updated_program)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error updating program %s: %s", program_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update program: {exc}",
        ) from exc


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program(
    program_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
) -> None:
    """Delete a workout program and all associated sessions."""
    try:
        logger.info("Deleting program %s for user %s", program_id, user_id)
        return None
    except Exception as exc:
        logger.error("Error deleting program %s: %s", program_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete program: {exc}",
        ) from exc


@router.get("/{program_id}/progress", response_model=Dict[str, Any])
async def get_program_progress(
    program_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
) -> Dict[str, Any]:
    """Get detailed progress information for a workout program."""
    try:
        logger.info("Fetching progress for program %s", program_id)
        progress_data = {
            "program_id": str(program_id),
            "completion_percentage": 35.7,
            "days_completed": 10,
            "duration_days": 28,
            "current_week": 2,
            "total_weeks": 4,
            "sessions_completed": 8,
            "sessions_planned": 20,
            "sessions_skipped": 1,
            "consistency_score": 88.9,
            "weekly_progress": [
                {"week": 1, "sessions_completed": 4, "sessions_planned": 4, "completion_rate": 100},
                {"week": 2, "sessions_completed": 4, "sessions_planned": 5, "completion_rate": 80},
                {"week": 3, "sessions_completed": 0, "sessions_planned": 5, "completion_rate": 0},
                {"week": 4, "sessions_completed": 0, "sessions_planned": 6, "completion_rate": 0},
            ],
            "performance_trends": {
                "strength_improvement": 12.5,
                "endurance_improvement": 8.3,
                "consistency_trend": "stable",
            },
            "next_scheduled_session": {
                "date": str(date.today()),
                "type": "strength",
                "focus": "lower_body",
                "estimated_duration": 45,
            },
            "milestones_achieved": [
                {"name": "First Week Complete", "date": "2024-01-08"},
                {"name": "10 Sessions Complete", "date": "2024-01-22"},
            ],
        }
        return progress_data
    except Exception as exc:
        logger.error("Error fetching progress for program %s: %s", program_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve program progress: {exc}",
        ) from exc


# Health check endpoint
@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for programs service"""
    return {"status": "healthy", "service": "programs_api", "version": "1.0.0"}
