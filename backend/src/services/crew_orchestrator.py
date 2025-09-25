"""
Crew Orchestrator service for FitFusion AI Workout App.
Coordinates multiple AI agents to generate comprehensive workout programs.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
import asyncio
import logging
import re
import json

from crewai import Crew, Task
from ..agents.base_agent import FitnessContext, WorkoutGenerationRequest, WorkoutGenerationResponse
from ..agents.strength_coach import StrengthCoach
from ..agents.cardio_coach import CardioCoach
from ..agents.nutritionist import Nutritionist
from ..agents.equipment_advisor import EquipmentAdvisor
from ..agents.recovery_specialist import RecoverySpecialist
from ..agents.motivation_coach import MotivationCoach
from ..agents.analytics_expert import AnalyticsExpert
from ..agents.preferences_manager import PreferencesManager
from ..agents.program_director import ProgramDirector
from ..agents.general_coach import GeneralCoach

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentContribution(BaseModel):
    """Represents contribution from a specific agent"""
    agent_name: str
    contribution_type: str
    content: Dict[str, Any]
    confidence_score: float = Field(ge=0.0, le=1.0)
    execution_time: float
    timestamp: datetime


class OrchestrationResult(BaseModel):
    """Result from agent orchestration"""
    request_id: UUID
    workout_response: WorkoutGenerationResponse
    agent_contributions: List[AgentContribution]
    orchestration_metadata: Dict[str, Any]
    total_execution_time: float
    success: bool
    error_message: Optional[str] = None


class CrewOrchestrator:
    """Orchestrates multiple AI agents to generate comprehensive workout programs"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        self.llm_config = llm_config
        self.agents = self._initialize_agents()
        self.request_history: List[OrchestrationResult] = []
        
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all AI agents"""
        try:
            agents = {
                'strength_coach': StrengthCoach(self.llm_config),
                'cardio_coach': CardioCoach(self.llm_config),
                'nutritionist': Nutritionist(self.llm_config),
                'equipment_advisor': EquipmentAdvisor(self.llm_config),
                'recovery_specialist': RecoverySpecialist(self.llm_config),
                'motivation_coach': MotivationCoach(self.llm_config),
                'analytics_expert': AnalyticsExpert(self.llm_config),
                'preferences_manager': PreferencesManager(self.llm_config),
                'program_director': ProgramDirector(self.llm_config),
                'general_coach': GeneralCoach(self.llm_config)
            }
            logger.info(f"Initialized {len(agents)} AI agents successfully")
            return agents
        except Exception as e:
            logger.error(f"Failed to initialize agents: {str(e)}")
            raise
    

    def _format_json_instruction(self, schema: str) -> str:
        """Helper to instruct agents to reply with strict JSON."""
        return "\n".join([
            "Return your answer strictly as valid JSON matching this schema:",
            schema,
            "Guidelines:",
            "- Do not include markdown, code fences, or commentary outside the JSON.",
            "- Use arrays even when only one element exists.",
            "- Use null for unknown numeric values instead of omitting keys.",
            "- Keep keys in snake_case."
        ])

    async def _generate_macro_plan(
        self,
        request: WorkoutGenerationRequest,
        context_analysis: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], Optional[AgentContribution]]:
        """Use Program Director agent (with heuristic fallback) to create macro time budget."""
        heuristic_plan = self._heuristic_macro_plan(request)
        plan_agent = self.agents.get('program_director')
        if not plan_agent:
            logger.warning("Program Director agent unavailable; using heuristic macro plan")
            return heuristic_plan, None

        start_time = datetime.now()
        try:
            raw_plan = plan_agent.design_macro_plan(request)
            if not isinstance(raw_plan, dict) or raw_plan.get('error'):
                logger.warning("Program Director returned invalid plan: %s", raw_plan.get('error'))
                return heuristic_plan, None

            coerced_plan = self._coerce_macro_plan(raw_plan, request, source="program_director")
            execution_time = (datetime.now() - start_time).total_seconds()
            contribution = AgentContribution(
                agent_name='program_director',
                contribution_type='macro_plan',
                content=coerced_plan,
                confidence_score=0.85,
                execution_time=execution_time,
                timestamp=datetime.now()
            )
            return coerced_plan, contribution

        except Exception as exc:
            logger.warning("Program Director failed, using heuristic plan: %s", exc)
            return heuristic_plan, None

    def _heuristic_macro_plan(self, request: WorkoutGenerationRequest) -> Dict[str, Any]:
        """Create a deterministic macro plan when AI planning is unavailable."""
        total_seconds = max(600, int(request.duration_minutes or 45) * 60)
        warmup = max(240, min(480, int(total_seconds * 0.12)))
        cooldown = max(240, min(540, int(total_seconds * 0.12)))
        if warmup + cooldown >= total_seconds - 120:
            warmup = int(total_seconds * 0.1)
            cooldown = int(total_seconds * 0.1)
        main = max(300, total_seconds - warmup - cooldown)

        focus_areas = request.focus_areas or ['full_body']
        modalities = ['strength', 'cardio'] if request.workout_type in ('mixed', 'hiit') else [request.workout_type]
        modalities = [m for m in modalities if m in {'strength', 'cardio', 'mobility', 'core', 'mixed'}]
        if not modalities:
            modalities = ['strength']

        blocks: List[Dict[str, Any]] = []
        block_count = max(2, min(3, len(focus_areas)))
        block_duration = main // block_count
        remainder = main - block_duration * block_count

        special_reqs = set(request.special_requirements or [])
        low_impact = 'low_impact' in special_reqs
        impact_level = 'low' if low_impact else 'moderate'
        available_equipment = request.user_context.available_equipment or []
        equipment_bias = 'bodyweight' if not available_equipment else 'minimal_equipment'

        for idx in range(block_count):
            focus = focus_areas[idx % len(focus_areas)]
            modality = modalities[idx % len(modalities)] if modalities else 'strength'
            duration = block_duration + (1 if idx < remainder else 0)
            blocks.append({
                'name': f"{focus.replace('_', ' ').title()} {modality.title()} Block",
                'focus_areas': [focus],
                'modality': modality,
                'duration_seconds': duration,
                'sets': 3,
                'rep_scheme': '8-12' if modality == 'strength' else None,
                'interval_style': '45s work / 15s rest' if modality in ('cardio', 'mixed') else None,
                'target_intensity': 'moderate-hard',
                'rest_seconds': 45,
                'impact_level': impact_level,
                'equipment_bias': equipment_bias,
                'coaching_priority': 'Maintain form, control tempo'
            })

        warmup_focus = ['mobility', 'activation']
        cooldown_focus = ['breathing', 'flexibility']

        plan = {
            'phase_allocation': {
                'warmup': warmup,
                'main': main,
                'cooldown': cooldown
            },
            'warmup_focus': warmup_focus,
            'main_blocks': blocks,
            'cooldown_focus': cooldown_focus,
            'intensity_curve': [
                {'phase': 'warmup', 'average_rpe': 3.0, 'notes': 'Gradual ramp to working heart rate'},
                {'phase': 'main', 'average_rpe': 7.0, 'notes': 'Intervals peak at RPE 8'},
                {'phase': 'cooldown', 'average_rpe': 2.0, 'notes': 'Guided breathing and long holds'},
            ],
            'notes': [
                'Heuristic plan generated without Program Director agent',
                'Adjust block rest and intensity to user feedback if needed'
            ],
            'source': 'heuristic_fallback'
        }
        return plan

    def _coerce_macro_plan(
        self,
        raw_plan: Dict[str, Any],
        request: WorkoutGenerationRequest,
        source: str,
    ) -> Dict[str, Any]:
        """Ensure macro plan meets structural expectations."""
        plan = json.loads(json.dumps(raw_plan))  # deep copy without non-serializable items

        total_seconds = max(600, int(request.duration_minutes or 45) * 60)
        phase_allocation = plan.get('phase_allocation') or {}
        warmup = self._parse_duration_value(phase_allocation.get('warmup')) or int(total_seconds * 0.12)
        main = self._parse_duration_value(phase_allocation.get('main')) or int(total_seconds * 0.76)
        cooldown = self._parse_duration_value(phase_allocation.get('cooldown')) or int(total_seconds * 0.12)

        total_alloc = warmup + main + cooldown
        if total_alloc != total_seconds:
            scale = total_seconds / (total_alloc or total_seconds)
            warmup = max(180, int(round(warmup * scale)))
            main = max(300, int(round(main * scale)))
            cooldown = max(180, int(round(cooldown * scale)))
            diff = total_seconds - (warmup + main + cooldown)
            cooldown += diff

        plan['phase_allocation'] = {
            'warmup': warmup,
            'main': main,
            'cooldown': cooldown
        }

        blocks = plan.get('main_blocks') or []
        if not isinstance(blocks, list) or not blocks:
            plan.update(self._heuristic_macro_plan(request))
            plan['source'] = f'{source}_with_heuristic_blocks'
            return plan

        block_total = sum(self._parse_duration_value(b.get('duration_seconds')) or 0 for b in blocks) or main
        if block_total != main:
            scale = main / (block_total or main)
            adjusted = 0
            for block in blocks:
                duration = self._parse_duration_value(block.get('duration_seconds')) or max(300, main // len(blocks))
                new_duration = max(180, int(round(duration * scale)))
                block['duration_seconds'] = new_duration
                adjusted += new_duration
            diff = main - adjusted
            idx = 0
            while blocks and diff != 0 and idx < len(blocks) * 2:
                block = blocks[idx % len(blocks)]
                adjust = 1 if diff > 0 else -1
                candidate = block['duration_seconds'] + adjust
                if candidate >= 180:
                    block['duration_seconds'] = candidate
                    diff -= adjust
                idx += 1

        for block in blocks:
            block.setdefault('focus_areas', request.focus_areas or ['full_body'])
            block.setdefault('modality', request.workout_type if request.workout_type in {'strength', 'cardio', 'mobility', 'core', 'mixed'} else 'mixed')
            block.setdefault('rest_seconds', 45)
            block.setdefault('impact_level', 'low' if 'low_impact' in (request.special_requirements or []) else 'moderate')
            if not block.get('equipment_bias'):
                block['equipment_bias'] = 'bodyweight' if not request.user_context.available_equipment else 'minimal_equipment'
            block.setdefault('coaching_priority', 'Maintain impeccable form and breathing')

        plan['main_blocks'] = blocks
        plan.setdefault('warmup_focus', ['mobility', 'activation'])
        plan.setdefault('cooldown_focus', ['breathing', 'flexibility'])
        plan.setdefault('intensity_curve', [])
        plan.setdefault('notes', [])
        plan['source'] = source
        return plan
    def _parse_duration_value(self, value: Any) -> Optional[int]:
        """Convert various duration representations to seconds."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return max(0, int(value))
        if isinstance(value, str):
            value_str = value.strip().lower()
            match = re.search(r"(\d+(?:\.\d+)?)", value_str)
            if not match:
                return None
            amount = float(match.group(1))
            if any(unit in value_str for unit in ("hour", "hr")):
                amount *= 3600
            elif "min" in value_str:
                amount *= 60
            return max(0, int(round(amount)))
        return None

    def _normalize_phase_items(
        self,
        items: List[Dict[str, Any]],
        default_duration: int = 300,
        target_total: Optional[int] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Normalize warmup/cooldown entries to consistent structure and optional time budget."""
        normalized: List[Dict[str, Any]] = []
        total = 0
        for raw in items or []:
            if not isinstance(raw, dict):
                continue
            name = str(raw.get('name') or raw.get('title') or 'Exercise').strip() or 'Exercise'
            duration_val = (
                self._parse_duration_value(raw.get('duration'))
                or self._parse_duration_value(raw.get('duration_seconds'))
                or self._parse_duration_value(raw.get('duration_minutes'))
            )
            if not duration_val or duration_val <= 0:
                duration_val = default_duration
            description = (
                raw.get('instructions')
                or raw.get('description')
                or raw.get('notes')
                or ''
            )
            cues = raw.get('coaching_cues') or raw.get('cues') or []
            if isinstance(cues, str):
                cues = [cues]
            normalized.append({
                'name': name,
                'duration': duration_val,
                'duration_seconds': duration_val,
                'description': description,
                'focus': raw.get('focus') or raw.get('target_area'),
                'intensity': raw.get('intensity'),
                'equipment': raw.get('equipment') or raw.get('equipment_needed'),
                'coaching_cues': cues
            })
            total += duration_val
        if target_total and total > 0 and normalized:
            scale = target_total / total
            scaled_total = 0
            for item in normalized:
                new_duration = max(20, int(round(item['duration'] * scale)))
                item['duration'] = new_duration
                item['duration_seconds'] = new_duration
                scaled_total += new_duration
            total = scaled_total
            difference = (target_total or 0) - total
            idx = 0
            # Adjust any rounding drift to hit exact target seconds
            while normalized and abs(difference) > 0 and idx < len(normalized) * 2:
                item = normalized[idx % len(normalized)]
                adjust = 1 if difference > 0 else -1
                candidate = item['duration'] + adjust
                if candidate >= 20:
                    item['duration'] = candidate
                    item['duration_seconds'] = candidate
                    total += adjust
                    difference -= adjust
                idx += 1
        return normalized, total

    def _normalize_main_exercises(
        self,
        exercises: List[Dict[str, Any]],
        request: WorkoutGenerationRequest,
        target_total: Optional[int] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Normalize main workout exercises, flag time vs reps, and compute duration estimates."""
        normalized: List[Dict[str, Any]] = []
        total = 0
        rest_defaults = {'beginner': 45, 'intermediate': 60, 'advanced': 75}
        for raw in exercises or []:
            if not isinstance(raw, dict):
                continue
            name = str(raw.get('name') or raw.get('title') or 'Exercise').strip() or 'Exercise'
            raw_sets = raw.get('sets') or raw.get('rounds') or 1
            try:
                sets = max(1, int(raw_sets))
            except Exception:
                sets = 1
            reps_value = raw.get('reps') or raw.get('rep_range')
            if isinstance(reps_value, str):
                rep_match = re.search(r"(\d+)", reps_value)
                reps = int(rep_match.group(1)) if rep_match else None
            else:
                try:
                    reps = int(reps_value) if reps_value is not None else None
                except Exception:
                    reps = None
            work_seconds = (
                self._parse_duration_value(raw.get('work_seconds'))
                or self._parse_duration_value(raw.get('work_interval_seconds'))
            )
            duration_val = (
                work_seconds
                or self._parse_duration_value(raw.get('duration'))
                or self._parse_duration_value(raw.get('duration_seconds_per_set'))
                or self._parse_duration_value(raw.get('duration_seconds'))
            )
            if (not duration_val or duration_val <= 0) and reps:
                duration_val = max(30, int(reps) * 4)
            if not duration_val or duration_val <= 0:
                duration_val = 45
            rest_val = (
                self._parse_duration_value(raw.get('rest_seconds'))
                or self._parse_duration_value(raw.get('rest_interval_seconds'))
                or self._parse_duration_value(raw.get('rest'))
                or rest_defaults.get(request.difficulty_level, 60)
            )
            rest_val = max(15, rest_val)
            block_duration = self._parse_duration_value(raw.get('block_duration_seconds'))
            if not block_duration or block_duration <= 0:
                block_duration = sets * duration_val + rest_val * max(0, sets - 1)
            instructions = (
                raw.get('instructions')
                or raw.get('coaching_instructions')
                or raw.get('description')
                or raw.get('notes')
                or ''
            )
            cues = raw.get('coaching_cues') or raw.get('cues') or raw.get('tips') or []
            if isinstance(cues, str):
                cues = [cues]
            target_muscles = raw.get('target_muscles') or raw.get('primary_muscles') or []
            if isinstance(target_muscles, str):
                target_muscles = [target_muscles]
            equipment = raw.get('equipment') or raw.get('equipment_needed')
            if isinstance(equipment, list):
                equipment = ", ".join(str(item) for item in equipment if item)
            if not equipment:
                equipment = 'bodyweight'
            impact_level = raw.get('impact_level') or raw.get('impact')
            intensity = raw.get('intensity') or raw.get('target_heart_rate_zone')
            time_based = bool(work_seconds) and reps is None
            if time_based:
                reps_output = None
                work_output = work_seconds or duration_val
            else:
                reps_output = reps
                work_output = None
            normalized.append({
                'name': name,
                'sets': sets,
                'reps': reps_output,
                'duration': duration_val,
                'duration_seconds_per_set': duration_val,
                'work_seconds': work_output,
                'rest_seconds': rest_val,
                'tempo': raw.get('tempo'),
                'notes': raw.get('notes') or raw.get('description'),
                'intensity': intensity,
                'impact_level': impact_level,
                'equipment': equipment,
                'target_muscles': target_muscles,
                'instructions': instructions,
                'description': instructions,
                'coaching_cues': cues,
                'tips': '; '.join(cues) if cues else None,
                'block_duration_seconds': block_duration,
                'total_duration_seconds': block_duration,
                'is_time_based': time_based
            })
            total += block_duration
        if target_total and total > 0 and normalized:
            scale = target_total / total
            adjusted_total = 0
            for ex in normalized:
                new_block = max(60, int(round(ex['total_duration_seconds'] * scale)))
                ex['block_duration_seconds'] = new_block
                ex['total_duration_seconds'] = new_block
                adjusted_total += new_block
                if ex['is_time_based'] and ex['work_seconds']:
                    ex['work_seconds'] = max(15, int(round(ex['work_seconds'] * scale)))
                    ex['duration'] = ex['work_seconds']
                elif not ex['is_time_based']:
                    ex['duration'] = max(30, int(round(ex['duration'] * scale)))
                    # keep rest the same but ensure block recalculated roughly
            total = adjusted_total
            difference = (target_total or 0) - total
            idx = 0
            while normalized and abs(difference) > 0 and idx < len(normalized) * 2:
                ex = normalized[idx % len(normalized)]
                adjust = 1 if difference > 0 else -1
                candidate = ex['block_duration_seconds'] + adjust
                if candidate >= 60:
                    ex['block_duration_seconds'] = candidate
                    ex['total_duration_seconds'] = candidate
                    total += adjust
                    difference -= adjust
                idx += 1
        return normalized, total

    def _rebalance_main_duration(self, exercises: List[Dict[str, Any]], target_seconds: int) -> int:
        """Adjust main exercise durations to better match target time."""
        if not exercises:
            return 0
        current = sum(ex.get('total_duration_seconds', 0) for ex in exercises) or 1
        if target_seconds <= 0:
            return current
        scale = target_seconds / current
        scale = max(0.75, min(scale, 1.25))
        if abs(scale - 1.0) > 0.05:
            for ex in exercises:
                new_block = max(60, int(round(ex['total_duration_seconds'] * scale)))
                ex['block_duration_seconds'] = new_block
                ex['total_duration_seconds'] = new_block
                if ex.get('is_time_based') and ex.get('work_seconds'):
                    ex['work_seconds'] = max(15, int(round(ex['work_seconds'] * scale)))
                    ex['duration'] = ex['work_seconds']
                    ex['duration_seconds_per_set'] = ex['work_seconds']
                else:
                    ex['duration'] = max(20, int(round(ex['duration'] * scale)))
                    ex['duration_seconds_per_set'] = ex['duration']
        current = sum(ex.get('total_duration_seconds', 0) for ex in exercises)
        difference = target_seconds - current
        idx = 0
        while exercises and abs(difference) > 0 and idx < len(exercises) * 2:
            ex = exercises[idx % len(exercises)]
            adjust = 1 if difference > 0 else -1
            candidate = ex['block_duration_seconds'] + adjust
            if candidate >= 60:
                ex['block_duration_seconds'] = candidate
                ex['total_duration_seconds'] = candidate
                difference -= adjust
                current += adjust
            idx += 1
        return current

    def get_agent_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available agents"""
        return {name: agent.get_agent_info() for name, agent in self.agents.items()}
    
    async def generate_workout(self, request: WorkoutGenerationRequest) -> OrchestrationResult:
        """Generate a comprehensive workout using multiple agents"""
        request_id = uuid4()
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting workout generation for request {request_id}")

            # Phase 1: Analyze user context and preferences
            context_analysis = await self._analyze_user_context(request)

            # Phase 2: Build macro time-budget plan
            macro_plan, plan_contribution = await self._generate_macro_plan(request, context_analysis)

            # Phase 3: Gather specialist contributions informed by the plan
            agent_contributions: List[AgentContribution] = []
            if plan_contribution:
                agent_contributions.append(plan_contribution)

            specialist_contributions = await self._gather_agent_contributions(request, context_analysis, macro_plan)
            agent_contributions.extend(specialist_contributions)

            # Phase 4: Synthesize contributions into final workout
            workout_response, general_contribution = await self._synthesize_workout(
                request,
                agent_contributions,
                macro_plan,
                context_analysis
            )
            if general_contribution:
                agent_contributions.append(general_contribution)

            # Phase 5: Validate and optimize final workout
            validated_workout = await self._validate_and_optimize(workout_response, request)

            execution_time = (datetime.now() - start_time).total_seconds()

            result = OrchestrationResult(
                request_id=request_id,
                workout_response=validated_workout,
                agent_contributions=agent_contributions,
                orchestration_metadata={
                    "context_analysis": context_analysis,
                    "macro_plan": macro_plan,
                    "agents_used": [contrib.agent_name for contrib in agent_contributions],
                    "synthesis_approach": "macro_plan_guided_multi_agent",
                    "validation_passed": True
                },
                total_execution_time=execution_time,
                success=True
            )

            self.request_history.append(result)
            logger.info(f"Workout generation completed successfully in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Workout generation failed: {str(e)}")
            
            return OrchestrationResult(
                request_id=request_id,
                workout_response=WorkoutGenerationResponse(
                    workout_id=uuid4(),
                    name="Error - Workout Generation Failed",
                    description="An error occurred during workout generation",
                    duration_minutes=0,
                    difficulty_level="unknown",
                    workout_type="error",
                    exercises=[],
                    warmup=[],
                    cooldown=[],
                    equipment_needed=[],
                    safety_notes=["Please try again or contact support"],
                    modifications={},
                    agent_attribution={}
                ),
                agent_contributions=[],
                orchestration_metadata={"error_details": str(e)},
                total_execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
    
    async def _analyze_user_context(self, request: WorkoutGenerationRequest) -> Dict[str, Any]:
        """Analyze user context using Preferences Manager and Analytics Expert"""
        context_tasks = []
        
        # Get preference analysis
        if 'preferences_manager' in self.agents:
            pref_task = self.agents['preferences_manager'].create_task(
                description=f"""
                Analyze user context and preferences for workout generation:
                - User Goals: {request.user_context.fitness_goals}
                - Experience Level: {request.user_context.experience_level}
                - Available Equipment: {request.user_context.available_equipment}
                - Time Constraints: {request.user_context.time_constraints}
                - Current Preferences: {request.user_context.preferences}
                """,
                expected_output="User context analysis with preference insights and personalization recommendations"
            )
            context_tasks.append(('preferences', pref_task))
        
        # Get analytics insights if user has history
        if 'analytics_expert' in self.agents and request.user_context.progress_history:
            analytics_task = self.agents['analytics_expert'].create_task(
                description=f"""
                Analyze user's fitness history and performance data:
                - Progress History: {request.user_context.progress_history}
                - Recent Sessions: {request.user_context.recent_sessions}
                - Current Program: {request.user_context.current_program}
                """,
                expected_output="Performance analysis with insights for workout optimization"
            )
            context_tasks.append(('analytics', analytics_task))
        
        # Execute context analysis tasks
        context_results = {}
        for task_name, task in context_tasks:
            try:
                if task_name == 'preferences':
                    result = self.agents['preferences_manager'].execute_task(task)
                elif task_name == 'analytics':
                    result = self.agents['analytics_expert'].execute_task(task)
                
                if result.success:
                    context_results[task_name] = result.result
                else:
                    logger.warning(f"Context analysis failed for {task_name}: {result.error_message}")
            except Exception as e:
                logger.warning(f"Error in context analysis for {task_name}: {str(e)}")
        
        return context_results
    
    async def _gather_agent_contributions(
        self,
        request: WorkoutGenerationRequest,
        context: Dict[str, Any],
        macro_plan: Dict[str, Any],
    ) -> List[AgentContribution]:
        """Gather contributions from relevant agents based on workout requirements"""
        contributions = []

        # Determine which agents to use based on workout type and goals
        relevant_agents = self._select_relevant_agents(request)
        
        # Create tasks for each relevant agent
        agent_tasks = []
        for agent_name in relevant_agents:
            if agent_name in self.agents:
                task = self._create_agent_task(agent_name, request, context, macro_plan)
                if task:
                    agent_tasks.append((agent_name, task))

        # Execute agent tasks
        for agent_name, task in agent_tasks:
            try:
                start_time = datetime.now()
                result = self.agents[agent_name].execute_task(task)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                if result.success:
                    contribution = AgentContribution(
                        agent_name=agent_name,
                        contribution_type=self._get_contribution_type(agent_name, request),
                        content=result.result,
                        confidence_score=0.8,  # Could be calculated based on various factors
                        execution_time=execution_time,
                        timestamp=datetime.now()
                    )
                    contributions.append(contribution)
                    logger.info(f"Got contribution from {agent_name} in {execution_time:.2f}s")
                else:
                    logger.warning(f"Agent {agent_name} failed: {result.error_message}")
                    
            except Exception as e:
                logger.error(f"Error getting contribution from {agent_name}: {str(e)}")
        
        return contributions
    
    def _select_relevant_agents(self, request: WorkoutGenerationRequest) -> List[str]:
        """Select relevant agents based on workout requirements"""
        relevant_agents = ['preferences_manager']  # Always include preferences
        
        # Add agents based on workout type
        if request.workout_type in ['strength', 'mixed']:
            relevant_agents.append('strength_coach')
        
        if request.workout_type in ['cardio', 'hiit', 'mixed']:
            relevant_agents.append('cardio_coach')
        
        # Always include equipment advisor for equipment optimization
        relevant_agents.append('equipment_advisor')
        
        # Include recovery specialist for longer workouts or advanced users
        if request.duration_minutes > 45 or request.user_context.experience_level == 'advanced':
            relevant_agents.append('recovery_specialist')
        
        # Include nutritionist for specific goals
        if any(goal in ['weight_loss', 'muscle_building'] for goal in request.user_context.fitness_goals):
            relevant_agents.append('nutritionist')
        
        # Include motivation coach for beginners or if user has consistency issues
        if request.user_context.experience_level == 'beginner':
            relevant_agents.append('motivation_coach')
        
        # Include analytics expert if user has history
        if request.user_context.progress_history:
            relevant_agents.append('analytics_expert')
        
        return relevant_agents
    
    def _create_agent_task(
        self,
        agent_name: str,
        request: WorkoutGenerationRequest,
        context: Dict[str, Any],
        macro_plan: Dict[str, Any],
    ) -> Optional[Task]:
        """Create appropriate task for specific agent"""
        if agent_name in {'program_director', 'general_coach'}:
            return None

        agent = self.agents[agent_name]
        phase_allocation = macro_plan.get('phase_allocation', {})
        main_blocks = macro_plan.get('main_blocks', [])
        warmup_focus = macro_plan.get('warmup_focus', [])
        cooldown_focus = macro_plan.get('cooldown_focus', [])
        special_requirements = ', '.join(request.special_requirements) or 'none'

        def _blocks_for_modalities(modalities: List[str]) -> List[Dict[str, Any]]:
            if not main_blocks:
                return []
            targets: List[Dict[str, Any]] = []
            modality_set = set(m.lower() for m in modalities)
            for block in main_blocks:
                modality = str(block.get('modality', '')).lower()
                if modality in modality_set or ('mixed' in modality_set and modality == 'mixed'):
                    targets.append(block)
            return targets

        if agent_name == 'strength_coach':
            json_instruction = self._format_json_instruction(
                """{
  "warmup": [
    {
      "name": string,
      "duration_seconds": int,
      "instructions": string,
      "coaching_cues": [string],
      "focus": string,
      "intensity": "light"|"moderate",
      "equipment": string|null
    }
  ],
  "exercises": [
    {
      "name": string,
      "sets": int,
      "reps": int|null,
      "work_seconds": int|null,
      "duration_seconds_per_set": int|null,
      "rest_seconds": int,
      "tempo": string|null,
      "equipment": string|null,
      "target_muscles": [string],
      "instructions": string,
      "coaching_cues": [string],
      "notes": string|null
    }
  ],
  "cooldown": [
    {
      "name": string,
      "duration_seconds": int,
      "instructions": string,
      "focus": string,
      "intensity": "light"|"moderate",
      "equipment": string|null
    }
  ],
  "safety_notes": [
    string
  ],
  "modifications": {
    "exercise_name": [
      {
        "description": string,
        "equipment": string|null,
        "impact": "low"|"moderate"|"high"|null
      }
    ]
  }
}
"""
            )
            plan_context = json.dumps({
                "phase_allocation": phase_allocation,
                "target_blocks": _blocks_for_modalities(['strength', 'mixed']),
                "warmup_focus": warmup_focus,
                "special_requirements": request.special_requirements,
            }, default=str)
            return agent.create_task(
                description=f"""
                Design strength training components for this workout:
                - Workout Type: {request.workout_type}
                - Duration: {request.duration_minutes} minutes
                - Difficulty: {request.difficulty_level}
                - Focus Areas: {request.focus_areas}
                - Available Equipment: {request.user_context.available_equipment}
                - User Experience: {request.user_context.experience_level}
                - Special Requirements: {special_requirements}

                Macro Plan Context (JSON):
                {plan_context}

                Requirements:
                - Build a warm-up of 4-6 dynamic mobility and activation drills (30-45 seconds each) with precise instructions and coaching cues that respect low-impact or low-noise constraints.
                - Program 6-8 main exercises spanning the full body. Provide sets x reps or timed work, rest between sets, target muscles, equipment, explicit instructions, and concise coaching cues for each movement.
                - Ensure movement selection honours low-impact/quiet constraints and defaults to bodyweight solutions when equipment is not listed.
                - Add 3-5 cooldown stretches or breathing drills (40-60 seconds each) describing focus areas and breathing cadence.
                - Express every timing value in seconds and avoid vague placeholders.

                {json_instruction}
                """,
                expected_output="Strength training exercises with sets, reps, rest, and coaching cues"
            )

        elif agent_name == 'cardio_coach':
            json_instruction = self._format_json_instruction(
                """{
  "cardio_exercises": [
    {
      "name": string,
      "duration_seconds": int,
      "sets": int,
      "rest_seconds": int,
      "intensity": "light"|"moderate"|"vigorous",
      "target_heart_rate_zone": string|null,
      "instructions": string,
      "coaching_cues": [string],
      "equipment": string|null,
      "impact_level": "low"|"moderate"|"high"
    }
  ],
  "intervals": [
    {
      "name": string,
      "work_interval_seconds": int,
      "rest_interval_seconds": int,
      "rounds": int,
      "intensity_focus": string,
      "instructions": string,
      "coaching_cues": [string]
    }
  ],
  "warmup": [
    {
      "name": string,
      "duration_seconds": int,
      "instructions": string,
      "coaching_cues": [string],
      "focus": string,
      "intensity": "light"|"moderate"
    }
  ],
  "cooldown": [
    {
      "name": string,
      "duration_seconds": int,
      "instructions": string,
      "focus": string,
      "intensity": "light"|"moderate"
    }
  ],
  "safety_notes": [
    string
  ],
  "modifications": {
    "exercise_name": [
      {
        "description": string,
        "equipment": string|null,
        "intensity_adjustment": string|null,
        "impact": "low"|"moderate"|"high"|null
      }
    ]
  }
}
"""
            )
            plan_context = json.dumps({
                "phase_allocation": phase_allocation,
                "target_blocks": _blocks_for_modalities(['cardio', 'mixed', 'hiit']),
                "special_requirements": request.special_requirements,
                "warmup_focus": warmup_focus,
                "cooldown_focus": cooldown_focus,
                "intensity_curve": macro_plan.get('intensity_curve', [])
            }, default=str)
            return agent.create_task(
                description=f"""
                Design cardiovascular training components for this workout:
                - Workout Type: {request.workout_type}
                - Duration: {request.duration_minutes} minutes
                - Intensity Level: {request.difficulty_level}
                - Available Equipment: {request.user_context.available_equipment}
                - Space Constraints: {request.user_context.space_constraints}

                Macro Plan Context (JSON):
                {plan_context}

                Requirements:
                - Provide a progressive warm-up of 4-5 quiet, low-impact drills (30-45 seconds each) with detailed instructions and cues.
                - Create 5-6 primary cardio or interval pieces with timing, rest, intensity, impact level, and coaching cues tailored to the requested difficulty.
                - Ensure intervals respect low-noise/low-impact constraints and rely only on supplied equipment (default to bodyweight locomotion otherwise).
                - Add 3-4 cooldown or breathing segments (40-60 seconds) with focus descriptions.
                - Express every timing value in seconds and avoid placeholders.

                {json_instruction}
                """,
                expected_output="Cardio exercises with intensity zones and timing recommendations"
            )

        elif agent_name == 'equipment_advisor':
            json_instruction = self._format_json_instruction(
                """{
  \"recommended_equipment\": [\"string\"],
  \"alternatives\": [
    {\"equipment\": \"string\", \"alternative\": \"string\", \"notes\": \"string|null\"}
  ],
  \"modifications\": {
    \"exercise_name\": [
      {\"description\": \"string\", \"equipment\": \"string|null\"}
    ]
  },
  \"safety_notes\": [\"string\"]
}"""
            )
            plan_context = json.dumps({
                "phase_allocation": phase_allocation,
                "main_blocks": main_blocks,
                "available_equipment": request.user_context.available_equipment,
                "space_constraints": request.user_context.space_constraints,
                "special_requirements": request.special_requirements
            }, default=str)
            return agent.create_task(
                description=f"""
                Optimize equipment usage and suggest alternatives:
                - Required Exercises: Based on workout type {request.workout_type}
                - Available Equipment: {request.user_context.available_equipment}
                - Space Constraints: {request.user_context.space_constraints}
                - Duration: {request.duration_minutes} minutes

                Macro Plan Context (JSON):
                {plan_context}

                {json_instruction}
                """,
                expected_output="Equipment optimization with alternatives and space-efficient solutions"
            )
        
        # Add similar task creation for other agents...
        return None
    
    def _get_contribution_type(self, agent_name: str, request: WorkoutGenerationRequest) -> str:
        """Get the type of contribution expected from each agent"""
        contribution_types = {
            'strength_coach': 'exercise_selection',
            'cardio_coach': 'cardio_programming',
            'nutritionist': 'nutrition_guidance',
            'equipment_advisor': 'equipment_optimization',
            'recovery_specialist': 'recovery_protocols',
            'motivation_coach': 'motivation_strategies',
            'analytics_expert': 'performance_insights',
            'preferences_manager': 'personalization'
        }
        return contribution_types.get(agent_name, 'general_contribution')
    
    async def _synthesize_workout(
        self,
        request: WorkoutGenerationRequest,
        contributions: List[AgentContribution],
        macro_plan: Dict[str, Any],
        context_analysis: Dict[str, Any],
    ) -> Tuple[WorkoutGenerationResponse, Optional[AgentContribution]]:
        """Synthesize agent contributions into final workout"""

        specialist_contributions = [
            contrib
            for contrib in contributions
            if contrib.agent_name not in {'general_coach', 'program_director'}
        ]
        payload_for_general = self._build_specialist_payload(
            specialist_contributions,
            macro_plan,
            context_analysis,
        )

        general_agent = self.agents.get('general_coach')
        general_contribution: Optional[AgentContribution] = None
        final_payload: Optional[Dict[str, Any]] = None

        if general_agent:
            start_time = datetime.now()
            general_result = general_agent.synthesize_workout(
                request=request,
                macro_plan=macro_plan,
                specialist_payload=payload_for_general,
            )
            if isinstance(general_result, dict) and not general_result.get('error'):
                final_payload = general_result
                general_contribution = AgentContribution(
                    agent_name='general_coach',
                    contribution_type='integration',
                    content=general_result,
                    confidence_score=0.9,
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    timestamp=datetime.now(),
                )
            else:
                logger.warning(
                    "General Coach returned invalid result; using fallback synthesis: %s",
                    general_result.get('error') if isinstance(general_result, dict) else general_result,
                )

        if not isinstance(final_payload, dict) or not final_payload:
            final_payload = self._fallback_structured_payload(
                request,
                macro_plan,
                specialist_contributions,
            )

        agent_attribution = {
            contrib.agent_name: contrib.contribution_type for contrib in specialist_contributions
        }
        if general_contribution:
            agent_attribution[general_contribution.agent_name] = general_contribution.contribution_type

        workout_response = self._build_workout_from_payload(
            request,
            macro_plan,
            final_payload,
            agent_attribution,
        )

        return workout_response, general_contribution

    def _build_specialist_payload(
        self,
        contributions: List[AgentContribution],
        macro_plan: Dict[str, Any],
        context_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            'macro_plan': macro_plan,
            'specialist_contributions': {},
            'context_analysis': context_analysis,
        }
        for contrib in contributions:
            payload['specialist_contributions'][contrib.agent_name] = contrib.content
        return payload

    def _fallback_structured_payload(
        self,
        request: WorkoutGenerationRequest,
        macro_plan: Dict[str, Any],
        contributions: List[AgentContribution],
    ) -> Dict[str, Any]:
        equipment_needed: set = set()
        safety_notes: List[str] = []
        modifications: Dict[str, Any] = {}
        warmup: List[Dict[str, Any]] = []
        cooldown: List[Dict[str, Any]] = []
        main: List[Dict[str, Any]] = []

        for contrib in contributions:
            content = contrib.content or {}
            if not isinstance(content, dict):
                continue

            warmup_items = content.get('warmup') or content.get('warm_up') or []
            cooldown_items = content.get('cooldown') or content.get('cool_down') or []
            if isinstance(warmup_items, list):
                warmup.extend(warmup_items)
            if isinstance(cooldown_items, list):
                cooldown.extend(cooldown_items)

            if contrib.agent_name == 'strength_coach' and isinstance(content.get('exercises'), list):
                main.extend(content['exercises'])

            if contrib.agent_name == 'cardio_coach':
                cardio_items = content.get('cardio_exercises') or []
                if isinstance(cardio_items, list):
                    for item in cardio_items:
                        main.append(dict(item))
                intervals = content.get('intervals') or []
                if isinstance(intervals, list):
                    for block in intervals:
                        main.append({
                            'name': block.get('name') or 'Interval Block',
                            'sets': block.get('rounds') or 1,
                            'work_seconds': block.get('work_interval_seconds'),
                            'duration_seconds_per_set': block.get('work_interval_seconds'),
                            'rest_seconds': block.get('rest_interval_seconds'),
                            'instructions': block.get('instructions'),
                            'coaching_cues': block.get('coaching_cues'),
                            'intensity': block.get('intensity_focus'),
                            'impact_level': block.get('impact'),
                            'notes': block.get('notes'),
                        })

            recommended = content.get('recommended_equipment') or content.get('equipment_needed') or []
            if isinstance(recommended, list):
                equipment_needed.update(recommended)

            if isinstance(content.get('safety_notes'), list):
                safety_notes.extend(content['safety_notes'])

            if isinstance(content.get('modifications'), dict):
                for key, value in content['modifications'].items():
                    if key not in modifications:
                        modifications[key] = value
                    else:
                        existing = modifications[key]
                        if isinstance(existing, list) and isinstance(value, list):
                            existing.extend(value)
                        else:
                            modifications[key] = value

        return {
            'warmup': warmup,
            'cooldown': cooldown,
            'main_workout': main,
            'safety_notes': safety_notes,
            'modifications': modifications,
            'equipment_needed': sorted({str(item).strip() for item in equipment_needed if item}),
            'coaching_overview': {
                'time_allocation_seconds': macro_plan.get('phase_allocation', {}),
                'summary': 'Fallback synthesis assembled from specialist outputs',
            },
        }

    def _build_workout_from_payload(
        self,
        request: WorkoutGenerationRequest,
        macro_plan: Dict[str, Any],
        payload: Dict[str, Any],
        agent_attribution: Dict[str, str],
    ) -> WorkoutGenerationResponse:
        phase_allocation = macro_plan.get('phase_allocation', {})
        warmup_target = self._parse_duration_value(phase_allocation.get('warmup'))
        main_target = self._parse_duration_value(phase_allocation.get('main'))
        cooldown_target = self._parse_duration_value(phase_allocation.get('cooldown'))

        normalized_warmup, warmup_total = self._normalize_phase_items(
            payload.get('warmup') or [],
            target_total=warmup_target,
        )
        if not normalized_warmup:
            raise ValueError("Warm-up phase missing from synthesis")
        normalized_cooldown, cooldown_total = self._normalize_phase_items(
            payload.get('cooldown') or [],
            target_total=cooldown_target,
        )
        if not normalized_cooldown:
            raise ValueError("Cooldown phase missing from synthesis")
        normalized_main, main_total = self._normalize_main_exercises(
            payload.get('main_workout') or [],
            request,
            target_total=main_target,
        )
        if not normalized_main:
            raise ValueError("Main workout phase missing from synthesis")

        if normalized_main:
            desired_main = main_target or sum(ex['total_duration_seconds'] for ex in normalized_main)
            main_total = self._rebalance_main_duration(normalized_main, desired_main)

        total_estimated = warmup_total + main_total + cooldown_total
        if not warmup_target:
            warmup_target = warmup_total
        if not cooldown_target:
            cooldown_target = cooldown_total
        if not main_target:
            main_target = main_total

        phase_breakdown = {
            'warmup': warmup_target,
            'main': main_target,
            'cooldown': cooldown_target,
        }

        safety_notes = list(dict.fromkeys(payload.get('safety_notes') or []))
        modifications = self._normalize_modifications(payload.get('modifications') or {})
        equipment_needed = payload.get('equipment_needed')
        if not equipment_needed:
            equipment_needed = sorted({
                ex.get('equipment', 'bodyweight') for ex in normalized_main if ex.get('equipment')
            })

        overview = payload.get('coaching_overview') or {}
        summary_text = overview.get('summary') if isinstance(overview, dict) else None

        workout = WorkoutGenerationResponse(
            workout_id=uuid4(),
            name=f"AI-Generated {request.workout_type.title()} Workout",
            description=summary_text or f"Personalized {request.duration_minutes}-minute {request.workout_type} workout",
            duration_minutes=max(request.duration_minutes, int(round(total_estimated / 60))) if total_estimated else request.duration_minutes,
            difficulty_level=request.difficulty_level,
            workout_type=request.workout_type,
            exercises=normalized_main,
            warmup=normalized_warmup,
            cooldown=normalized_cooldown,
            equipment_needed=equipment_needed,
            safety_notes=safety_notes,
            modifications=modifications,
            estimated_calories=self._estimate_calories(request.duration_minutes, request.difficulty_level),
            total_estimated_duration_seconds=total_estimated,
            phase_duration_breakdown=phase_breakdown,
            agent_attribution=agent_attribution,
        )

        if isinstance(overview, dict):
            workout.modifications.setdefault('_session_overview', []).append(overview)

        return workout

    def _normalize_modifications(self, modifications: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        normalized: Dict[str, List[Dict[str, Any]]] = {}
        for key, value in modifications.items():
            if isinstance(value, dict):
                normalized[key] = [value]
            elif isinstance(value, list):
                normalized[key] = []
                for item in value:
                    if isinstance(item, dict):
                        normalized[key].append(item)
                    else:
                        normalized[key].append({'description': str(item), 'equipment': None, 'impact': None})
            else:
                normalized[key] = [{'description': str(value), 'equipment': None, 'impact': None}]
        return normalized

    async def _validate_and_optimize(self, workout: WorkoutGenerationResponse, request: WorkoutGenerationRequest) -> WorkoutGenerationResponse:
        """Validate and optimize the final workout"""
        # Basic validation and optimization
        
        # Ensure workout duration metadata is consistent

        if workout.phase_duration_breakdown:

            workout.total_estimated_duration_seconds = sum(workout.phase_duration_breakdown.values())

        elif workout.total_estimated_duration_seconds is None:

            warmup_total = sum(item.get('duration', 0) for item in workout.warmup)

            main_total = sum(ex.get('total_duration_seconds', ex.get('duration', 0)) for ex in workout.exercises)

            cooldown_total = sum(item.get('duration', 0) for item in workout.cooldown)

            workout.total_estimated_duration_seconds = warmup_total + main_total + cooldown_total

            workout.phase_duration_breakdown = {

                'warmup': warmup_total,

                'main': main_total,

                'cooldown': cooldown_total

            }



        if workout.total_estimated_duration_seconds and workout.total_estimated_duration_seconds > 0:

            computed_minutes = max(1, int(round(workout.total_estimated_duration_seconds / 60)))

            workout.duration_minutes = max(request.duration_minutes, computed_minutes) if request.duration_minutes else computed_minutes



        # Ensure equipment is available

        available_equipment = [eq.get('name', '').lower() for eq in request.user_context.available_equipment]

        workout.equipment_needed = [eq for eq in workout.equipment_needed if eq.lower() in available_equipment or eq.lower() == 'bodyweight']



        return workout
    
    def _estimate_calories(self, duration: int, difficulty: str) -> int:
        """Estimate calories burned based on duration and difficulty"""
        base_rate = {"beginner": 6, "intermediate": 8, "advanced": 10}
        rate = base_rate.get(difficulty, 7)
        return duration * rate
    
    def get_orchestration_history(self, limit: int = 10) -> List[OrchestrationResult]:
        """Get recent orchestration history"""
        return self.request_history[-limit:]
    
    def get_agent_performance_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for each agent"""
        stats = {}
        
        for result in self.request_history:
            for contrib in result.agent_contributions:
                agent_name = contrib.agent_name
                if agent_name not in stats:
                    stats[agent_name] = {
                        'total_contributions': 0,
                        'avg_execution_time': 0,
                        'avg_confidence': 0,
                        'contribution_types': set()
                    }
                
                stats[agent_name]['total_contributions'] += 1
                stats[agent_name]['avg_execution_time'] = (
                    stats[agent_name]['avg_execution_time'] + contrib.execution_time
                ) / 2
                stats[agent_name]['avg_confidence'] = (
                    stats[agent_name]['avg_confidence'] + contrib.confidence_score
                ) / 2
                stats[agent_name]['contribution_types'].add(contrib.contribution_type)
        
        # Convert sets to lists for JSON serialization
        for agent_stats in stats.values():
            agent_stats['contribution_types'] = list(agent_stats['contribution_types'])
        
        return stats
