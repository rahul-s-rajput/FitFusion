"""
Gemini API Integration Service - Enhanced with Debug Logging
Based on extensive debugging and latest google-genai SDK patterns
Compatible with google-genai>=0.1.0

Features:
- Comprehensive debug logging for raw requests/responses
- Better error handling with proper APIError catching
- Session management to prevent unclosed client warnings
- Retry logic with exponential backoff
- Model configuration based on latest test results
"""

import os
import asyncio
import logging
import json
import time
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
import traceback
from enum import Enum
from dataclasses import dataclass, field
import aiohttp

from google import genai
from google.genai import types
from google.genai import errors

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG if os.getenv('DEBUG', 'false').lower() == 'true' else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Enable detailed HTTP logging if requested
if os.getenv('GEMINI_DEBUG_HTTP', 'false').lower() == 'true':
    logging.getLogger("aiohttp.client").setLevel(logging.DEBUG)
    logging.getLogger("aiohttp.client_reqrep").setLevel(logging.DEBUG)

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
    model_type: ModelType = ModelType.GEMINI_2_0_FLASH  # Use stable 2.0 based on test results
    temperature: float = 0.7
    top_p: float = 0.8
    top_k: int = 40
    max_output_tokens: int = 8192
    timeout: int = 30
    api_version: str = "v1"  # Use stable v1
    enable_safety_settings: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    debug_requests: bool = False

@dataclass
class RequestDebugInfo:
    """Debug information for API requests"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    model: str = ""
    prompt_length: int = 0
    config: Optional[Dict[str, Any]] = None
    response_text: Optional[str] = None
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    attempt: int = 1

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
    Enhanced Gemini service with debug logging, better error handling, and session management
    """
    
    def __init__(self, config: GeminiConfig):
        self.config = config
        self.client = None
        self.session_manager = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client with API key and proper session management"""
        try:
            # Configure HTTP options with better session management
            http_options = types.HttpOptions(
                api_version=self.config.api_version
            )
            
            # Add debug logging configuration
            if self.config.debug_requests:
                logger.info("Debug logging enabled for Gemini API requests")
            
            self.client = genai.Client(
                api_key=self.config.api_key,
                http_options=http_options
            )
            logger.info(f"Gemini client initialized - Model: {self.config.model_type.value}, API: {self.config.api_version}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    def _log_request_debug(self, debug_info: RequestDebugInfo, stage: str = "request"):
        """Log detailed debug information"""
        if not self.config.debug_requests:
            return
            
        if stage == "request":
            logger.debug(f"🔄 [REQ-{debug_info.request_id}] Starting request")
            logger.debug(f"   Model: {debug_info.model}")
            logger.debug(f"   Prompt length: {debug_info.prompt_length} chars")
            logger.debug(f"   Config: {json.dumps(debug_info.config, indent=2) if debug_info.config else 'None'}")
            logger.debug(f"   Attempt: {debug_info.attempt}")
        elif stage == "response":
            logger.debug(f"✅ [REQ-{debug_info.request_id}] Response received")
            logger.debug(f"   Response time: {debug_info.response_time_ms:.2f}ms")
            logger.debug(f"   Response length: {len(debug_info.response_text or '')} chars")
            if debug_info.response_text and len(debug_info.response_text) < 500:
                logger.debug(f"   Response text: {debug_info.response_text}")
            else:
                logger.debug(f"   Response text (truncated): {debug_info.response_text[:200]}...")
        elif stage == "error":
            logger.debug(f"❌ [REQ-{debug_info.request_id}] Error occurred")
            logger.debug(f"   Error: {debug_info.error}")
            logger.debug(f"   Attempt: {debug_info.attempt}")
    
    async def _make_request_with_retry(
        self, 
        request_func, 
        debug_info: RequestDebugInfo,
        *args,
        **kwargs
    ) -> Any:
        """Make a request with retry logic and debug logging"""
        last_error = None
        
        for attempt in range(1, self.config.max_retries + 1):
            debug_info.attempt = attempt
            start_time = time.time()
            
            try:
                self._log_request_debug(debug_info, "request")
                
                # Make the actual request
                response = await request_func(*args, **kwargs)
                
                # Log successful response
                debug_info.response_time_ms = (time.time() - start_time) * 1000
                if hasattr(response, 'text'):
                    debug_info.response_text = response.text
                self._log_request_debug(debug_info, "response")
                
                return response
                
            except errors.APIError as e:
                last_error = e
                debug_info.error = f"APIError {e.code}: {e.message}"
                self._log_request_debug(debug_info, "error")
                
                # Check if we should retry
                if attempt < self.config.max_retries and self._should_retry(e):
                    delay = self.config.retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                    logger.warning(f"API error {e.code}, retrying in {delay}s (attempt {attempt}/{self.config.max_retries})")
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise
                    
            except Exception as e:
                last_error = e
                debug_info.error = str(e)
                self._log_request_debug(debug_info, "error")
                
                # For non-API errors, retry only on specific conditions
                if attempt < self.config.max_retries and self._should_retry_generic(e):
                    delay = self.config.retry_delay * (2 ** (attempt - 1))
                    logger.warning(f"Request error, retrying in {delay}s (attempt {attempt}/{self.config.max_retries}): {e}")
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise
        
        # If we get here, all retries failed
        raise last_error
    
    def _should_retry(self, error: errors.APIError) -> bool:
        """Determine if an API error should trigger a retry"""
        # Retry on rate limits, server errors, timeouts
        retry_codes = [429, 500, 502, 503, 504]
        return error.code in retry_codes
    
    def _should_retry_generic(self, error: Exception) -> bool:
        """Determine if a generic error should trigger a retry"""
        # Retry on connection errors, timeouts
        error_str = str(error).lower()
        retry_conditions = [
            'timeout', 'connection', 'network', 'temporary', 'unavailable'
        ]
        return any(condition in error_str for condition in retry_conditions)
    
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
        """Approach 1: JSON without schema with enhanced debug logging"""
        try:
            logger.debug("Trying JSON generation without schema")
            
            prompt = self._create_simple_workout_prompt(context)
            
            debug_info = RequestDebugInfo(
                model=self.config.model_type.value,
                prompt_length=len(prompt),
                config={
                    'temperature': self.config.temperature,
                    'max_output_tokens': self.config.max_output_tokens,
                    'response_mime_type': 'application/json'
                }
            )
            
            async def make_json_request():
                config = types.GenerateContentConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_output_tokens,
                    response_mime_type="application/json"
                )
                
                return await self.client.aio.models.generate_content(
                    model=self.config.model_type.value,
                    contents=prompt,
                    config=config
                )
            
            response = await self._make_request_with_retry(
                make_json_request,
                debug_info
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
                    model_used=self.config.model_type.value,
                    generation_time=debug_info.response_time_ms / 1000 if debug_info.response_time_ms else None
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
        """Generate alternative exercises with enhanced error handling and retry logic"""
        
        # Create a more detailed and specific prompt based on best practices
        equipment_str = ', '.join(available_equipment) if available_equipment else 'no equipment'
        
        prompt = f"""
You are a fitness expert. Generate 3 alternative exercises for "{exercise_name}".

Requirements:
- Target the same muscle groups as {exercise_name}
- Match the {difficulty_level} difficulty level
- Use only: {equipment_str}
- Provide clear, actionable instructions

Return your response as valid JSON with this exact structure:
{{
  "original_exercise": "{exercise_name}",
  "alternatives": [
    {{
      "name": "First alternative exercise name",
      "difficulty": "{difficulty_level}",
      "instructions": "Step-by-step instructions"
    }},
    {{
      "name": "Second alternative exercise name", 
      "difficulty": "{difficulty_level}",
      "instructions": "Step-by-step instructions"
    }},
    {{
      "name": "Third alternative exercise name",
      "difficulty": "{difficulty_level}", 
      "instructions": "Step-by-step instructions"
    }}
  ]
}}

Important: Return only valid JSON, no other text or markdown.
"""
        
        debug_info = RequestDebugInfo(
            model=self.config.model_type.value,
            prompt_length=len(prompt),
            config={
                'temperature': 0.7,
                'max_output_tokens': 1500,
                'response_mime_type': 'application/json'
            }
        )
        
        # Try multiple approaches for better reliability
        approaches = [
            self._try_alternatives_with_schema,
            self._try_alternatives_without_schema,
            self._try_alternatives_fallback
        ]
        
        for approach_func in approaches:
            try:
                result = await approach_func(exercise_name, available_equipment, difficulty_level, prompt, debug_info)
                if result.success:
                    return result
            except Exception as e:
                logger.debug(f"Approach {approach_func.__name__} failed: {e}")
                continue
        
        return GenerationResult(
            success=False,
            error_message="All alternative generation approaches failed"
        )
    
    async def _try_alternatives_with_schema(
        self, exercise_name: str, available_equipment: List[str], 
        difficulty_level: str, prompt: str, debug_info: RequestDebugInfo
    ) -> GenerationResult:
        """Try generating alternatives with simple JSON schema"""
        
        # Use a very simple schema to avoid compatibility issues
        simple_schema = {
            'type': 'OBJECT',
            'properties': {
                'original_exercise': {'type': 'STRING'},
                'alternatives': {
                    'type': 'ARRAY',
                    'items': {
                        'type': 'OBJECT',
                        'properties': {
                            'name': {'type': 'STRING'},
                            'difficulty': {'type': 'STRING'},
                            'instructions': {'type': 'STRING'}
                        }
                    }
                }
            }
        }
        
        async def make_schema_request():
            config = types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1500,
                response_mime_type="application/json",
                response_schema=simple_schema
            )
            
            return await self.client.aio.models.generate_content(
                model=self.config.model_type.value,
                contents=prompt,
                config=config
            )
        
        response = await self._make_request_with_retry(
            make_schema_request,
            debug_info
        )
        
        if response and hasattr(response, 'text') and response.text:
            alternatives_data = json.loads(response.text.strip())
            return GenerationResult(
                success=True,
                workout_data=alternatives_data,
                model_used=self.config.model_type.value,
                generation_time=debug_info.response_time_ms / 1000 if debug_info.response_time_ms else None
            )
        
        raise Exception("No valid response received")
    
    async def _try_alternatives_without_schema(
        self, exercise_name: str, available_equipment: List[str], 
        difficulty_level: str, prompt: str, debug_info: RequestDebugInfo
    ) -> GenerationResult:
        """Try generating alternatives without schema (JSON mime type only)"""
        
        async def make_json_request():
            config = types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1500,
                response_mime_type="application/json"
            )
            
            return await self.client.aio.models.generate_content(
                model=self.config.model_type.value,
                contents=prompt,
                config=config
            )
        
        response = await self._make_request_with_retry(
            make_json_request,
            debug_info
        )
        
        if response and hasattr(response, 'text') and response.text:
            text = response.text.strip()
            
            # Clean up any markdown formatting
            if text.startswith('```'):
                lines = text.split('\n')
                text = '\n'.join(lines[1:-1])  # Remove first and last lines
                if text.startswith('json'):
                    text = text[4:].strip()
            
            alternatives_data = json.loads(text)
            return GenerationResult(
                success=True,
                workout_data=alternatives_data,
                model_used=self.config.model_type.value,
                generation_time=debug_info.response_time_ms / 1000 if debug_info.response_time_ms else None
            )
        
        raise Exception("No valid response received")
    
    async def _try_alternatives_fallback(
        self, exercise_name: str, available_equipment: List[str], 
        difficulty_level: str, prompt: str, debug_info: RequestDebugInfo
    ) -> GenerationResult:
        """Fallback approach: plain text generation and manual parsing"""
        
        fallback_prompt = f"""
Generate 3 alternative exercises for "{exercise_name}" suitable for {difficulty_level} level using {', '.join(available_equipment) if available_equipment else 'no equipment'}.

Format each alternative as:
ALTERNATIVE 1: [name]
INSTRUCTIONS: [step-by-step instructions]

ALTERNATIVE 2: [name] 
INSTRUCTIONS: [step-by-step instructions]

ALTERNATIVE 3: [name]
INSTRUCTIONS: [step-by-step instructions]
"""
        
        async def make_text_request():
            config = types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1000
            )
            
            return await self.client.aio.models.generate_content(
                model=self.config.model_type.value,
                contents=fallback_prompt,
                config=config
            )
        
        response = await self._make_request_with_retry(
            make_text_request,
            debug_info
        )
        
        if response and hasattr(response, 'text') and response.text:
            # Parse the text response into JSON format
            text = response.text
            alternatives = self._parse_alternatives_text(text, exercise_name, difficulty_level)
            
            return GenerationResult(
                success=True,
                workout_data=alternatives,
                model_used=self.config.model_type.value,
                generation_time=debug_info.response_time_ms / 1000 if debug_info.response_time_ms else None
            )
        
        raise Exception("No valid response received")
    
    def _parse_alternatives_text(self, text: str, original_exercise: str, difficulty_level: str) -> Dict[str, Any]:
        """Parse text response into structured alternatives format"""
        alternatives = []
        lines = text.strip().split('\n')
        
        current_alt = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('ALTERNATIVE'):
                if current_alt and current_alt.get('name'):
                    alternatives.append(current_alt)
                    current_alt = {}
                
                # Extract name after the colon
                if ':' in line:
                    name = line.split(':', 1)[1].strip()
                    current_alt['name'] = name
                    current_alt['difficulty'] = difficulty_level
            
            elif line.startswith('INSTRUCTIONS:'):
                if current_alt:
                    instructions = line.split(':', 1)[1].strip()
                    current_alt['instructions'] = instructions
        
        # Add the last alternative
        if current_alt and current_alt.get('name'):
            alternatives.append(current_alt)
        
        # Ensure we have at least some alternatives
        while len(alternatives) < 3:
            alternatives.append({
                'name': f'Alternative exercise {len(alternatives) + 1}',
                'difficulty': difficulty_level,
                'instructions': f'Alternative to {original_exercise}'
            })
        
        return {
            'original_exercise': original_exercise,
            'alternatives': alternatives[:3]  # Limit to 3
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Enhanced health check with better error handling and debug logging"""
        debug_info = RequestDebugInfo(
            model=self.config.model_type.value,
            prompt_length=7,  # "Say OK" length
            config={'temperature': 0.1, 'max_output_tokens': 50}
        )
        
        try:
            async def make_health_request():
                config = types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=50
                )
                
                return await self.client.aio.models.generate_content(
                    model=self.config.model_type.value,
                    contents='Say "OK"',
                    config=config
                )
            
            response = await self._make_request_with_retry(
                make_health_request,
                debug_info
            )
            
            is_healthy = response and hasattr(response, 'text') and bool(response.text)
            response_text = response.text.strip() if is_healthy else None
            
            result = {
                'gemini_healthy': is_healthy,
                'model_type': self.config.model_type.value,
                'api_version': self.config.api_version,
                'response_received': response_text,
                'response_time_ms': debug_info.response_time_ms,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            if is_healthy:
                logger.info(f"Health check passed - Response: '{response_text}'")
            else:
                logger.warning(f"Health check failed - No valid response received")
                result['error'] = "No valid response received"
            
            return result
            
        except errors.APIError as e:
            logger.error(f"API Error in health check: {e.code} - {e.message}")
            return {
                'gemini_healthy': False,
                'error': f"API Error {e.code}: {e.message}",
                'error_code': e.code,
                'model_type': self.config.model_type.value,
                'api_version': self.config.api_version,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'gemini_healthy': False,
                'error': str(e),
                'error_type': type(e).__name__,
                'model_type': self.config.model_type.value,
                'api_version': self.config.api_version,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def close(self):
        """Close the service and clean up resources"""
        try:
            # Close any active sessions or connections
            if self.client and hasattr(self.client, 'aio'):
                # Try to close any underlying HTTP sessions
                try:
                    if hasattr(self.client.aio, '_transport'):
                        transport = self.client.aio._transport
                        if hasattr(transport, 'close'):
                            await transport.close()
                except Exception as e:
                    logger.debug(f"Error closing transport: {e}")
            
            self.client = None
            logger.info("Gemini service closed successfully")
            
        except Exception as e:
            logger.warning(f"Error during service cleanup: {e}")
            self.client = None

# Global service management
_gemini_service: Optional[GeminiServiceFixed] = None

def get_gemini_service() -> GeminiServiceFixed:
    """Get the global Gemini service instance with enhanced configuration"""
    global _gemini_service
    if _gemini_service is None:
        # Get model type from environment (use working model based on test results)
        model_name = os.getenv('GEMINI_MODEL_TYPE', 'gemini-2.0-flash-001')
        model_type = ModelType.GEMINI_2_0_FLASH  # Default to working model
        
        # Map environment model name to enum
        for mt in ModelType:
            if mt.value == model_name:
                model_type = mt
                break
        
        config = GeminiConfig(
            api_key=os.getenv('GEMINI_API_KEY', ''),
            model_type=model_type,
            temperature=float(os.getenv('GEMINI_TEMPERATURE', '0.7')),
            max_output_tokens=int(os.getenv('GEMINI_MAX_TOKENS', '8192')),
            api_version=os.getenv('GEMINI_API_VERSION', 'v1'),  # Use stable API
            enable_safety_settings=os.getenv('GEMINI_SAFETY', 'true').lower() == 'true',
            max_retries=int(os.getenv('GEMINI_MAX_RETRIES', '3')),
            retry_delay=float(os.getenv('GEMINI_RETRY_DELAY', '1.0')),
            debug_requests=os.getenv('GEMINI_DEBUG_REQUESTS', 'false').lower() == 'true'
        )
        _gemini_service = GeminiServiceFixed(config)
        logger.info(f"Gemini service initialized with model: {config.model_type.value}")
    return _gemini_service

def initialize_gemini():
    """Initialize the Gemini service"""
    service = get_gemini_service()
    logger.info("Gemini service (fixed version) initialized")
    return service

# Make it backward compatible with old import
GeminiService = GeminiServiceFixed
