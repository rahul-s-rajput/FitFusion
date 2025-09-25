"""
Equipment Advisor agent for FitFusion AI Workout App.
Specializes in equipment selection, alternatives, and optimization for different spaces and budgets.
"""

from typing import Dict, Any, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .base_agent import BaseAgent, AgentConfig, FitnessContext, WorkoutGenerationRequest


class EquipmentAnalysisTool(BaseTool):
    """Tool for analyzing equipment needs and alternatives"""
    name: str = "equipment_analysis"
    description: str = "Analyze equipment requirements and suggest alternatives based on space and budget"
    
    def _run(self, workout_requirements: str, space_constraints: str, budget: str) -> str:
        """Analyze equipment needs"""
        return f"Equipment analysis for {workout_requirements} in {space_constraints} with budget {budget}"


class SpaceOptimizationTool(BaseTool):
    """Tool for optimizing workout space and equipment layout"""
    name: str = "space_optimization"
    description: str = "Optimize workout space layout and equipment storage solutions"
    
    def _run(self, available_space: str, equipment_list: str) -> str:
        """Optimize space usage"""
        return f"Space optimization for {available_space} with equipment: {equipment_list}"


class BudgetPlannerTool(BaseTool):
    """Tool for creating budget-conscious equipment acquisition plans"""
    name: str = "budget_planner"
    description: str = "Create prioritized equipment acquisition plans within budget constraints"
    
    def _run(self, budget: str, priorities: str, timeline: str) -> str:
        """Create budget plan"""
        return f"Budget plan created for {budget} with priorities: {priorities}"


class EquipmentAdvisor(BaseAgent):
    """AI agent specializing in fitness equipment selection and optimization"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        config = AgentConfig(
            name="Equipment Advisor",
            role="Fitness Equipment Specialist",
            goal="Provide expert guidance on fitness equipment selection, alternatives, and space optimization to maximize workout effectiveness within budget and space constraints",
            backstory="""You are a fitness equipment specialist with extensive knowledge of home gym setups, 
            commercial fitness equipment, and creative workout solutions. You understand the pros and cons 
            of different equipment types, space requirements, and how to maximize workout variety with 
            minimal equipment investment.
            
            Your expertise includes:
            - Equipment selection for specific fitness goals
            - Space-efficient home gym design
            - Budget-conscious equipment prioritization
            - Equipment maintenance and safety
            - Creative alternatives and DIY solutions
            - Multi-functional equipment recommendations
            - Storage and organization solutions
            - Equipment progression and upgrades
            
            You excel at finding creative solutions that deliver maximum workout variety and effectiveness 
            while working within real-world constraints of space, budget, and lifestyle.""",
            tools=["equipment_analysis", "space_optimization", "budget_planner"],
            max_iter=6,
            allow_delegation=False
        )
        super().__init__(config, llm_config)
    
    def _get_tools(self) -> List[BaseTool]:
        """Get equipment advisory specific tools"""
        return [
            EquipmentAnalysisTool(),
            SpaceOptimizationTool(),
            BudgetPlannerTool()
        ]
    
    def get_specialized_prompts(self) -> Dict[str, str]:
        """Get equipment advisory specialized prompts"""
        return {
            "equipment_assessment": """
            Assess the user's current equipment inventory and identify gaps or optimization opportunities.
            Consider their fitness goals, space constraints, and budget to provide targeted recommendations.
            """,
            
            "equipment_selection": """
            Recommend specific equipment based on user requirements:
            - Primary fitness goals and training style
            - Available space and storage options
            - Budget constraints and value priorities
            - Experience level and safety considerations
            - Versatility and multi-functionality needs
            - Quality and durability requirements
            """,
            
            "space_optimization": """
            Optimize workout space layout and equipment arrangement:
            - Efficient use of available space
            - Equipment storage solutions
            - Multi-purpose area design
            - Safety clearances and movement patterns
            - Noise considerations for neighbors
            - Ventilation and lighting optimization
            """,
            
            "budget_planning": """
            Create prioritized equipment acquisition plans:
            - Essential vs nice-to-have equipment
            - Phased acquisition timeline
            - Cost-effective alternatives
            - Quality vs budget trade-offs
            - Used equipment considerations
            - DIY and creative solutions
            """,
            
            "equipment_alternatives": """
            Suggest creative alternatives and substitutions:
            - Bodyweight alternatives to equipment exercises
            - Household items as fitness tools
            - Resistance band substitutions
            - Outdoor and park equipment utilization
            - Partner/buddy system alternatives
            - Minimal equipment maximum impact solutions
            """,
            
            "maintenance_guidance": """
            Provide equipment maintenance and safety guidance:
            - Regular maintenance schedules
            - Safety inspection checklists
            - Proper storage techniques
            - Troubleshooting common issues
            - When to replace or upgrade
            - Warranty and service considerations
            """
        }
    
    def assess_equipment_needs(self, context: FitnessContext) -> Dict[str, Any]:
        """Assess user's equipment needs and current inventory"""
        prompt = self.get_specialized_prompts()["equipment_assessment"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Context:
            - Fitness Goals: {context.fitness_goals}
            - Current Equipment: {context.available_equipment}
            - Space Constraints: {context.space_constraints}
            - Experience Level: {context.experience_level}
            - Preferences: {context.preferences}
            """,
            expected_output="Equipment assessment with gap analysis and optimization recommendations"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def recommend_equipment(self, requirements: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend specific equipment based on requirements"""
        prompt = self.get_specialized_prompts()["equipment_selection"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Requirements: {requirements}
            Constraints: {constraints}
            """,
            expected_output="Specific equipment recommendations with rationale and alternatives"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def optimize_workout_space(self, space_details: Dict[str, Any], equipment_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize workout space layout and organization"""
        prompt = self.get_specialized_prompts()["space_optimization"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Space Details: {space_details}
            Equipment List: {equipment_list}
            """,
            expected_output="Space optimization plan with layout suggestions and storage solutions"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def create_budget_plan(self, budget_info: Dict[str, Any], priorities: List[str]) -> Dict[str, Any]:
        """Create prioritized equipment acquisition plan"""
        prompt = self.get_specialized_prompts()["budget_planning"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Budget Information: {budget_info}
            Priorities: {priorities}
            """,
            expected_output="Prioritized equipment acquisition plan with timeline and alternatives"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def suggest_alternatives(self, target_exercises: List[str], available_items: List[str]) -> Dict[str, Any]:
        """Suggest creative alternatives for equipment-based exercises"""
        prompt = self.get_specialized_prompts()["equipment_alternatives"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Target Exercises: {target_exercises}
            Available Items: {available_items}
            """,
            expected_output="Creative alternatives and substitutions with effectiveness ratings"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def provide_maintenance_guidance(self, equipment_inventory: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Provide equipment maintenance and safety guidance"""
        prompt = self.get_specialized_prompts()["maintenance_guidance"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Equipment Inventory: {equipment_inventory}
            """,
            expected_output="Maintenance schedules and safety guidelines for each equipment type"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}


class EquipmentRequest(BaseModel):
    """Request for equipment advisory services"""
    user_context: FitnessContext
    budget_range: str = Field(..., description="Budget range: under_100, 100_500, 500_1000, 1000_plus")
    space_type: str = Field(..., description="Space type: apartment, house, garage, outdoor, gym")
    priority_goals: List[str] = Field(..., description="Priority fitness goals for equipment selection")
    acquisition_timeline: str = Field("3_months", description="Timeline for equipment acquisition")
    
    
class EquipmentResponse(BaseModel):
    """Response from equipment advisory"""
    recommended_equipment: List[Dict[str, Any]]
    space_layout_plan: Dict[str, Any]
    budget_breakdown: Dict[str, float]
    alternative_solutions: List[Dict[str, Any]]
    acquisition_timeline: Dict[str, List[str]]
    maintenance_schedule: Dict[str, str]
    upgrade_path: List[str]
