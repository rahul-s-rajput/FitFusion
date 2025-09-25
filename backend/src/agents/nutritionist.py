"""
Nutritionist agent for FitFusion AI Workout App.
Specializes in nutrition planning, meal timing, and dietary recommendations for fitness goals.
"""

from typing import Dict, Any, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .base_agent import BaseAgent, AgentConfig, FitnessContext, WorkoutGenerationRequest


class MacroCalculatorTool(BaseTool):
    """Tool for calculating macronutrient requirements"""
    name: str = "macro_calculator"
    description: str = "Calculate personalized macronutrient requirements based on goals and activity"
    
    def _run(self, user_stats: str, activity_level: str, goals: str) -> str:
        """Calculate macro requirements"""
        return f"Macros calculated for {user_stats}, activity: {activity_level}, goals: {goals}"


class MealTimingTool(BaseTool):
    """Tool for optimizing meal timing around workouts"""
    name: str = "meal_timing"
    description: str = "Optimize meal timing for workout performance and recovery"
    
    def _run(self, workout_schedule: str, meal_preferences: str) -> str:
        """Optimize meal timing"""
        return f"Meal timing optimized for schedule: {workout_schedule}"


class SupplementGuidanceTool(BaseTool):
    """Tool for providing evidence-based supplement recommendations"""
    name: str = "supplement_guidance"
    description: str = "Provide evidence-based supplement recommendations for fitness goals"
    
    def _run(self, goals: str, diet_restrictions: str, budget: str) -> str:
        """Provide supplement guidance"""
        return f"Supplement recommendations for {goals} with restrictions: {diet_restrictions}"


class Nutritionist(BaseAgent):
    """AI agent specializing in nutrition and dietary planning for fitness"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        config = AgentConfig(
            name="Nutritionist",
            role="Certified Sports Nutritionist",
            goal="Provide evidence-based nutrition guidance that supports fitness goals, optimizes performance, and promotes long-term health through sustainable dietary practices",
            backstory="""You are a registered dietitian and certified sports nutritionist with expertise in 
            performance nutrition, body composition, and metabolic health. You understand how nutrition 
            impacts exercise performance, recovery, and adaptation. Your approach is evidence-based, 
            practical, and focused on sustainable lifestyle changes.
            
            Your expertise includes:
            - Macronutrient optimization for different training goals
            - Pre/post-workout nutrition timing
            - Body composition and weight management
            - Supplement evaluation and recommendations
            - Dietary restriction accommodations
            - Hydration strategies
            - Metabolic health optimization
            - Sustainable eating behavior change
            
            You prioritize whole foods, balanced nutrition, and realistic approaches that fit into 
            busy lifestyles while supporting training adaptations and health goals.""",
            tools=["macro_calculator", "meal_timing", "supplement_guidance"],
            max_iter=5,
            allow_delegation=False
        )
        super().__init__(config, llm_config)
    
    def _get_tools(self) -> List[BaseTool]:
        """Get nutrition coaching specific tools"""
        return [
            MacroCalculatorTool(),
            MealTimingTool(),
            SupplementGuidanceTool()
        ]
    
    def get_specialized_prompts(self) -> Dict[str, str]:
        """Get nutrition coaching specialized prompts"""
        return {
            "nutrition_assessment": """
            Assess the user's current nutritional status and dietary habits.
            Consider their fitness goals, dietary preferences, restrictions, and lifestyle.
            Identify areas for improvement and provide baseline recommendations.
            """,
            
            "macro_planning": """
            Calculate and plan optimal macronutrient distribution:
            - Protein requirements for muscle building/maintenance
            - Carbohydrate needs for energy and performance
            - Fat requirements for hormone production and health
            - Caloric needs based on goals (deficit, maintenance, surplus)
            - Timing considerations around workouts
            """,
            
            "meal_timing_optimization": """
            Optimize meal timing for workout performance and recovery:
            - Pre-workout nutrition (2-3 hours and 30-60 minutes before)
            - Intra-workout fueling for longer sessions
            - Post-workout recovery nutrition (0-2 hours after)
            - Daily meal distribution and frequency
            - Sleep and meal timing interactions
            """,
            
            "dietary_recommendations": """
            Provide specific dietary recommendations:
            - Food choices for specific goals
            - Meal prep strategies
            - Healthy substitutions
            - Portion control guidance
            - Eating out strategies
            - Budget-friendly options
            """,
            
            "supplement_evaluation": """
            Evaluate and recommend supplements based on evidence:
            - Essential vs optional supplements
            - Timing and dosage recommendations
            - Quality and safety considerations
            - Cost-benefit analysis
            - Interaction warnings
            - Natural food alternatives
            """,
            
            "hydration_strategy": """
            Develop hydration strategies for optimal performance:
            - Daily fluid requirements
            - Pre/during/post workout hydration
            - Electrolyte balance
            - Climate and sweat rate considerations
            - Hydration monitoring techniques
            """
        }
    
    def assess_nutrition_status(self, context: FitnessContext) -> Dict[str, Any]:
        """Assess user's current nutritional status"""
        prompt = self.get_specialized_prompts()["nutrition_assessment"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Context:
            - Fitness Goals: {context.fitness_goals}
            - Physical Attributes: {context.physical_attributes}
            - Experience Level: {context.experience_level}
            - Preferences: {context.preferences}
            - Current Program: {context.current_program}
            """,
            expected_output="Comprehensive nutrition assessment with improvement recommendations"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def calculate_macro_requirements(self, context: FitnessContext, specific_goals: List[str]) -> Dict[str, Any]:
        """Calculate personalized macronutrient requirements"""
        prompt = self.get_specialized_prompts()["macro_planning"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Profile:
            - Physical Attributes: {context.physical_attributes}
            - Fitness Goals: {context.fitness_goals}
            - Specific Goals: {specific_goals}
            - Experience Level: {context.experience_level}
            - Activity Level: Based on current program and recent sessions
            """,
            expected_output="Detailed macro requirements with rationale and timing recommendations"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def optimize_workout_nutrition(self, workout_schedule: Dict[str, Any], user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize nutrition timing around workouts"""
        prompt = self.get_specialized_prompts()["meal_timing_optimization"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Workout Schedule: {workout_schedule}
            User Preferences: {user_preferences}
            """,
            expected_output="Workout nutrition timing plan with specific meal recommendations"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def provide_dietary_guidance(self, context: FitnessContext, dietary_restrictions: List[str]) -> Dict[str, Any]:
        """Provide specific dietary recommendations"""
        prompt = self.get_specialized_prompts()["dietary_recommendations"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Fitness Goals: {context.fitness_goals}
            Dietary Restrictions: {dietary_restrictions}
            Preferences: {context.preferences}
            Physical Attributes: {context.physical_attributes}
            """,
            expected_output="Specific dietary recommendations with meal ideas and strategies"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def evaluate_supplements(self, goals: List[str], current_diet: Dict[str, Any], budget: str) -> Dict[str, Any]:
        """Evaluate and recommend supplements"""
        prompt = self.get_specialized_prompts()["supplement_evaluation"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Fitness Goals: {goals}
            Current Diet: {current_diet}
            Budget: {budget}
            """,
            expected_output="Evidence-based supplement recommendations with priorities and alternatives"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def create_hydration_plan(self, context: FitnessContext, climate_factors: Dict[str, Any]) -> Dict[str, Any]:
        """Create personalized hydration strategy"""
        prompt = self.get_specialized_prompts()["hydration_strategy"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Context: {context.physical_attributes}
            Training Schedule: {context.current_program}
            Climate Factors: {climate_factors}
            """,
            expected_output="Personalized hydration plan with daily and workout-specific recommendations"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}


class NutritionRequest(BaseModel):
    """Request for nutrition guidance"""
    user_context: FitnessContext
    nutrition_goals: List[str] = Field(..., description="Specific nutrition goals")
    dietary_restrictions: List[str] = Field(default_factory=list, description="Dietary restrictions or preferences")
    meal_prep_preference: str = Field("moderate", description="Meal prep willingness: minimal, moderate, extensive")
    budget_level: str = Field("moderate", description="Budget level: tight, moderate, flexible")
    cooking_skill: str = Field("intermediate", description="Cooking skill level")
    
    
class NutritionResponse(BaseModel):
    """Response from nutrition guidance"""
    macro_targets: Dict[str, float]
    meal_timing_plan: Dict[str, Any]
    food_recommendations: List[str]
    supplement_suggestions: List[Dict[str, Any]]
    hydration_plan: Dict[str, Any]
    meal_prep_tips: List[str]
    progress_tracking: Dict[str, str]
