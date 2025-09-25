"""
General Coach agent for FitFusion AI Workout App.
Synthesizes specialist contributions into a cohesive, elite-level workout session.
"""

import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from .base_agent import BaseAgent, AgentConfig, WorkoutGenerationRequest


class FinalWorkoutResponse(BaseModel):
    """Schema for the final workout assembled by the general coach"""

    warmup: List[Dict[str, Any]] = Field(default_factory=list)
    main_workout: List[Dict[str, Any]] = Field(default_factory=list)
    cooldown: List[Dict[str, Any]] = Field(default_factory=list)
    safety_notes: List[str] = Field(default_factory=list)
    modifications: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    coaching_overview: Dict[str, Any] = Field(default_factory=dict)


class GeneralCoach(BaseAgent):
    """Agent that integrates plans and specialist input into final workout schema"""

    def __init__(self, llm_config: Dict[str, Any]):
        config = AgentConfig(
            name="General Coach",
            role="Elite Head Coach",
            goal="Deliver a cohesive, science-backed workout honoring time budgets, preferences, and specialist insights",
            backstory="""
You are the veteran head coach who leads a team of specialist coaches. You receive a detailed macro plan with
time allocations plus raw recommendations from strength, cardio, recovery, and equipment experts. Your job is to
assemble an airtight workout that feels like it was built by a world-class personal trainer who knows the athlete
intimately.

You reconcile overlaps, enforce the phase time budgets exactly, and ensure the sequence flows logically with
progressive intensity and safe transitions. You include precise instructions and coaching cues that make every
exercise feel coached in-person, respect low-impact/noise constraints, highlight rest intervals, and cover full-body
training unless directed otherwise.
""",
            tools=[],
            max_iter=7,
            allow_delegation=False,
            verbose=False,
        )
        super().__init__(config, llm_config)

    def _get_tools(self) -> List[Any]:
        """General Coach aggregates without external tools."""
        return []

    def get_specialized_prompts(self) -> Dict[str, str]:
        return {
            "synthesize": """
You receive:
1. A macro plan with phase time allocations and block intentions.
2. Specialist contributions detailing candidate warm-ups, main exercises, cardio intervals, cooldown moves, equipment guidance, and safety notes.
3. User profile with preferences (impact/noise, equipment limits, experience).

Produce the final workout JSON with this schema:
{
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
  "main_workout": [
    {
      "name": string,
      "sets": int,
      "reps": int|null,
      "work_seconds": int|null,
      "rest_seconds": int,
      "target_muscles": [string],
      "intensity": string,
      "impact_level": "low"|"moderate"|"high",
      "equipment": string,
      "instructions": string,
      "coaching_cues": [string],
      "block_duration_seconds": int
    }
  ],
  "cooldown": [
    {
      "name": string,
      "duration_seconds": int,
      "instructions": string,
      "coaching_cues": [string],
      "focus": string,
      "intensity": "light",
      "equipment": string|null
    }
  ],
  "safety_notes": [string],
  "modifications": {
    "exercise_name": [
      {
        "description": string,
        "equipment": string|null,
        "impact": "low"|"moderate"|"high"|null
      }
    ]
  },
  "coaching_overview": {
    "time_allocation_seconds": {
      "warmup": int,
      "main": int,
      "cooldown": int
    },
    "training_goals": [string],
    "intensity_curve": [
      {
        "phase": string,
        "average_rpe": float,
        "notes": string
      }
    ],
    "summary": string
  }
}

Rules:
- Total warmup duration must equal the macro plan warmup seconds.
- Total cooldown duration must equal macro plan cooldown seconds.
- Sum of block_duration_seconds for main_workout entries must equal macro plan main seconds.
- For each main exercise: if work_seconds is provided (time-based), set reps=null. If reps are provided, set work_seconds=null.
- Always provide rest_seconds (minimum 20s) and ensure transitions respect low-impact/low-noise requirements.
- Prioritize bodyweight options when equipment list is empty.
- Merge specialist notes into safety_notes and modifications, removing duplicates.
- Ensure coaching cues are concise, actionable, and 3-6 words each.
"""
        }

    def synthesize_workout(self, *,
                            request: WorkoutGenerationRequest,
                            macro_plan: Dict[str, Any],
                            specialist_payload: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self.get_specialized_prompts()["synthesize"]

        context_blob = json.dumps(specialist_payload, default=str)
        plan_blob = json.dumps(macro_plan, default=str)

        task_description = f"""
{prompt}

User Profile:
- Difficulty: {request.difficulty_level}
- Experience: {request.user_context.experience_level}
- Fitness Goals: {request.user_context.fitness_goals}
- Special Requirements: {request.special_requirements}
- Available Equipment: {request.user_context.available_equipment}
- Preferences: {request.user_context.preferences}

Macro Plan JSON:
{plan_blob}

Specialist Contributions JSON:
{context_blob}
"""

        task = self.create_task(
            description=task_description,
            expected_output="Final workout JSON following the prescribed schema",
        )

        result = self.execute_task(task)
        if result.success and isinstance(result.result, dict):
            return result.result
        return {"error": result.error_message or "Unable to synthesize workout"}
