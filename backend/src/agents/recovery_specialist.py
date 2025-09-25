"""
Recovery Specialist agent for FitFusion AI Workout App.
Specializes in recovery protocols, sleep optimization, and injury prevention strategies.
"""

from typing import Dict, Any, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .base_agent import BaseAgent, AgentConfig, FitnessContext, WorkoutGenerationRequest


class RecoveryAnalysisTool(BaseTool):
    """Tool for analyzing recovery needs and status"""
    name: str = "recovery_analysis"
    description: str = "Analyze current recovery status and recommend optimization strategies"
    
    def _run(self, training_load: str, sleep_data: str, stress_indicators: str) -> str:
        """Analyze recovery status"""
        return f"Recovery analysis: training load {training_load}, sleep {sleep_data}, stress {stress_indicators}"


class SleepOptimizationTool(BaseTool):
    """Tool for optimizing sleep quality and recovery"""
    name: str = "sleep_optimization"
    description: str = "Provide sleep optimization strategies for better recovery"
    
    def _run(self, sleep_patterns: str, lifestyle_factors: str) -> str:
        """Optimize sleep for recovery"""
        return f"Sleep optimization for patterns: {sleep_patterns}, lifestyle: {lifestyle_factors}"


class StressManagementTool(BaseTool):
    """Tool for managing stress and its impact on recovery"""
    name: str = "stress_management"
    description: str = "Provide stress management techniques to improve recovery"
    
    def _run(self, stress_level: str, stressors: str, preferences: str) -> str:
        """Manage stress for better recovery"""
        return f"Stress management for level {stress_level}, stressors: {stressors}"


class RecoverySpecialist(BaseAgent):
    """AI agent specializing in recovery, sleep, and injury prevention"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        config = AgentConfig(
            name="Recovery Specialist",
            role="Recovery and Regeneration Expert",
            goal="Optimize recovery protocols, sleep quality, and stress management to maximize training adaptations while preventing overtraining and injury",
            backstory="""You are a recovery specialist with expertise in exercise physiology, sleep science, 
            and stress management. You understand the critical role of recovery in fitness progress and 
            long-term health. Your approach integrates evidence-based recovery modalities with practical 
            lifestyle strategies.
            
            Your expertise includes:
            - Sleep optimization for athletic performance
            - Active and passive recovery protocols
            - Stress management and cortisol regulation
            - Injury prevention and movement quality
            - Recovery monitoring and biomarkers
            - Periodization and deload strategies
            - Mobility and flexibility programming
            - Recovery nutrition and hydration
            
            You recognize that recovery is where adaptation happens and that sustainable fitness requires 
            balancing training stress with adequate recovery. Your recommendations are practical and 
            fit into real-world schedules and lifestyles.""",
            tools=["recovery_analysis", "sleep_optimization", "stress_management"],
            max_iter=5,
            allow_delegation=False
        )
        super().__init__(config, llm_config)
    
    def _get_tools(self) -> List[BaseTool]:
        """Get recovery specialist specific tools"""
        return [
            RecoveryAnalysisTool(),
            SleepOptimizationTool(),
            StressManagementTool()
        ]
    
    def get_specialized_prompts(self) -> Dict[str, str]:
        """Get recovery specialist specialized prompts"""
        return {
            "recovery_assessment": """
            Assess the user's current recovery status and identify areas for improvement.
            Consider training load, sleep quality, stress levels, and lifestyle factors.
            Provide baseline recommendations for recovery optimization.
            """,
            
            "sleep_optimization": """
            Optimize sleep quality and duration for better recovery:
            - Sleep hygiene practices
            - Bedroom environment optimization
            - Pre-sleep routines and rituals
            - Sleep timing and consistency
            - Technology and blue light management
            - Supplement considerations for sleep
            - Sleep tracking and monitoring
            """,
            
            "active_recovery": """
            Design active recovery protocols:
            - Low-intensity movement patterns
            - Mobility and flexibility routines
            - Breathing exercises and meditation
            - Light cardio activities
            - Yoga and stretching sequences
            - Recovery-focused workouts
            """,
            
            "stress_management": """
            Develop stress management strategies:
            - Stress identification and monitoring
            - Relaxation techniques and mindfulness
            - Time management and prioritization
            - Social support and communication
            - Lifestyle modifications
            - Recovery mindset and mental training
            """,
            
            "injury_prevention": """
            Create injury prevention protocols:
            - Movement screening and assessment
            - Corrective exercise programming
            - Warm-up and cool-down optimization
            - Load management and progression
            - Risk factor identification
            - Early intervention strategies
            """,
            
            "recovery_monitoring": """
            Establish recovery monitoring systems:
            - Subjective recovery markers (mood, energy, motivation)
            - Objective markers (HRV, resting HR, sleep metrics)
            - Performance indicators
            - Recovery tracking methods
            - When to modify training based on recovery
            """
        }
    
    def assess_recovery_status(self, context: FitnessContext) -> Dict[str, Any]:
        """Assess user's current recovery status"""
        prompt = self.get_specialized_prompts()["recovery_assessment"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Context:
            - Current Program: {context.current_program}
            - Recent Sessions: {context.recent_sessions}
            - Experience Level: {context.experience_level}
            - Lifestyle Preferences: {context.preferences}
            - Time Constraints: {context.time_constraints}
            """,
            expected_output="Comprehensive recovery assessment with optimization recommendations"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def optimize_sleep_protocol(self, sleep_data: Dict[str, Any], lifestyle_factors: Dict[str, Any]) -> Dict[str, Any]:
        """Create personalized sleep optimization protocol"""
        prompt = self.get_specialized_prompts()["sleep_optimization"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Sleep Data: {sleep_data}
            Lifestyle Factors: {lifestyle_factors}
            """,
            expected_output="Personalized sleep optimization protocol with specific strategies"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def design_active_recovery(self, context: FitnessContext, recovery_goals: List[str]) -> Dict[str, Any]:
        """Design active recovery protocols"""
        prompt = self.get_specialized_prompts()["active_recovery"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Recovery Goals: {recovery_goals}
            Available Equipment: {context.available_equipment}
            Space Constraints: {context.space_constraints}
            Time Available: {context.time_constraints}
            Experience Level: {context.experience_level}
            """,
            expected_output="Active recovery protocol with specific exercises and timing"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def create_stress_management_plan(self, stress_profile: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Create personalized stress management plan"""
        prompt = self.get_specialized_prompts()["stress_management"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Stress Profile: {stress_profile}
            User Preferences: {preferences}
            """,
            expected_output="Comprehensive stress management plan with practical techniques"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def develop_injury_prevention_protocol(self, context: FitnessContext, risk_factors: List[str]) -> Dict[str, Any]:
        """Develop injury prevention protocol"""
        prompt = self.get_specialized_prompts()["injury_prevention"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Context: {context.experience_level}
            Risk Factors: {risk_factors}
            Current Program: {context.current_program}
            Available Equipment: {context.available_equipment}
            """,
            expected_output="Injury prevention protocol with specific exercises and guidelines"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def setup_recovery_monitoring(self, context: FitnessContext, monitoring_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Setup recovery monitoring system"""
        prompt = self.get_specialized_prompts()["recovery_monitoring"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Context: {context.experience_level}
            Monitoring Preferences: {monitoring_preferences}
            Training Schedule: {context.current_program}
            """,
            expected_output="Recovery monitoring system with metrics and tracking methods"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}


class RecoveryRequest(BaseModel):
    """Request for recovery optimization services"""
    user_context: FitnessContext
    recovery_goals: List[str] = Field(..., description="Specific recovery goals")
    sleep_quality_rating: int = Field(..., ge=1, le=10, description="Current sleep quality rating 1-10")
    stress_level: int = Field(..., ge=1, le=10, description="Current stress level 1-10")
    recovery_time_available: int = Field(..., description="Minutes available daily for recovery activities")
    injury_history: List[str] = Field(default_factory=list, description="Previous injuries or concerns")
    
    
class RecoveryResponse(BaseModel):
    """Response from recovery optimization"""
    sleep_protocol: Dict[str, Any]
    active_recovery_plan: Dict[str, Any]
    stress_management_techniques: List[Dict[str, Any]]
    injury_prevention_exercises: List[Dict[str, Any]]
    recovery_monitoring_plan: Dict[str, str]
    lifestyle_recommendations: List[str]
    recovery_timeline: Dict[str, str]
