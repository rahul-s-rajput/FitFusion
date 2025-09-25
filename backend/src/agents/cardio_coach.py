"""
Cardio Coach agent for FitFusion AI Workout App.
Specializes in cardiovascular training, endurance building, and heart rate optimization.
"""

from typing import Dict, Any, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .base_agent import BaseAgent, AgentConfig, FitnessContext, WorkoutGenerationRequest


class HeartRateZoneTool(BaseTool):
    """Tool for calculating heart rate zones and training intensities"""
    name: str = "heart_rate_zones"
    description: str = "Calculate personalized heart rate zones for optimal cardio training"
    
    def _run(self, age: str, resting_hr: str, fitness_level: str) -> str:
        """Calculate heart rate zones"""
        return f"Heart rate zones calculated for age {age}, RHR {resting_hr}, fitness level {fitness_level}"


class EnduranceAnalysisTool(BaseTool):
    """Tool for analyzing endurance capacity and progression"""
    name: str = "endurance_analysis"
    description: str = "Analyze current endurance capacity and create progression plans"
    
    def _run(self, current_capacity: str, goals: str) -> str:
        """Analyze endurance capacity"""
        return f"Endurance analysis completed: {current_capacity} -> {goals}"


class IntervalDesignTool(BaseTool):
    """Tool for designing interval training protocols"""
    name: str = "interval_design"
    description: str = "Design effective interval training protocols for various fitness goals"
    
    def _run(self, workout_type: str, duration: str, intensity: str) -> str:
        """Design interval protocols"""
        return f"Interval protocol designed: {workout_type}, {duration}, {intensity}"


class CardioCoach(BaseAgent):
    """AI agent specializing in cardiovascular training and endurance"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        config = AgentConfig(
            name="Cardio Coach",
            role="Expert Cardiovascular Training Specialist",
            goal="Design effective cardiovascular training programs that improve heart health, endurance, and metabolic fitness while optimizing training zones and recovery",
            backstory="""You are a certified exercise physiologist and endurance coach with extensive experience 
            in cardiovascular training across all fitness levels. You specialize in heart rate-based training, 
            interval protocols, and endurance periodization. Your expertise spans from rehabilitation cardio 
            to elite endurance performance.
            
            Your expertise includes:
            - Heart rate zone training and monitoring
            - Interval training design (HIIT, LISS, Tabata, etc.)
            - Endurance periodization and base building
            - Metabolic conditioning and fat burning
            - Cardio equipment optimization and alternatives
            - Recovery and adaptation monitoring
            - Sport-specific cardio conditioning
            
            You understand the importance of progressive overload in cardio, proper intensity distribution, 
            and how to balance different energy systems for optimal results.""",
            tools=["heart_rate_zones", "endurance_analysis", "interval_design"],
            max_iter=6,
            allow_delegation=True
        )
        super().__init__(config, llm_config)
    
    def _get_tools(self) -> List[BaseTool]:
        """Get cardio coaching specific tools"""
        return [
            HeartRateZoneTool(),
            EnduranceAnalysisTool(),
            IntervalDesignTool()
        ]
    
    def get_specialized_prompts(self) -> Dict[str, str]:
        """Get cardio coaching specialized prompts"""
        return {
            "endurance_assessment": """
            Assess the user's current cardiovascular fitness level and endurance capacity.
            Consider their exercise history, current activity level, and cardiovascular goals.
            Provide baseline recommendations for training zones and progression rates.
            """,
            
            "cardio_program_design": """
            Design a comprehensive cardiovascular training program based on user goals:
            - Heart rate zone distribution
            - Workout frequency and duration
            - Intensity progression
            - Recovery protocols
            - Equipment-specific adaptations
            Balance different training modalities for optimal adaptation.
            """,
            
            "interval_programming": """
            Create effective interval training protocols:
            - Work-to-rest ratios
            - Intensity targets (HR zones, RPE, pace)
            - Progression schemes
            - Recovery intervals
            - Session structure and timing
            Adapt for user's fitness level and available time.
            """,
            
            "heart_rate_optimization": """
            Optimize training based on heart rate data and zones:
            - Calculate personalized HR zones
            - Intensity distribution recommendations
            - Training load management
            - Adaptation monitoring
            - Zone-specific benefits and applications
            """,
            
            "equipment_cardio": """
            Adapt cardio training for available equipment and space:
            - Bodyweight cardio alternatives
            - Home equipment optimization
            - Outdoor vs indoor adaptations
            - Equipment-free HIIT protocols
            - Space-efficient cardio solutions
            """,
            
            "metabolic_conditioning": """
            Design metabolic conditioning workouts:
            - Energy system targeting
            - Circuit training protocols
            - Metabolic finishers
            - Fat burning optimization
            - Performance-based conditioning
            """
        }
    
    def assess_cardio_fitness(self, context: FitnessContext) -> Dict[str, Any]:
        """Assess user's cardiovascular fitness level"""
        prompt = self.get_specialized_prompts()["endurance_assessment"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Context:
            - Experience Level: {context.experience_level}
            - Fitness Goals: {context.fitness_goals}
            - Physical Attributes: {context.physical_attributes}
            - Recent Cardio Sessions: {context.recent_sessions}
            - Available Equipment: {context.available_equipment}
            """,
            expected_output="Comprehensive cardio fitness assessment with training zone recommendations"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def design_cardio_program(self, request: WorkoutGenerationRequest) -> Dict[str, Any]:
        """Design a comprehensive cardio training program"""
        prompt = self.get_specialized_prompts()["cardio_program_design"]
        
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
            - Time Constraints: {request.user_context.time_constraints}
            """,
            expected_output="Complete cardio program with heart rate zones, intervals, and progression"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def create_interval_workout(self, context: FitnessContext, interval_type: str, duration: int) -> Dict[str, Any]:
        """Create specific interval training workout"""
        prompt = self.get_specialized_prompts()["interval_programming"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Interval Type: {interval_type}
            Duration: {duration} minutes
            Fitness Level: {context.experience_level}
            Available Equipment: {context.available_equipment}
            Space Constraints: {context.space_constraints}
            """,
            expected_output="Detailed interval workout with timing, intensity, and recovery protocols"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def optimize_heart_rate_training(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize training based on heart rate data"""
        prompt = self.get_specialized_prompts()["heart_rate_optimization"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Data: {user_data}
            """,
            expected_output="Heart rate zone optimization with training recommendations"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def adapt_cardio_for_equipment(self, cardio_goals: List[str], available_equipment: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Adapt cardio training for available equipment"""
        prompt = self.get_specialized_prompts()["equipment_cardio"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Cardio Goals: {cardio_goals}
            Available Equipment: {available_equipment}
            """,
            expected_output="Equipment-adapted cardio workouts with alternatives"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def design_metabolic_workout(self, context: FitnessContext, focus: str) -> Dict[str, Any]:
        """Design metabolic conditioning workout"""
        prompt = self.get_specialized_prompts()["metabolic_conditioning"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Metabolic Focus: {focus}
            Fitness Level: {context.experience_level}
            Duration: {context.time_constraints}
            Equipment: {context.available_equipment}
            """,
            expected_output="Metabolic conditioning workout with energy system targeting"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}


class CardioWorkoutRequest(BaseModel):
    """Specific request for cardio workout generation"""
    base_request: WorkoutGenerationRequest
    cardio_type: str = Field(..., description="Type: HIIT, LISS, Tabata, circuit, steady_state")
    target_hr_zone: str = Field("moderate", description="Target heart rate zone")
    interval_preference: str = Field("mixed", description="Interval preference: short, long, mixed")
    equipment_preference: List[str] = Field(default_factory=list, description="Preferred cardio equipment")
    outdoor_option: bool = Field(False, description="Include outdoor cardio options")
    
    
class CardioWorkoutResponse(BaseModel):
    """Response from cardio workout generation"""
    workout_structure: Dict[str, Any]
    heart_rate_zones: Dict[str, int]
    interval_protocols: List[Dict[str, Any]]
    equipment_alternatives: List[str]
    progression_plan: str
    recovery_recommendations: str
