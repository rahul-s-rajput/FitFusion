"""
Base agent class for FitFusion AI Workout App.
Provides common functionality for all CrewAI agents.
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from crewai import Agent, Task, Crew
from crewai.llm import LLM
from crewai.tools import BaseTool


logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    """Configuration for AI agents"""
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[str] = Field(default_factory=list)
    max_iter: int = Field(default=5)
    memory: bool = Field(default=True)
    verbose: bool = Field(default=True)
    allow_delegation: bool = Field(default=False)


class TaskResult(BaseModel):
    """Result from agent task execution"""
    agent_name: str
    task_id: str
    result: Dict[str, Any]
    execution_time: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None


class BaseAgent(ABC):
    """Base class for all FitFusion AI agents"""
    
    def __init__(self, config: AgentConfig, llm_config: Dict[str, Any]):
        self.config = config
        self.llm_config = llm_config or {}
        self.llm = self._create_llm()
        self.tools = self._get_tools()
        self.agent = self._create_agent()
    
    @abstractmethod
    def _get_tools(self) -> List[BaseTool]:
        """Get tools specific to this agent"""
        pass
    
    @abstractmethod
    def get_specialized_prompts(self) -> Dict[str, str]:
        """Get specialized prompts for this agent's domain"""
        pass
    
    def _create_llm(self) -> Optional[LLM]:
        """Initialize the language model for this agent using shared configuration."""
        if not self.llm_config:
            logger.warning("No LLM configuration provided for %s; CrewAI will use its defaults", self.config.name)
            return None

        config = {key: value for key, value in self.llm_config.items() if value is not None}

        if not config.get("model"):
            raise ValueError("llm_config must include a 'model' entry")

        if not config.get("api_key"):
            logger.debug(
                "LLM config for %s is missing an explicit API key; falling back to environment variables",
                self.config.name,
            )

        try:
            return LLM(**config)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to initialize LLM for agent {self.config.name}: {exc}"
            ) from exc

    def _create_agent(self) -> Agent:
        """Create the CrewAI agent instance"""
        return Agent(
            role=self.config.role,
            goal=self.config.goal,
            backstory=self.config.backstory,
            verbose=self.config.verbose,
            allow_delegation=self.config.allow_delegation,
            max_iter=self.config.max_iter,
            memory=self.config.memory,
            tools=self.tools,
            llm=self.llm
        )
    
    def create_task(self, description: str, expected_output: str, context: Dict[str, Any] = None) -> Task:
        """Create a task for this agent"""
        task_context: Optional[List[str]] = None

        if context:
            if isinstance(context, dict):
                task_context = []
                for key, value in context.items():
                    if isinstance(value, (dict, list)):
                        task_context.append(f"{key}: {json.dumps(value, default=str)}")
                    else:
                        task_context.append(f"{key}: {value}")
            elif isinstance(context, (list, tuple, set)):
                task_context = []
                for item in context:
                    if isinstance(item, (dict, list)):
                        task_context.append(json.dumps(item, default=str))
                    else:
                        task_context.append(str(item))
            else:
                task_context = [str(context)]

        task_kwargs = {
            "description": description,
            "expected_output": expected_output,
            "agent": self.agent,
        }
        if task_context:
            task_kwargs["context"] = task_context

        return Task(**task_kwargs)

    def _extract_raw_output(self, crew_output: Any) -> Any:
        """Best effort extraction of textual output from CrewAI result objects."""
        if crew_output is None:
            return ""
        if isinstance(crew_output, (dict, list)):
            return crew_output
        if isinstance(crew_output, str):
            return crew_output

        for attr in ("raw_output", "output", "final_output", "response", "text"):
            if hasattr(crew_output, attr):
                value = getattr(crew_output, attr)
                try:
                    return value() if callable(value) else value
                except TypeError:
                    return value

        return str(crew_output)

    def _json_candidates(self, text: str) -> List[str]:
        """Generate potential JSON substrings from a block of text."""
        candidates: List[str] = []
        stripped = text.strip()
        if stripped.startswith('{') and stripped.endswith('}'):
            candidates.append(stripped)
        if stripped.startswith('[') and stripped.endswith(']'):
            candidates.append(stripped)

        brace_start = stripped.find('{')
        brace_end = stripped.rfind('}')
        if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
            candidates.append(stripped[brace_start:brace_end + 1])

        bracket_start = stripped.find('[')
        bracket_end = stripped.rfind(']')
        if bracket_start != -1 and bracket_end != -1 and bracket_end > bracket_start:
            candidates.append(stripped[bracket_start:bracket_end + 1])

        seen = set()
        unique_candidates = []
        for candidate in candidates:
            normalized = candidate.strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_candidates.append(normalized)
        return unique_candidates

    def _parse_structured_output(self, raw_output: Any) -> Dict[str, Any]:
        """Attempt to coerce agent output into a structured dictionary."""
        if isinstance(raw_output, dict):
            return raw_output
        if isinstance(raw_output, list):
            return {"items": raw_output}

        text = str(raw_output).strip()
        if not text:
            return {}

        for candidate in self._json_candidates(text):
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
                return {"items": parsed}
            except json.JSONDecodeError:
                continue

        return {"raw_output": text}

    def execute_task(self, task: Task) -> TaskResult:
        """Execute a task and return structured result"""
        start_time = datetime.now()

        try:
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=self.config.verbose
            )

            result = crew.kickoff()
            raw_output = self._extract_raw_output(result)
            structured_output = self._parse_structured_output(raw_output)
            if isinstance(raw_output, str) and isinstance(structured_output, dict):
                structured_output.setdefault('_raw_output', raw_output)

            execution_time = (datetime.now() - start_time).total_seconds()

            return TaskResult(
                agent_name=self.config.name,
                task_id=str(task.id) if hasattr(task, 'id') else 'unknown',
                result=structured_output,
                execution_time=execution_time,
                timestamp=datetime.now(),
                success=True
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()

            return TaskResult(
                agent_name=self.config.name,
                task_id=str(task.id) if hasattr(task, 'id') else 'unknown',
                result={},
                execution_time=execution_time,
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent"""
        return {
            "name": self.config.name,
            "role": self.config.role,
            "goal": self.config.goal,
            "backstory": self.config.backstory,
            "tools": [tool.__class__.__name__ for tool in self.tools],
            "specializations": list(self.get_specialized_prompts().keys())
        }


class FitnessContext(BaseModel):
    """Context information for fitness-related tasks"""
    user_id: UUID
    fitness_goals: List[str]
    experience_level: str
    available_equipment: List[Dict[str, Any]]
    space_constraints: Dict[str, Any]
    time_constraints: Dict[str, Any]
    physical_attributes: Dict[str, Any]
    preferences: Dict[str, Any]
    current_program: Optional[Dict[str, Any]] = None
    recent_sessions: List[Dict[str, Any]] = Field(default_factory=list)
    progress_history: List[Dict[str, Any]] = Field(default_factory=list)


class WorkoutGenerationRequest(BaseModel):
    """Request for workout generation"""
    user_context: FitnessContext
    workout_type: str
    duration_minutes: int
    difficulty_level: str
    focus_areas: List[str]
    equipment_preference: Optional[str] = None
    special_requirements: List[str] = Field(default_factory=list)


class WorkoutGenerationResponse(BaseModel):
    """Response from workout generation"""
    workout_id: UUID
    name: str
    description: str
    duration_minutes: int
    difficulty_level: str
    workout_type: str
    exercises: List[Dict[str, Any]]
    warmup: List[Dict[str, Any]]
    cooldown: List[Dict[str, Any]]
    equipment_needed: List[str]
    safety_notes: List[str]
    modifications: Dict[str, List[Dict[str, Any]]]
    estimated_calories: Optional[int] = None
    total_estimated_duration_seconds: Optional[int] = None
    phase_duration_breakdown: Dict[str, int] = Field(default_factory=dict)
    agent_attribution: Dict[str, str]  # Which agents contributed to this workout
