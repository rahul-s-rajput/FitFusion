"""
Strength Coach agent for FitFusion AI Workout App.
Specializes in strength training, progressive overload, and muscle building.
"""

import json
from typing import Dict, Any, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .base_agent import BaseAgent, AgentConfig, FitnessContext, WorkoutGenerationRequest




def _normalize_tool_input(value: Any) -> str:
    """Convert tool arguments to JSON strings CrewAI tools accept."""
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, default=str)
    except TypeError:
        return str(value)


class StrengthAnalysisTool(BaseTool):
    """Tool for analyzing strength training requirements"""
    name: str = "strength_analysis"
    description: str = "Analyze user's strength training needs and create progressive workout plans"
    
    def _run(self, user_context: Any, workout_requirements: Any) -> str:
        """Analyze strength training requirements"""
        context_str = _normalize_tool_input(user_context)
        requirements_str = _normalize_tool_input(workout_requirements)
        return f"Strength analysis completed for requirements: {requirements_str}"


class ProgressiveOverloadTool(BaseTool):
    """Tool for calculating progressive overload"""
    name: str = "progressive_overload"
    description: str = "Calculate progressive overload for strength training exercises"
    
    def _run(self, current_weights: Any, target_progression: Any) -> str:
        """Calculate progressive overload progression"""
        weights_str = _normalize_tool_input(current_weights)
        progression_str = _normalize_tool_input(target_progression)
        return f"Progressive overload calculated: {progression_str}"


class MuscleGroupBalanceTool(BaseTool):
    """Tool for ensuring balanced muscle group development"""
    name: str = "muscle_balance"
    description: str = "Analyze and ensure balanced muscle group development"
    
    def _run(self, workout_plan: Any, muscle_groups: Any) -> str:
        """Analyze muscle group balance"""
        plan_str = _normalize_tool_input(workout_plan)
        groups_str = _normalize_tool_input(muscle_groups)
        return f"Muscle balance analysis: {groups_str}"


class StrengthCoach(BaseAgent):
    """AI agent specializing in strength training and muscle building"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        config = AgentConfig(
            name="Strength Coach",
            role="Expert Strength Training Coach",
            goal="Design effective strength training programs that build muscle, increase power, and improve functional strength while preventing injury",
            backstory="""You are a certified strength and conditioning specialist with 15+ years of experience 
            training athletes and fitness enthusiasts. You specialize in progressive overload principles, 
            compound movement patterns, and evidence-based strength training methodologies. You understand 
            biomechanics, muscle physiology, and how to adapt programs for different experience levels and goals.
            
            Your expertise includes:
            - Progressive overload programming
            - Compound movement selection and progression
            - Muscle group balancing and periodization
            - Strength assessment and goal setting
            - Injury prevention through proper form and loading
            - Equipment adaptation and exercise modifications
            
            You always prioritize safety, proper form, and sustainable progression over quick gains.""",
            tools=["strength_analysis", "progressive_overload", "muscle_balance"],
            max_iter=7,
            allow_delegation=True
        )
        super().__init__(config, llm_config)
    
    def _get_tools(self) -> List[BaseTool]:
        """Get strength coaching specific tools"""
        return [
            StrengthAnalysisTool(),
            ProgressiveOverloadTool(),
            MuscleGroupBalanceTool()
        ]
    
    def get_specialized_prompts(self) -> Dict[str, str]:
        """Get strength coaching specialized prompts"""
        return {
            "strength_assessment": """
            Assess the user's current strength level and create a baseline evaluation.
            Consider their experience level, available equipment, and strength goals.
            Provide specific recommendations for starting weights and progression rates.
            """,
            
            "program_design": """
            Design a comprehensive strength training program based on the user's goals and constraints.
            Include:
            - Primary compound movements (squat, deadlift, press, pull patterns)
            - Accessory exercises for muscle balance
            - Progressive overload scheme
            - Deload and recovery protocols
            - Exercise modifications for available equipment
            """,
            
            "exercise_selection": """
            Select appropriate strength training exercises based on:
            - User's experience level and mobility
            - Available equipment and space
            - Target muscle groups and movement patterns
            - Time constraints and workout frequency
            Prioritize compound movements and functional strength patterns.
            """,
            
            "progression_planning": """
            Create a detailed progression plan for strength development:
            - Weekly/monthly progression targets
            - Load progression (weight, reps, sets)
            - Movement complexity progression
            - Periodization for long-term gains
            - Plateau-breaking strategies
            """,
            
            "form_coaching": """
            Provide detailed form cues and safety instructions for strength exercises:
            - Setup and positioning
            - Movement execution
            - Breathing patterns
            - Common mistakes to avoid
            - Injury prevention tips
            """,
            
            "equipment_adaptation": """
            Adapt strength training exercises for available equipment:
            - Bodyweight alternatives to weighted exercises
            - Resistance band substitutions
            - Home gym equipment modifications
            - Creative solutions for limited equipment
            """
        }
    
    def assess_strength_level(self, context: FitnessContext) -> Dict[str, Any]:
        """Assess user's current strength level"""
        prompt = self.get_specialized_prompts()["strength_assessment"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Context:
            - Experience Level: {context.experience_level}
            - Fitness Goals: {context.fitness_goals}
            - Available Equipment: {context.available_equipment}
            - Physical Attributes: {context.physical_attributes}
            - Recent Sessions: {context.recent_sessions}
            """,
            expected_output="Detailed strength assessment with baseline recommendations and progression rates"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def design_strength_program(self, request: WorkoutGenerationRequest) -> Dict[str, Any]:
        """Design a comprehensive strength training program"""
        prompt = self.get_specialized_prompts()["program_design"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Workout Requirements:
            - Workout Type: {request.workout_type}
            - Duration: {request.duration_minutes} minutes
            - Difficulty: {request.difficulty_level}
            - Focus Areas: {request.focus_areas}
            - Equipment: {request.user_context.available_equipment}
            - Experience: {request.user_context.experience_level}
            - Goals: {request.user_context.fitness_goals}
            """,
            expected_output="Complete strength training program with exercises, sets, reps, and progression plan"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def select_strength_exercises(self, context: FitnessContext, focus_areas: List[str]) -> Dict[str, Any]:
        """Select appropriate strength exercises"""
        prompt = self.get_specialized_prompts()["exercise_selection"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Focus Areas: {focus_areas}
            Available Equipment: {context.available_equipment}
            Experience Level: {context.experience_level}
            Space Constraints: {context.space_constraints}
            Time Constraints: {context.time_constraints}
            """,
            expected_output="List of selected exercises with rationale and modifications"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def create_progression_plan(self, current_program: Dict[str, Any], user_progress: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create detailed progression plan"""
        prompt = self.get_specialized_prompts()["progression_planning"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Current Program: {current_program}
            Progress History: {user_progress}
            """,
            expected_output="Detailed progression plan with targets and periodization"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def provide_form_coaching(self, exercise_name: str, user_experience: str) -> Dict[str, Any]:
        """Provide form coaching for specific exercises"""
        prompt = self.get_specialized_prompts()["form_coaching"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Exercise: {exercise_name}
            User Experience Level: {user_experience}
            """,
            expected_output="Detailed form coaching with cues and safety tips"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def adapt_for_equipment(self, exercises: List[str], available_equipment: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Adapt exercises for available equipment"""
        prompt = self.get_specialized_prompts()["equipment_adaptation"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Target Exercises: {exercises}
            Available Equipment: {available_equipment}
            """,
            expected_output="Equipment-adapted exercise alternatives with instructions"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}


class StrengthWorkoutRequest(BaseModel):
    """Specific request for strength workout generation"""
    base_request: WorkoutGenerationRequest
    strength_focus: str = Field(..., description="Primary strength focus: power, hypertrophy, endurance, or mixed")
    target_muscle_groups: List[str] = Field(..., description="Specific muscle groups to target")
    current_maxes: Dict[str, float] = Field(default_factory=dict, description="Current 1RM or working weights")
    progression_preference: str = Field("linear", description="Progression type: linear, undulating, or block")
    compound_focus: bool = Field(True, description="Prioritize compound movements")
    
    
class StrengthWorkoutResponse(BaseModel):
    """Response from strength workout generation"""
    workout_structure: Dict[str, Any]
    exercise_details: List[Dict[str, Any]]
    progression_notes: str
    form_cues: Dict[str, List[str]]
    safety_considerations: List[str]
    next_session_recommendations: str
