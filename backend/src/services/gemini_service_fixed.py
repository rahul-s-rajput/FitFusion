"""
Gemini API Integration Service - Fixed Version
Based on extensive debugging and latest google-genai SDK patterns
Compatible with google-genai>=0.1.0
"""

import os
import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
import traceback
from enum import Enum
from dataclasses import dataclass

from google import genai
from google.genai import types
from google.genai import errors

# Configure logging
logger = logging.getLogger(__name__)

class ModelType(str, Enum):
    """Available Gemini model types - using correct names"""
    GEMINI_2_5_FLASH = "gemini-2.5-flash"  # Latest stable
    GEMINI_2_0_FLASH = "gemini-2.0-flash-001"  # Stable 2.0
    GEMINI_1_5_FLASH = "gemini-1.5-flash"  # Older stable
    GEMINI_2_0_FLASH_EXP = "gemini-2.0-flash-exp"  # Experimental

@dataclass
class GeminiConfig:
    """Gemini API configuration"""
    api_key: str
    model_type: ModelType = ModelType.GEMINI_2_5_FLASH  # Use stable 2.0
    temperature: float = 0.7
    top_p: float = 0.8
    top_k: int = 40
    max_output_tokens: int = 8192
    timeout: int = 30
    api_version: str = "v1"  # Use stable v1
    enable_safety_settings: bool = True

@dataclass
class WorkoutContext:
    """Context information for workout generation"""
    user_id: str
    fitness_goals: List[str]
    experience_level: str
    available_equipment: List[Dict[str, Any]]
    space_constraints: Dict[str, Any]
    time_constraints: Dict[str, Any]
    physical_attributes: Dict[str, Any]
    preferences: Dict[str, Any]
    workout_type: str
    duration_minutes: int
    difficulty_level: str
    focus_areas: List[str]
    special_requirements: List[str]

@dataclass
class GenerationResult:
    """Result of workout generation"""
    success: bool
    workout_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None
    generation_time: Optional[float] = None
    model_used: Optional[str] = None

class GeminiServiceFixed:
    """
    Fixed Gemini service with fallback approaches and better error handling
    """
    
    def __init__(self, config: GeminiConfig):
        self.config = config
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client with API key"""
        try:
            # Use stable v1 API by default
            http_options = types.HttpOptions(api_version=self.config.api_version)
            self.client = genai.Client(
                api_key=self.config.api_key,
                http_options=http_options
            )
            logger.info(f"Gemini client initialized - Model: {self.config.model_type.value}, API: {self.config.api_version}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    def _create_simple_workout_prompt(self, context: WorkoutContext) -> str:
        """Create a simple prompt for workout generation"""
        
        equipment_list = ", ".join([eq.get('name', 'Unknown') for eq in context.available_equipment]) if context.available_equipment else "No equipment"
        
        prompt = f"""
Generate a {context.duration_minutes}-minute {context.workout_type} workout for {context.experience_level} level.

Requirements:
- Difficulty: {context.difficulty_level}
- Equipment: {equipment_list}
- Focus areas: {', '.join(context.focus_areas)}

Respond with a JSON object containing:
{{
  "workout_session": {{
    "title": "workout title",
    "description": "brief description",
    "total_duration": {context.duration_minutes},
    "difficulty_level": "{context.difficulty_level}",
    "warmup": [
      {{"name": "exercise", "duration_seconds": 30, "instructions": "how to"}}
    ],
    "main_exercises": [
      {{"name": "exercise", "sets": 3, "reps": 10, "instructions": "how to"}}
    ],
    "cooldown": [
      {{"name": "exercise", "duration_seconds": 30, "instructions": "how to"}}
    ]
  }}
}}

Provide valid JSON only.
"""
        return prompt
    
    async def generate_workout(self, context: WorkoutContext) -> GenerationResult:
        """Generate a personalized workout using multiple fallback approaches"""
        start_time = datetime.now()
        
        # Try different approaches in order
        approaches = [
            self._try_json_no_schema,
            self._try_dict_schema,
            self._try_simple_generation
        ]
        
        for approach_func in approaches:
            result = await approach_func(context)
            if result.success:
                result.generation_time = (datetime.now() - start_time).total_seconds()
                return result
        
        # All approaches failed
        return GenerationResult(
            success=False,
            error_message="All generation approaches failed",
            generation_time=(datetime.now() - start_time).total_seconds(),
            model_used=self.config.model_type.value
        )
    
    async def _try_json_no_schema(self, context: WorkoutContext) -> GenerationResult:
        """Approach 1: JSON without schema"""
        try:
            logger.debug("Trying JSON generation without schema")
            
            prompt = self._create_simple_workout_prompt(context)
            
            config = types.GenerateContentConfig(
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_output_tokens,
                response_mime_type="application/json"
            )
            
            response = await self.client.aio.models.generate_content(
                model=self.config.model_type.value,
                contents=prompt,
                config=config
            )
            
            if response and hasattr(response, 'text') and response.text:
                text = response.text.strip()
                
                # Remove markdown if present
                if text.startswith('```'):
                    text = text.split('```')[1]
                    if text.startswith('json'):
                        text = text[4:]
                    text = text.rsplit('```', 1)[0]
                
                workout_data = json.loads(text)
                logger.debug("Successfully generated workout with JSON approach")
                return GenerationResult(
                    success=True,
                    workout_data=workout_data,
                    model_used=self.config.model_type.value
                )
                
        except json.JSONDecodeError as e:
            logger.debug(f"JSON parse error in approach 1: {e}")
        except Exception as e:
            logger.debug(f"Error in approach 1: {e}")
        
        return GenerationResult(success=False, error_message="JSON approach failed")
    
    async def _try_dict_schema(self, context: WorkoutContext) -> GenerationResult:
        """Approach 2: Dictionary schema"""
        try:
            logger.debug("Trying generation with dictionary schema")
            
            prompt = self._create_simple_workout_prompt(context)
            
            # Simple dictionary schema
            schema = {
                'type': 'OBJECT',
                'properties': {
                    'workout_session': {
                        'type': 'OBJECT',
                        'properties': {
                            'title': {'type': 'STRING'},
                            'description': {'type': 'STRING'},
                            'total_duration': {'type': 'INTEGER'},
                            'difficulty_level': {'type': 'STRING'}
                        }
                    }
                }
            }
            
            config = types.GenerateContentConfig(
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_output_tokens,
                response_mime_type='application/json',
                response_schema=schema
            )
            
            response = await self.client.aio.models.generate_content(
                model=self.config.model_type.value,
                contents=prompt,
                config=config
            )
            
            if response and hasattr(response, 'text') and response.text:
                workout_data = json.loads(response.text)
                logger.debug("Successfully generated workout with dict schema approach")
                return GenerationResult(
                    success=True,
                    workout_data=workout_data,
                    model_used=self.config.model_type.value
                )
                
        except Exception as e:
            logger.debug(f"Error in approach 2: {e}")
        
        return GenerationResult(success=False, error_message="Dict schema approach failed")
    
    async def _try_simple_generation(self, context: WorkoutContext) -> GenerationResult:
        """Approach 3: Simple text generation and parse"""
        try:
            logger.debug("Trying simple text generation")
            
            prompt = f"""
Create a {context.duration_minutes}-minute {context.workout_type} workout for {context.experience_level} level.

Format your response as:
TITLE: [workout title]
WARMUP:
- [exercise 1] (duration)
- [exercise 2] (duration)
MAIN:
- [exercise 1] (sets x reps)
- [exercise 2] (sets x reps)
COOLDOWN:
- [exercise 1] (duration)
- [exercise 2] (duration)
"""
            
            config = types.GenerateContentConfig(
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_output_tokens
            )
            
            response = await self.client.aio.models.generate_content(
                model=self.config.model_type.value,
                contents=prompt,
                config=config
            )
            
            if response and hasattr(response, 'text') and response.text:
                # Parse the text response into structured data
                text = response.text
                workout_data = self._parse_text_workout(text, context)
                logger.debug("Successfully generated workout with text approach")
                return GenerationResult(
                    success=True,
                    workout_data=workout_data,
                    model_used=self.config.model_type.value
                )
                
        except Exception as e:
            logger.debug(f"Error in approach 3: {e}")
        
        return GenerationResult(success=False, error_message="Text generation approach failed")
    
    def _parse_text_workout(self, text: str, context: WorkoutContext) -> Dict[str, Any]:
        """Parse text workout into structured format"""
        lines = text.strip().split('\n')
        
        workout = {
            "workout_session": {
                "title": f"{context.workout_type.title()} Workout",
                "description": f"A {context.duration_minutes}-minute {context.difficulty_level} {context.workout_type} workout",
                "total_duration": context.duration_minutes,
                "difficulty_level": context.difficulty_level,
                "workout_type": context.workout_type,
                "warmup": [],
                "main_exercises": [],
                "cooldown": []
            }
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("TITLE:"):
                workout["workout_session"]["title"] = line.replace("TITLE:", "").strip()
            elif "WARMUP" in line.upper():
                current_section = "warmup"
            elif "MAIN" in line.upper():
                current_section = "main_exercises"
            elif "COOLDOWN" in line.upper():
                current_section = "cooldown"
            elif line.startswith("-") and current_section:
                exercise_text = line[1:].strip()
                
                if current_section == "warmup" or current_section == "cooldown":
                    # Parse duration exercises
                    parts = exercise_text.split("(")
                    name = parts[0].strip()
                    duration = 30  # default
                    if len(parts) > 1:
                        duration_str = parts[1].replace(")", "").strip()
                        # Extract number from duration string
                        import re
                        numbers = re.findall(r'\d+', duration_str)
                        if numbers:
                            duration = int(numbers[0])
                    
                    workout["workout_session"][current_section].append({
                        "name": name,
                        "duration_seconds": duration,
                        "instructions": f"Perform {name}"
                    })
                
                elif current_section == "main_exercises":
                    # Parse sets/reps exercises
                    parts = exercise_text.split("(")
                    name = parts[0].strip()
                    sets = 3  # default
                    reps = 10  # default
                    if len(parts) > 1:
                        sets_reps = parts[1].replace(")", "").strip()
                        # Parse "3 x 10" or similar
                        import re
                        numbers = re.findall(r'\d+', sets_reps)
                        if len(numbers) >= 2:
                            sets = int(numbers[0])
                            reps = int(numbers[1])
                        elif len(numbers) == 1:
                            reps = int(numbers[0])
                    
                    workout["workout_session"][current_section].append({
                        "name": name,
                        "sets": sets,
                        "reps": reps,
                        "instructions": f"Perform {name}"
                    })
        
        # Ensure we have at least some exercises
        if not workout["workout_session"]["warmup"]:
            workout["workout_session"]["warmup"].append({
                "name": "Light cardio",
                "duration_seconds": 60,
                "instructions": "Start with light cardio to warm up"
            })
        
        if not workout["workout_session"]["main_exercises"]:
            workout["workout_session"]["main_exercises"].append({
                "name": "Bodyweight exercise",
                "sets": 3,
                "reps": 10,
                "instructions": "Perform bodyweight exercises"
            })
        
        if not workout["workout_session"]["cooldown"]:
            workout["workout_session"]["cooldown"].append({
                "name": "Stretching",
                "duration_seconds": 60,
                "instructions": "Cool down with stretching"
            })
        
        return workout
    
    async def generate_quick_workout(
        self,
        workout_type: str,
        duration_minutes: int,
        difficulty_level: str,
        equipment_available: bool = False
    ) -> GenerationResult:
        """Generate a quick workout"""
        
        # Create a simplified context
        context = WorkoutContext(
            user_id="quick",
            fitness_goals=["general fitness"],
            experience_level=difficulty_level,
            available_equipment=[{"name": "dumbbells"}] if equipment_available else [],
            space_constraints={},
            time_constraints={},
            physical_attributes={},
            preferences={},
            workout_type=workout_type,
            duration_minutes=duration_minutes,
            difficulty_level=difficulty_level,
            focus_areas=["general"],
            special_requirements=[]
        )
        
        return await self.generate_workout(context)
    
    async def generate_motivational_message(
        self,
        user_context: Dict[str, Any],
        workout_progress: Dict[str, Any]
    ) -> str:
        """Generate a personalized motivational message"""
        
        prompt = f"""
Generate a short motivational fitness message (2-3 sentences) based on:
User goals: {user_context.get('goals', [])}
User level: {user_context.get('level', 'beginner')}
Progress: {workout_progress}

Be encouraging and specific. Keep it positive.
"""
        
        try:
            config = types.GenerateContentConfig(
                temperature=0.8,
                max_output_tokens=150
            )
            
            response = await self.client.aio.models.generate_content(
                model=self.config.model_type.value,
                contents=prompt,
                config=config
            )
            
            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
            
        except Exception as e:
            logger.debug(f"Error generating motivational message: {e}")
        
        # Fallback message
        return "Keep pushing towards your fitness goals! Every workout counts."
    
    async def generate_exercise_alternatives(
        self, 
        exercise_name: str, 
        available_equipment: List[str],
        difficulty_level: str = "intermediate"
    ) -> GenerationResult:
        """Generate alternative exercises"""
        
        prompt = f"""
List 3 alternative exercises for "{exercise_name}" that:
- Target the same muscles
- Are {difficulty_level} level
- Use: {', '.join(available_equipment) if available_equipment else 'no equipment'}

Format as JSON:
{{
  "original_exercise": "{exercise_name}",
  "alternatives": [
    {{
      "name": "alternative name",
      "difficulty": "level",
      "instructions": "how to perform"
    }}
  ]
}}
"""
        
        try:
            config = types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1000,
                response_mime_type="application/json"
            )
            
            response = await self.client.aio.models.generate_content(
                model=self.config.model_type.value,
                contents=prompt,
                config=config
            )
            
            if response and hasattr(response, 'text') and response.text:
                text = response.text.strip()
                
                # Remove markdown if present
                if text.startswith('```'):
                    text = text.split('```')[1]
                    if text.startswith('json'):
                        text = text[4:]
                    text = text.rsplit('```', 1)[0]
                
                alternatives_data = json.loads(text)
                return GenerationResult(
                    success=True,
                    workout_data=alternatives_data,
                    model_used=self.config.model_type.value
                )
                
        except Exception as e:
            logger.debug(f"Error generating alternatives: {e}")
        
        return GenerationResult(
            success=False,
            error_message="Could not generate alternatives"
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Simple health check"""
        try:
            config = types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=10
            )
            
            response = await self.client.aio.models.generate_content(
                model=self.config.model_type.value,
                contents='Say "OK"',
                config=config
            )
            
            is_healthy = response and hasattr(response, 'text') and bool(response.text)
            
            return {
                'gemini_healthy': is_healthy,
                'model_type': self.config.model_type.value,
                'api_version': self.config.api_version,
                'response_received': response.text if is_healthy else None,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except errors.APIError as e:
            logger.error(f"API Error in health check: {e.code} - {e.message}")
            return {
                'gemini_healthy': False,
                'error': f"API Error {e.code}: {e.message}",
                'model_type': self.config.model_type.value,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'gemini_healthy': False,
                'error': str(e),
                'model_type': self.config.model_type.value,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def close(self):
        """Close the service"""
        self.client = None
        logger.info("Gemini service closed")

# Global service management
_gemini_service: Optional[GeminiServiceFixed] = None

def get_gemini_service() -> GeminiServiceFixed:
    """Get the global Gemini service instance"""
    global _gemini_service
    if _gemini_service is None:
        config = GeminiConfig(
            api_key=os.getenv('GEMINI_API_KEY', ''),
            model_type=ModelType.GEMINI_2_0_FLASH,  # Use stable model
            temperature=float(os.getenv('GEMINI_TEMPERATURE', '0.7')),
            max_output_tokens=int(os.getenv('GEMINI_MAX_TOKENS', '8192')),
            api_version=os.getenv('GEMINI_API_VERSION', 'v1'),  # Use stable API
            enable_safety_settings=os.getenv('GEMINI_SAFETY', 'true').lower() == 'true'
        )
        _gemini_service = GeminiServiceFixed(config)
    return _gemini_service

def initialize_gemini():
    """Initialize the Gemini service"""
    service = get_gemini_service()
    logger.info("Gemini service (fixed version) initialized")
    return service

# Make it backward compatible with old import
GeminiService = GeminiServiceFixed
