"""
Gemini API Debug Service - Enhanced with detailed logging and multiple approaches
Compatible with google-genai>=0.1.0
"""

import os
import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass
import traceback

from google import genai
from google.genai import types
from google.genai import errors
from pydantic import BaseModel, Field
from typing import List

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ModelType(str, Enum):
    """Available Gemini model types"""
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_2_0_FLASH = "gemini-2.0-flash-001"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"

@dataclass
class GeminiConfig:
    """Gemini API configuration"""
    api_key: str
    model_type: ModelType = ModelType.GEMINI_2_5_FLASH
    temperature: float = 0.7
    top_p: float = 0.8
    top_k: int = 40
    max_output_tokens: int = 8192
    timeout: int = 30
    api_version: str = "v1beta"  # Try v1beta first
    debug_mode: bool = True

@dataclass
class GenerationResult:
    """Result of generation"""
    success: bool
    data: Optional[Any] = None
    error_message: Optional[str] = None
    raw_response: Optional[str] = None
    debug_info: Optional[Dict[str, Any]] = None

class GeminiDebugService:
    """Debug version of Gemini service with extensive logging"""
    
    def __init__(self, config: GeminiConfig):
        self.config = config
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client with API key and version"""
        try:
            logger.info(f"Initializing Gemini client with API version: {self.config.api_version}")
            
            # Initialize with specific API version
            http_options = types.HttpOptions(api_version=self.config.api_version)
            self.client = genai.Client(
                api_key=self.config.api_key,
                http_options=http_options
            )
            
            logger.info(f"✅ Client initialized successfully")
            logger.info(f"   Model: {self.config.model_type.value}")
            logger.info(f"   API Version: {self.config.api_version}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize client: {e}")
            logger.error(traceback.format_exc())
            raise
    
    async def test_simple_text(self) -> GenerationResult:
        """Test 1: Simple text generation without any structure"""
        logger.info("\n" + "="*60)
        logger.info("TEST 1: SIMPLE TEXT GENERATION")
        logger.info("="*60)
        
        try:
            prompt = 'Say "Hello World"'
            logger.info(f"Prompt: {prompt}")
            
            # Minimal config
            config = types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=50
            )
            
            logger.info(f"Config: temperature={config.temperature}, max_tokens={config.max_output_tokens}")
            
            # Make request
            response = await self.client.aio.models.generate_content(
                model=self.config.model_type.value,
                contents=prompt,
                config=config
            )
            
            # Log raw response attributes
            logger.info("Response attributes:")
            for attr in dir(response):
                if not attr.startswith('_'):
                    try:
                        value = getattr(response, attr)
                        if not callable(value):
                            logger.debug(f"  {attr}: {type(value).__name__}")
                            if attr in ['text', 'parts']:
                                logger.info(f"  {attr}: {value}")
                    except Exception as e:
                        logger.debug(f"  {attr}: <error accessing: {e}>")
            
            # Check response
            if response and hasattr(response, 'text'):
                text = response.text
                logger.info(f"✅ Response text: {text}")
                return GenerationResult(
                    success=True,
                    data=text,
                    raw_response=text
                )
            else:
                logger.error("❌ No text in response")
                return GenerationResult(
                    success=False,
                    error_message="No text in response",
                    raw_response=str(response)
                )
                
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            logger.error(traceback.format_exc())
            return GenerationResult(
                success=False,
                error_message=str(e),
                debug_info={"traceback": traceback.format_exc()}
            )
    
    async def test_json_without_schema(self) -> GenerationResult:
        """Test 2: JSON generation without Pydantic schema"""
        logger.info("\n" + "="*60)
        logger.info("TEST 2: JSON WITHOUT SCHEMA")
        logger.info("="*60)
        
        try:
            prompt = """
Generate a JSON object with this structure:
{
  "exercise": "name of exercise",
  "duration": 30,
  "difficulty": "beginner"
}

Generate exactly this structure with sample data.
"""
            logger.info(f"Prompt: {prompt[:100]}...")
            
            # Config for JSON without schema
            config = types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=200,
                response_mime_type="application/json"
            )
            
            logger.info(f"Config: response_mime_type={config.response_mime_type}")
            
            response = await self.client.aio.models.generate_content(
                model=self.config.model_type.value,
                contents=prompt,
                config=config
            )
            
            if response and hasattr(response, 'text'):
                text = response.text
                logger.info(f"Raw response text: {text}")
                
                # Try to parse JSON
                try:
                    json_data = json.loads(text)
                    logger.info(f"✅ Parsed JSON: {json_data}")
                    return GenerationResult(
                        success=True,
                        data=json_data,
                        raw_response=text
                    )
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON parse error: {e}")
                    return GenerationResult(
                        success=False,
                        error_message=f"JSON parse error: {e}",
                        raw_response=text
                    )
            else:
                logger.error("❌ No text in response")
                return GenerationResult(
                    success=False,
                    error_message="No text in response"
                )
                
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            logger.error(traceback.format_exc())
            return GenerationResult(
                success=False,
                error_message=str(e),
                debug_info={"traceback": traceback.format_exc()}
            )
    
    async def test_dict_schema(self) -> GenerationResult:
        """Test 3: JSON with dictionary schema (not Pydantic)"""
        logger.info("\n" + "="*60)
        logger.info("TEST 3: JSON WITH DICT SCHEMA")
        logger.info("="*60)
        
        try:
            prompt = "Generate information about a simple exercise"
            
            # Dictionary schema
            schema = {
                'type': 'OBJECT',
                'properties': {
                    'name': {'type': 'STRING'},
                    'duration_seconds': {'type': 'INTEGER'},
                    'difficulty': {'type': 'STRING'}
                },
                'required': ['name', 'duration_seconds', 'difficulty']
            }
            
            logger.info(f"Schema: {json.dumps(schema, indent=2)}")
            
            config = types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=300,
                response_mime_type='application/json',
                response_schema=schema
            )
            
            response = await self.client.aio.models.generate_content(
                model=self.config.model_type.value,
                contents=prompt,
                config=config
            )
            
            if response and hasattr(response, 'text'):
                text = response.text
                logger.info(f"Raw response: {text}")
                
                try:
                    json_data = json.loads(text)
                    logger.info(f"✅ Parsed JSON: {json_data}")
                    return GenerationResult(
                        success=True,
                        data=json_data,
                        raw_response=text
                    )
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON parse error: {e}")
                    return GenerationResult(
                        success=False,
                        error_message=f"JSON parse error: {e}",
                        raw_response=text
                    )
            else:
                logger.error("❌ No text in response")
                return GenerationResult(
                    success=False,
                    error_message="No text in response"
                )
                
        except errors.APIError as e:
            logger.error(f"❌ API Error: code={e.code}, message={e.message}")
            return GenerationResult(
                success=False,
                error_message=f"API Error {e.code}: {e.message}"
            )
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            logger.error(traceback.format_exc())
            return GenerationResult(
                success=False,
                error_message=str(e),
                debug_info={"traceback": traceback.format_exc()}
            )
    
    async def test_simple_pydantic(self) -> GenerationResult:
        """Test 4: Simple Pydantic model"""
        logger.info("\n" + "="*60)
        logger.info("TEST 4: SIMPLE PYDANTIC MODEL")
        logger.info("="*60)
        
        try:
            # Very simple Pydantic model
            class SimpleExercise(BaseModel):
                name: str
                duration: int
                
            prompt = "Generate a simple exercise with name and duration in seconds"
            
            logger.info(f"Pydantic model: SimpleExercise")
            logger.info(f"Model fields: {SimpleExercise.model_fields}")
            
            config = types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=200,
                response_mime_type='application/json',
                response_schema=SimpleExercise
            )
            
            response = await self.client.aio.models.generate_content(
                model=self.config.model_type.value,
                contents=prompt,
                config=config
            )
            
            if response:
                # Check different response attributes
                if hasattr(response, 'text'):
                    text = response.text
                    logger.info(f"Response text: {text}")
                    
                    try:
                        json_data = json.loads(text)
                        logger.info(f"✅ Parsed JSON: {json_data}")
                        return GenerationResult(
                            success=True,
                            data=json_data,
                            raw_response=text
                        )
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON parse error: {e}")
                
                if hasattr(response, 'parsed'):
                    parsed = response.parsed
                    logger.info(f"Response parsed: {parsed}")
                    if parsed:
                        return GenerationResult(
                            success=True,
                            data=parsed,
                            raw_response=str(parsed)
                        )
                
                # Check candidates
                if hasattr(response, 'candidates'):
                    logger.info(f"Response has {len(response.candidates)} candidates")
                    for i, candidate in enumerate(response.candidates):
                        logger.debug(f"Candidate {i}: {candidate}")
                
                logger.error("❌ Could not extract data from response")
                return GenerationResult(
                    success=False,
                    error_message="Could not extract data from response",
                    raw_response=str(response)
                )
            else:
                logger.error("❌ Empty response")
                return GenerationResult(
                    success=False,
                    error_message="Empty response"
                )
                
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            logger.error(traceback.format_exc())
            return GenerationResult(
                success=False,
                error_message=str(e),
                debug_info={"traceback": traceback.format_exc()}
            )
    
    async def test_different_models(self) -> Dict[str, GenerationResult]:
        """Test 5: Try different models"""
        logger.info("\n" + "="*60)
        logger.info("TEST 5: DIFFERENT MODELS")
        logger.info("="*60)
        
        results = {}
        models_to_test = [
            "gemini-2.5-flash",
            "gemini-2.0-flash-001",
            "gemini-1.5-flash"
        ]
        
        for model in models_to_test:
            logger.info(f"\nTesting model: {model}")
            try:
                response = await self.client.aio.models.generate_content(
                    model=model,
                    contents='Say "OK"',
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=10
                    )
                )
                
                if response and hasattr(response, 'text') and response.text:
                    logger.info(f"✅ {model}: {response.text}")
                    results[model] = GenerationResult(
                        success=True,
                        data=response.text
                    )
                else:
                    logger.error(f"❌ {model}: No text in response")
                    results[model] = GenerationResult(
                        success=False,
                        error_message="No text in response"
                    )
                    
            except Exception as e:
                logger.error(f"❌ {model}: {e}")
                results[model] = GenerationResult(
                    success=False,
                    error_message=str(e)
                )
        
        return results
    
    async def test_api_versions(self) -> Dict[str, GenerationResult]:
        """Test 6: Try different API versions"""
        logger.info("\n" + "="*60)
        logger.info("TEST 6: DIFFERENT API VERSIONS")
        logger.info("="*60)
        
        results = {}
        versions = ["v1", "v1beta", "v1alpha"]
        
        for version in versions:
            logger.info(f"\nTesting API version: {version}")
            try:
                # Create new client with different API version
                http_options = types.HttpOptions(api_version=version)
                test_client = genai.Client(
                    api_key=self.config.api_key,
                    http_options=http_options
                )
                
                response = await test_client.aio.models.generate_content(
                    model=self.config.model_type.value,
                    contents='Say "OK"',
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=10
                    )
                )
                
                if response and hasattr(response, 'text') and response.text:
                    logger.info(f"✅ {version}: {response.text}")
                    results[version] = GenerationResult(
                        success=True,
                        data=response.text
                    )
                else:
                    logger.error(f"❌ {version}: No text in response")
                    results[version] = GenerationResult(
                        success=False,
                        error_message="No text in response"
                    )
                    
            except Exception as e:
                logger.error(f"❌ {version}: {e}")
                results[version] = GenerationResult(
                    success=False,
                    error_message=str(e)
                )
        
        return results
    
    async def close(self):
        """Close the service"""
        self.client = None
        logger.info("Service closed")

async def run_all_tests(api_key: str):
    """Run all debug tests"""
    print("\n" + "🔍"*30)
    print("GEMINI SERVICE DEBUG TESTS")
    print("🔍"*30)
    
    # Initialize service
    config = GeminiConfig(
        api_key=api_key,
        model_type=ModelType.GEMINI_2_5_FLASH,
        temperature=0.5,
        max_output_tokens=500,
        api_version="v1beta",
        debug_mode=True
    )
    
    service = GeminiDebugService(config)
    
    # Run tests
    tests = [
        ("Simple Text", service.test_simple_text),
        ("JSON Without Schema", service.test_json_without_schema),
        ("Dict Schema", service.test_dict_schema),
        ("Simple Pydantic", service.test_simple_pydantic),
    ]
    
    results = {}
    for name, test_func in tests:
        result = await test_func()
        results[name] = result
    
    # Test different models
    model_results = await service.test_different_models()
    results["Models"] = model_results
    
    # Test API versions
    version_results = await service.test_api_versions()
    results["API Versions"] = version_results
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        if isinstance(result, dict):
            # Model or version results
            print(f"\n{test_name}:")
            for sub_name, sub_result in result.items():
                status = "✅" if sub_result.success else "❌"
                print(f"  {status} {sub_name}: {sub_result.error_message if not sub_result.success else 'Success'}")
        else:
            status = "✅" if result.success else "❌"
            print(f"{status} {test_name}: {result.error_message if not result.success else 'Success'}")
    
    await service.close()
    
    return results

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ No GEMINI_API_KEY found")
    else:
        asyncio.run(run_all_tests(api_key))
