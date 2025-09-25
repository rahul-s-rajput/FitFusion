"""
Program Director agent for FitFusion AI Workout App.
Designs high-level workout blueprints with time allocation and focus planning.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field

from .base_agent import BaseAgent, AgentConfig, WorkoutGenerationRequest, FitnessContext


class MacroPlanResponse(BaseModel):
    """Schema for macro workout plan produced by Program Director"""

    phase_allocation: Dict[str, int] = Field(..., description="Seconds allocated to each workout phase")
    warmup_focus: List[str] = Field(default_factory=list)
    main_blocks: List[Dict[str, Any]] = Field(default_factory=list)
    cooldown_focus: List[str] = Field(default_factory=list)
    intensity_curve: List[Dict[str, Any]] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class ProgramDirector(BaseAgent):
    """Agent responsible for creating macro workout plans and time budgets"""

    def __init__(self, llm_config: Dict[str, Any]):
        config = AgentConfig(
            name="Program Director",
            role="Master Program Designer",
            goal="Translate user preferences and constraints into a time-budgeted, science-backed workout blueprint",
            backstory="""
You are a veteran head coach and periodization expert who orchestrates world-class training programs.
You interpret athlete profiles, environmental constraints, and tactical needs to build precise session blueprints.
You assign exact time budgets to warm-up, main work, and cooldown phases, and determine the sequence of
focus blocks (mobility, strength, cardio, recovery) that will deliver the intended adaptive stimulus while
respecting safety, equipment availability, and user preferences (impact, noise, space, scheduling).

You collaborate with specialist coaches, so your output must be actionable: clear durations, targeted muscle
groups, intensity prescriptions, rest expectations, and rationale for each block so downstream specialists can
fill in exercise specifics without ambiguity.
""",
            tools=[],
            max_iter=6,
            allow_delegation=False,
            verbose=False,
        )
        super().__init__(config, llm_config)

    def _get_tools(self) -> List[Any]:
        """Program Director operates without additional tools."""
        return []

    def get_specialized_prompts(self) -> Dict[str, str]:
        return {
            "macro_plan": """
You receive the total session duration, user profile, preferences, equipment, and special requirements.
Allocate exact seconds to warm-up, main work, and cooldown phases (they must sum exactly to the session total).
Divide the main phase into 2-4 focused blocks that collectively cover full-body training unless the user
explicitly requests otherwise. Specify for each block: focus areas, training modality (strength / cardio / mobility / core),
intended adaptation (e.g., hypertrophy, metabolic conditioning, stability), recommended set/rep or interval structure,
target intensity (RPE or % effort), expected rest windows, and impact/noise guidelines.

Respect constraints: low-impact, low-noise, minimal equipment, and available equipment list. Recommend safe
progression within the user's difficulty. Provide warm-up themes (mobility, activation) and cooldown focuses
(down-regulation, stretching) with suggested segment counts.

Respond with strict JSON using this schema:
{
  "phase_allocation": {
    "warmup": int,  // seconds
    "main": int,
    "cooldown": int
  },
  "warmup_focus": [string],
  "main_blocks": [
    {
      "name": string,
      "focus_areas": [string],
      "modality": "strength"|"cardio"|"mobility"|"core"|"balance"|"mixed",
      "duration_seconds": int,
      "sets": int|null,
      "rep_scheme": string|null,
      "interval_style": string|null,
      "target_intensity": string,
      "rest_seconds": int,
      "impact_level": "low"|"moderate"|"high",
      "equipment_bias": string,
      "coaching_priority": string
    }
  ],
  "cooldown_focus": [string],
  "intensity_curve": [
    {
      "phase": string,
      "average_rpe": float,
      "notes": string
    }
  ],
  "notes": [string]
}

- The sum of warmup + main + cooldown MUST equal the total session seconds.
- The sum of all main block durations MUST equal the main phase seconds.
- For low-impact or low-noise requests, mark impact_level="low" and choose appropriate modalities.
- When no equipment is available, set equipment_bias="bodyweight".
"""
        }

    def design_macro_plan(self, request: WorkoutGenerationRequest) -> Dict[str, Any]:
        context = request.user_context
        prompt = self.get_specialized_prompts()["macro_plan"]
        task_description = f"""
{prompt}

Session Parameters:
- Total Duration: {request.duration_minutes} minutes
- Difficulty: {request.difficulty_level}
- Workout Type: {request.workout_type}
- Focus Areas: {request.focus_areas}
- Special Requirements: {request.special_requirements}

User Context:
- Experience Level: {context.experience_level}
- Fitness Goals: {context.fitness_goals}
- Available Equipment: {context.available_equipment}
- Space Constraints: {context.space_constraints}
- Preferences: {context.preferences}
- Time Constraints: {context.time_constraints}
"""

        task = self.create_task(
            description=task_description,
            expected_output="Structured JSON macro plan with exact time allocations and block definitions",
        )

        result = self.execute_task(task)
        if result.success and isinstance(result.result, dict):
            return result.result
        return {"error": result.error_message or "Unable to design macro plan"}
