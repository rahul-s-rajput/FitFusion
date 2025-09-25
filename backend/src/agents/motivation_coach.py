"""
Motivation Coach agent for FitFusion AI Workout App.
Specializes in behavioral psychology, habit formation, and sustainable motivation strategies.
"""

from typing import Dict, Any, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .base_agent import BaseAgent, AgentConfig, FitnessContext, WorkoutGenerationRequest


class MotivationAnalysisTool(BaseTool):
    """Tool for analyzing motivation patterns and barriers"""
    name: str = "motivation_analysis"
    description: str = "Analyze motivation patterns, barriers, and psychological factors affecting adherence"
    
    def _run(self, behavior_patterns: str, barriers: str, goals: str) -> str:
        """Analyze motivation and barriers"""
        return f"Motivation analysis: patterns {behavior_patterns}, barriers {barriers}, goals {goals}"


class HabitFormationTool(BaseTool):
    """Tool for designing habit formation strategies"""
    name: str = "habit_formation"
    description: str = "Design evidence-based habit formation strategies for sustainable fitness routines"
    
    def _run(self, current_habits: str, target_habits: str, lifestyle: str) -> str:
        """Design habit formation strategy"""
        return f"Habit formation plan: current {current_habits} -> target {target_habits}"


class GoalSettingTool(BaseTool):
    """Tool for creating SMART goals and milestone tracking"""
    name: str = "goal_setting"
    description: str = "Create SMART goals with milestone tracking and accountability systems"
    
    def _run(self, aspirations: str, timeline: str, constraints: str) -> str:
        """Create SMART goals"""
        return f"SMART goals created for {aspirations} in {timeline} with constraints {constraints}"


class MotivationCoach(BaseAgent):
    """AI agent specializing in motivation, habit formation, and behavioral change"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        config = AgentConfig(
            name="Motivation Coach",
            role="Behavioral Psychology and Motivation Expert",
            goal="Foster sustainable motivation, build positive habits, and overcome psychological barriers to create lasting fitness lifestyle changes",
            backstory="""You are a certified behavioral coach with expertise in psychology, habit formation, 
            and motivation science. You understand that sustainable fitness is more about mindset and 
            consistency than perfect workouts. Your approach is empathetic, evidence-based, and focused 
            on long-term behavior change.
            
            Your expertise includes:
            - Behavioral psychology and change theory
            - Habit formation and routine optimization
            - Goal setting and achievement strategies
            - Motivation maintenance and renewal
            - Overcoming psychological barriers
            - Building self-efficacy and confidence
            - Accountability systems and social support
            - Mindset coaching and cognitive reframing
            
            You recognize that everyone's motivation is different and that sustainable change requires 
            understanding individual psychology, values, and life circumstances. Your coaching is 
            personalized, practical, and focused on building intrinsic motivation.""",
            tools=["motivation_analysis", "habit_formation", "goal_setting"],
            max_iter=6,
            allow_delegation=False
        )
        super().__init__(config, llm_config)
    
    def _get_tools(self) -> List[BaseTool]:
        """Get motivation coaching specific tools"""
        return [
            MotivationAnalysisTool(),
            HabitFormationTool(),
            GoalSettingTool()
        ]
    
    def get_specialized_prompts(self) -> Dict[str, str]:
        """Get motivation coaching specialized prompts"""
        return {
            "motivation_assessment": """
            Assess the user's current motivation patterns, barriers, and psychological factors.
            Identify their motivation type (intrinsic vs extrinsic), past experiences, and 
            potential obstacles to consistency. Understand their values and what drives them.
            """,
            
            "habit_formation_strategy": """
            Design a habit formation strategy based on behavioral science:
            - Start with micro-habits and build gradually
            - Use habit stacking and environmental design
            - Create clear cues, routines, and rewards
            - Address common habit formation obstacles
            - Build consistency before intensity
            - Use the 2-minute rule and minimum viable habits
            """,
            
            "goal_setting_framework": """
            Create SMART goals with psychological backing:
            - Specific, measurable, achievable, relevant, time-bound
            - Process goals vs outcome goals
            - Short-term milestones and long-term vision
            - Intrinsic motivation alignment
            - Progress tracking and celebration systems
            - Flexibility and adaptation strategies
            """,
            
            "barrier_identification": """
            Identify and address psychological barriers to fitness:
            - Time and scheduling challenges
            - Perfectionism and all-or-nothing thinking
            - Fear of judgment or failure
            - Past negative experiences
            - Lack of confidence or self-efficacy
            - Competing priorities and values conflicts
            """,
            
            "motivation_maintenance": """
            Develop strategies for maintaining motivation over time:
            - Variety and novelty in routines
            - Progress celebration and recognition
            - Social support and accountability
            - Intrinsic motivation cultivation
            - Setback recovery strategies
            - Long-term vision and purpose connection
            """,
            
            "mindset_coaching": """
            Provide mindset coaching and cognitive reframing:
            - Growth mindset vs fixed mindset
            - Reframing challenges as opportunities
            - Building self-compassion and resilience
            - Identity-based habit change
            - Cognitive behavioral techniques
            - Positive self-talk and affirmations
            """
        }
    
    def assess_motivation_profile(self, context: FitnessContext) -> Dict[str, Any]:
        """Assess user's motivation patterns and psychological profile"""
        prompt = self.get_specialized_prompts()["motivation_assessment"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Context:
            - Fitness Goals: {context.fitness_goals}
            - Experience Level: {context.experience_level}
            - Preferences: {context.preferences}
            - Time Constraints: {context.time_constraints}
            - Progress History: {context.progress_history}
            """,
            expected_output="Comprehensive motivation profile with psychological insights and recommendations"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def design_habit_formation_plan(self, current_habits: Dict[str, Any], target_habits: List[str]) -> Dict[str, Any]:
        """Design evidence-based habit formation strategy"""
        prompt = self.get_specialized_prompts()["habit_formation_strategy"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Current Habits: {current_habits}
            Target Habits: {target_habits}
            """,
            expected_output="Detailed habit formation plan with micro-habits and progression strategy"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def create_smart_goals(self, aspirations: List[str], context: FitnessContext) -> Dict[str, Any]:
        """Create SMART goals with milestone tracking"""
        prompt = self.get_specialized_prompts()["goal_setting_framework"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Aspirations: {aspirations}
            Current Context: {context.fitness_goals}
            Experience Level: {context.experience_level}
            Time Constraints: {context.time_constraints}
            """,
            expected_output="SMART goals with milestones, tracking methods, and celebration strategies"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def identify_barriers(self, context: FitnessContext, past_challenges: List[str]) -> Dict[str, Any]:
        """Identify and address psychological barriers"""
        prompt = self.get_specialized_prompts()["barrier_identification"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Context: {context.preferences}
            Past Challenges: {past_challenges}
            Current Constraints: {context.time_constraints}
            """,
            expected_output="Barrier analysis with specific strategies to overcome each obstacle"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def develop_motivation_maintenance_plan(self, motivation_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Develop long-term motivation maintenance strategies"""
        prompt = self.get_specialized_prompts()["motivation_maintenance"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Motivation Profile: {motivation_profile}
            """,
            expected_output="Motivation maintenance plan with variety, accountability, and renewal strategies"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def provide_mindset_coaching(self, current_mindset: Dict[str, Any], challenges: List[str]) -> Dict[str, Any]:
        """Provide mindset coaching and cognitive reframing"""
        prompt = self.get_specialized_prompts()["mindset_coaching"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Current Mindset: {current_mindset}
            Challenges: {challenges}
            """,
            expected_output="Mindset coaching with cognitive reframing techniques and growth strategies"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}


class MotivationRequest(BaseModel):
    """Request for motivation coaching services"""
    user_context: FitnessContext
    motivation_challenges: List[str] = Field(..., description="Current motivation challenges")
    past_fitness_attempts: List[Dict[str, Any]] = Field(default_factory=list, description="Previous fitness attempts and outcomes")
    motivation_type: str = Field("mixed", description="Primary motivation type: intrinsic, extrinsic, mixed")
    accountability_preference: str = Field("self", description="Accountability preference: self, partner, group, coach")
    goal_timeline: str = Field("3_months", description="Primary goal timeline")
    
    
class MotivationResponse(BaseModel):
    """Response from motivation coaching"""
    motivation_profile: Dict[str, Any]
    habit_formation_plan: Dict[str, Any]
    smart_goals: List[Dict[str, Any]]
    barrier_solutions: Dict[str, List[str]]
    accountability_system: Dict[str, Any]
    motivation_maintenance_strategies: List[str]
    mindset_coaching_plan: Dict[str, Any]
