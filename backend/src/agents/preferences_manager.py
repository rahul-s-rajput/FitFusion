"""
Preferences Manager agent for FitFusion AI Workout App.
Specializes in learning user preferences, personalizing experiences, and adapting recommendations.
"""

from typing import Dict, Any, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .base_agent import BaseAgent, AgentConfig, FitnessContext, WorkoutGenerationRequest


class PreferenceAnalysisTool(BaseTool):
    """Tool for analyzing user preferences and behavior patterns"""
    name: str = "preference_analysis"
    description: str = "Analyze user behavior to identify preferences and personalization opportunities"
    
    def _run(self, user_behavior: str, feedback_data: str, interaction_patterns: str) -> str:
        """Analyze user preferences"""
        return f"Preference analysis: behavior {user_behavior}, feedback {feedback_data}, patterns {interaction_patterns}"


class PersonalizationTool(BaseTool):
    """Tool for creating personalized recommendations"""
    name: str = "personalization"
    description: str = "Create personalized recommendations based on learned preferences"
    
    def _run(self, user_profile: str, preferences: str, context: str) -> str:
        """Create personalized recommendations"""
        return f"Personalized recommendations for profile {user_profile} with preferences {preferences}"


class AdaptationTool(BaseTool):
    """Tool for adapting recommendations based on feedback"""
    name: str = "adaptation"
    description: str = "Adapt and refine recommendations based on user feedback and outcomes"
    
    def _run(self, current_recommendations: str, feedback: str, outcomes: str) -> str:
        """Adapt recommendations"""
        return f"Adapted recommendations based on feedback {feedback} and outcomes {outcomes}"


class PreferencesManager(BaseAgent):
    """AI agent specializing in user preference learning and personalization"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        config = AgentConfig(
            name="Preferences Manager",
            role="Personalization and User Experience Specialist",
            goal="Learn and adapt to user preferences to create highly personalized fitness experiences that align with individual tastes, constraints, and goals",
            backstory="""You are a user experience specialist with expertise in personalization algorithms 
            and behavioral analysis. You excel at understanding individual preferences through both explicit 
            feedback and implicit behavioral signals. Your goal is to make the fitness experience feel 
            uniquely tailored to each user.
            
            Your expertise includes:
            - User preference learning and modeling
            - Behavioral pattern recognition
            - Personalization algorithm design
            - Feedback analysis and interpretation
            - User experience optimization
            - Recommendation system refinement
            - A/B testing for personalization
            - Preference evolution and adaptation
            
            You understand that preferences are dynamic and context-dependent. You continuously learn 
            from user interactions, feedback, and outcomes to refine personalization. Your approach 
            balances user preferences with fitness best practices to create optimal experiences.""",
            tools=["preference_analysis", "personalization", "adaptation"],
            max_iter=5,
            allow_delegation=False
        )
        super().__init__(config, llm_config)
    
    def _get_tools(self) -> List[BaseTool]:
        """Get preference management specific tools"""
        return [
            PreferenceAnalysisTool(),
            PersonalizationTool(),
            AdaptationTool()
        ]
    
    def get_specialized_prompts(self) -> Dict[str, str]:
        """Get preference management specialized prompts"""
        return {
            "preference_discovery": """
            Analyze user behavior and feedback to discover preferences:
            - Exercise type preferences and dislikes
            - Workout timing and duration preferences
            - Intensity and difficulty preferences
            - Equipment and space preferences
            - Coaching style and communication preferences
            - Goal prioritization and trade-off preferences
            - Motivation and reward preferences
            """,
            
            "personalization_strategy": """
            Create personalized recommendations based on learned preferences:
            - Workout customization based on preferences
            - Exercise selection and sequencing
            - Coaching tone and communication style
            - Progress tracking and celebration methods
            - Challenge level and progression rate
            - Recovery and rest day preferences
            - Notification timing and frequency
            """,
            
            "preference_evolution": """
            Track and adapt to evolving user preferences:
            - Preference changes over time
            - Context-dependent preference variations
            - Skill level impact on preferences
            - Goal evolution and preference shifts
            - Seasonal and lifestyle preference changes
            - Feedback-driven preference refinement
            """,
            
            "experience_optimization": """
            Optimize the user experience based on preferences:
            - Interface customization and layout
            - Content prioritization and filtering
            - Feature prominence and accessibility
            - Workflow optimization for user patterns
            - Personalized onboarding and guidance
            - Adaptive difficulty and challenge levels
            """,
            
            "feedback_integration": """
            Integrate user feedback to improve personalization:
            - Explicit feedback analysis and application
            - Implicit feedback from behavior patterns
            - Satisfaction and engagement metrics
            - Preference conflict resolution
            - Feedback quality assessment
            - Continuous learning and adaptation
            """,
            
            "preference_balancing": """
            Balance user preferences with fitness best practices:
            - Preference vs optimal training balance
            - Gradual introduction of beneficial but disliked elements
            - Compromise solutions for conflicting preferences
            - Education and preference evolution guidance
            - Safety and effectiveness priority management
            """
        }
    
    def discover_user_preferences(self, context: FitnessContext, behavioral_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user behavior to discover preferences"""
        prompt = self.get_specialized_prompts()["preference_discovery"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Context:
            - Current Preferences: {context.preferences}
            - Recent Sessions: {context.recent_sessions}
            - Progress History: {context.progress_history}
            - Behavioral Data: {behavioral_data}
            """,
            expected_output="Comprehensive preference profile with discovered patterns and insights"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def create_personalized_recommendations(self, user_preferences: Dict[str, Any], context: FitnessContext) -> Dict[str, Any]:
        """Create personalized recommendations based on preferences"""
        prompt = self.get_specialized_prompts()["personalization_strategy"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Preferences: {user_preferences}
            Context: {context.fitness_goals}
            Available Equipment: {context.available_equipment}
            Time Constraints: {context.time_constraints}
            """,
            expected_output="Personalized recommendations tailored to user preferences and constraints"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def track_preference_evolution(self, historical_preferences: List[Dict[str, Any]], current_behavior: Dict[str, Any]) -> Dict[str, Any]:
        """Track how user preferences evolve over time"""
        prompt = self.get_specialized_prompts()["preference_evolution"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Historical Preferences: {historical_preferences}
            Current Behavior: {current_behavior}
            """,
            expected_output="Preference evolution analysis with adaptation recommendations"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def optimize_user_experience(self, preferences: Dict[str, Any], usage_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize user experience based on preferences"""
        prompt = self.get_specialized_prompts()["experience_optimization"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Preferences: {preferences}
            Usage Patterns: {usage_patterns}
            """,
            expected_output="UX optimization recommendations for personalized experience"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def integrate_user_feedback(self, feedback_data: Dict[str, Any], current_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate user feedback to improve personalization"""
        prompt = self.get_specialized_prompts()["feedback_integration"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Feedback Data: {feedback_data}
            Current Preferences: {current_preferences}
            """,
            expected_output="Updated preferences and personalization strategy based on feedback"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def balance_preferences_with_best_practices(self, user_preferences: Dict[str, Any], fitness_goals: List[str]) -> Dict[str, Any]:
        """Balance user preferences with fitness best practices"""
        prompt = self.get_specialized_prompts()["preference_balancing"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Preferences: {user_preferences}
            Fitness Goals: {fitness_goals}
            """,
            expected_output="Balanced recommendations that respect preferences while optimizing effectiveness"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}


class PreferencesRequest(BaseModel):
    """Request for preference management services"""
    user_context: FitnessContext
    behavioral_data: Dict[str, Any] = Field(..., description="User behavioral data and interaction patterns")
    feedback_data: Dict[str, Any] = Field(default_factory=dict, description="Explicit user feedback")
    preference_categories: List[str] = Field(..., description="Categories of preferences to analyze")
    personalization_goals: List[str] = Field(..., description="Goals for personalization")
    
    
class PreferencesResponse(BaseModel):
    """Response from preference management"""
    discovered_preferences: Dict[str, Any]
    personalized_recommendations: Dict[str, Any]
    preference_evolution_insights: Dict[str, Any]
    experience_optimizations: List[Dict[str, Any]]
    updated_preference_model: Dict[str, Any]
    balancing_strategies: Dict[str, str]
    next_learning_opportunities: List[str]
