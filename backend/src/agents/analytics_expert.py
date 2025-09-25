"""
Analytics Expert agent for FitFusion AI Workout App.
Specializes in data analysis, progress tracking, and performance insights.
"""

from typing import Dict, Any, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .base_agent import BaseAgent, AgentConfig, FitnessContext, WorkoutGenerationRequest


class DataAnalysisTool(BaseTool):
    """Tool for analyzing fitness and performance data"""
    name: str = "data_analysis"
    description: str = "Analyze fitness data to identify trends, patterns, and insights"
    
    def _run(self, workout_data: str, progress_data: str, analysis_type: str) -> str:
        """Analyze fitness data"""
        return f"Data analysis completed: {analysis_type} on workout data and progress data"


class TrendIdentificationTool(BaseTool):
    """Tool for identifying trends and patterns in fitness data"""
    name: str = "trend_identification"
    description: str = "Identify trends, patterns, and correlations in fitness performance data"
    
    def _run(self, historical_data: str, metrics: str, timeframe: str) -> str:
        """Identify trends in data"""
        return f"Trends identified in {metrics} over {timeframe}: {historical_data}"


class PredictiveModelingTool(BaseTool):
    """Tool for creating predictive models and forecasts"""
    name: str = "predictive_modeling"
    description: str = "Create predictive models for fitness progress and goal achievement"
    
    def _run(self, training_data: str, target_metrics: str, prediction_horizon: str) -> str:
        """Create predictive models"""
        return f"Predictive model created for {target_metrics} with horizon {prediction_horizon}"


class AnalyticsExpert(BaseAgent):
    """AI agent specializing in fitness data analysis and performance insights"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        config = AgentConfig(
            name="Analytics Expert",
            role="Fitness Data Scientist and Performance Analyst",
            goal="Transform fitness data into actionable insights, identify performance patterns, and provide data-driven recommendations for optimization and goal achievement",
            backstory="""You are a data scientist specializing in fitness analytics and performance optimization. 
            You excel at finding meaningful patterns in complex fitness data and translating statistical 
            insights into practical recommendations. Your expertise combines sports science with advanced 
            analytics to help users understand their progress and optimize their training.
            
            Your expertise includes:
            - Statistical analysis of fitness and performance data
            - Trend identification and pattern recognition
            - Predictive modeling for goal achievement
            - Performance benchmarking and comparison
            - Data visualization and insight communication
            - A/B testing for workout optimization
            - Correlation analysis between lifestyle and performance
            - Risk assessment and injury prediction
            
            You understand that data without context is meaningless, so you always consider individual 
            circumstances, goals, and preferences when interpreting results. Your insights are actionable, 
            easy to understand, and focused on helping users make better decisions.""",
            tools=["data_analysis", "trend_identification", "predictive_modeling"],
            max_iter=7,
            allow_delegation=True
        )
        super().__init__(config, llm_config)
    
    def _get_tools(self) -> List[BaseTool]:
        """Get analytics specific tools"""
        return [
            DataAnalysisTool(),
            TrendIdentificationTool(),
            PredictiveModelingTool()
        ]
    
    def get_specialized_prompts(self) -> Dict[str, str]:
        """Get analytics specialized prompts"""
        return {
            "performance_analysis": """
            Analyze fitness performance data to identify strengths, weaknesses, and opportunities:
            - Workout consistency and adherence patterns
            - Performance trends across different exercise types
            - Progress velocity and plateau identification
            - Comparative analysis against goals and benchmarks
            - Seasonal or cyclical patterns in performance
            """,
            
            "progress_tracking": """
            Analyze progress data and provide insights on goal achievement:
            - Rate of progress toward specific goals
            - Milestone achievement analysis
            - Progress consistency and variability
            - Factors correlating with better progress
            - Prediction of goal achievement timeline
            - Identification of progress accelerators and barriers
            """,
            
            "workout_optimization": """
            Analyze workout data to optimize training effectiveness:
            - Exercise selection effectiveness analysis
            - Volume and intensity optimization
            - Recovery and adaptation patterns
            - Workout timing and frequency analysis
            - Equipment utilization and effectiveness
            - Program adherence and modification patterns
            """,
            
            "behavioral_insights": """
            Analyze behavioral patterns and their impact on fitness outcomes:
            - Consistency patterns and triggers
            - Motivation and engagement correlations
            - Lifestyle factors affecting performance
            - Habit formation and maintenance patterns
            - Barrier identification through data analysis
            - Success factor identification
            """,
            
            "predictive_analytics": """
            Create predictive models and forecasts for fitness outcomes:
            - Goal achievement probability and timeline
            - Performance plateau prediction
            - Injury risk assessment based on patterns
            - Optimal training load recommendations
            - Seasonal performance predictions
            - Long-term trend forecasting
            """,
            
            "comparative_analysis": """
            Provide comparative analysis and benchmarking:
            - Progress comparison to similar users
            - Performance benchmarking against standards
            - Program effectiveness comparisons
            - Equipment and exercise effectiveness ranking
            - Time-based performance comparisons
            - Goal achievement rate analysis
            """
        }
    
    def analyze_performance_data(self, context: FitnessContext) -> Dict[str, Any]:
        """Analyze comprehensive performance data"""
        prompt = self.get_specialized_prompts()["performance_analysis"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Context:
            - Recent Sessions: {context.recent_sessions}
            - Progress History: {context.progress_history}
            - Current Program: {context.current_program}
            - Fitness Goals: {context.fitness_goals}
            - Experience Level: {context.experience_level}
            """,
            expected_output="Comprehensive performance analysis with strengths, weaknesses, and optimization opportunities"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def track_progress_insights(self, progress_data: List[Dict[str, Any]], goals: List[str]) -> Dict[str, Any]:
        """Analyze progress data and provide goal achievement insights"""
        prompt = self.get_specialized_prompts()["progress_tracking"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Progress Data: {progress_data}
            Goals: {goals}
            """,
            expected_output="Progress analysis with achievement predictions and optimization recommendations"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def optimize_workout_effectiveness(self, workout_history: List[Dict[str, Any]], performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze workout data to optimize training effectiveness"""
        prompt = self.get_specialized_prompts()["workout_optimization"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Workout History: {workout_history}
            Performance Metrics: {performance_metrics}
            """,
            expected_output="Workout optimization analysis with specific recommendations for improvement"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def analyze_behavioral_patterns(self, context: FitnessContext, behavioral_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze behavioral patterns and their impact on outcomes"""
        prompt = self.get_specialized_prompts()["behavioral_insights"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Context: {context.preferences}
            Behavioral Data: {behavioral_data}
            Progress History: {context.progress_history}
            """,
            expected_output="Behavioral analysis with insights on success factors and barriers"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def create_predictive_models(self, historical_data: Dict[str, Any], prediction_targets: List[str]) -> Dict[str, Any]:
        """Create predictive models for fitness outcomes"""
        prompt = self.get_specialized_prompts()["predictive_analytics"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            Historical Data: {historical_data}
            Prediction Targets: {prediction_targets}
            """,
            expected_output="Predictive models with forecasts and confidence intervals"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}
    
    def provide_comparative_analysis(self, user_data: Dict[str, Any], benchmark_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide comparative analysis and benchmarking"""
        prompt = self.get_specialized_prompts()["comparative_analysis"]
        
        task = self.create_task(
            description=f"""
            {prompt}
            
            User Data: {user_data}
            Benchmark Data: {benchmark_data}
            """,
            expected_output="Comparative analysis with benchmarking insights and recommendations"
        )
        
        result = self.execute_task(task)
        return result.result if result.success else {"error": result.error_message}


class AnalyticsRequest(BaseModel):
    """Request for analytics and insights"""
    user_context: FitnessContext
    analysis_type: str = Field(..., description="Type of analysis: performance, progress, behavioral, predictive")
    time_period: str = Field("30_days", description="Time period for analysis")
    metrics_of_interest: List[str] = Field(..., description="Specific metrics to analyze")
    comparison_baseline: str = Field("personal_history", description="Comparison baseline: personal_history, peer_group, standards")
    
    
class AnalyticsResponse(BaseModel):
    """Response from analytics analysis"""
    performance_insights: Dict[str, Any]
    progress_analysis: Dict[str, Any]
    trend_identification: List[Dict[str, Any]]
    predictive_forecasts: Dict[str, Any]
    recommendations: List[str]
    data_visualizations: List[Dict[str, Any]]
    benchmark_comparisons: Dict[str, Any]
