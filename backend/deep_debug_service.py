#!/usr/bin/env python3
"""
Deep debug script to understand the service async client issue
"""

import os
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def deep_debug_service():
    """Deep debug the service issue"""
    
    print("🔍 Deep Debug: Service Async Client Issue")
    print("=" * 60)
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No GEMINI_API_KEY found")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    try:
        from google import genai
        from google.genai import types
        from src.services.gemini_service import GeminiService, GeminiConfig, ModelType
        
        # Test 1: Check if client.aio exists
        print("\n📝 Test 1: Check client.aio attribute")
        print("-" * 40)
        
        test_client = genai.Client(api_key=api_key)
        
        print(f"Client type: {type(test_client)}")
        print(f"Has 'aio' attr: {hasattr(test_client, 'aio')}")
        
        if hasattr(test_client, 'aio'):
            print(f"aio type: {type(test_client.aio)}")
            print(f"Has 'models' attr: {hasattr(test_client.aio, 'models')}")
            
            if hasattr(test_client.aio, 'models'):
                print(f"aio.models type: {type(test_client.aio.models)}")
                print(f"Has 'generate_content' attr: {hasattr(test_client.aio.models, 'generate_content')}")
        
        # Test 2: Test direct async call
        print("\n📝 Test 2: Direct async call with test client")
        print("-" * 40)
        
        try:
            response = await test_client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents='Say "Direct test OK"'
            )
            print(f"✅ Direct call worked: {response.text if response else 'None'}")
        except Exception as e:
            print(f"❌ Direct call failed: {e}")
        
        # Test 3: Create service and check its client
        print("\n📝 Test 3: Service client inspection")
        print("-" * 40)
        
        config = GeminiConfig(
            api_key=api_key,
            model_type=ModelType.GEMINI_2_5_FLASH,
            temperature=0.1,
            max_output_tokens=100
        )
        
        service = GeminiService(config)
        
        print(f"Service client type: {type(service.client)}")
        print(f"Service client has 'aio': {hasattr(service.client, 'aio')}")
        
        if hasattr(service.client, 'aio'):
            print(f"Service client.aio type: {type(service.client.aio)}")
            print(f"Service client.aio has 'models': {hasattr(service.client.aio, 'models')}")
            
            if hasattr(service.client.aio, 'models'):
                print(f"Service client.aio.models type: {type(service.client.aio.models)}")
                print(f"Has 'generate_content': {hasattr(service.client.aio.models, 'generate_content')}")
        
        # Test 4: Try service client directly
        print("\n📝 Test 4: Service client direct call")
        print("-" * 40)
        
        try:
            test_config = types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=10
            )
            
            response = await service.client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents='Say "Service client OK"',
                config=test_config
            )
            
            print(f"✅ Service client call worked: {response.text if response else 'None'}")
        except AttributeError as ae:
            print(f"❌ AttributeError: {ae}")
            print("   This means client.aio doesn't exist or has wrong structure")
        except Exception as e:
            print(f"❌ Service client call failed: {e}")
            print(f"   Error type: {type(e).__name__}")
        
        # Test 5: Call service health_check
        print("\n📝 Test 5: Service health_check method")
        print("-" * 40)
        
        try:
            result = await service.health_check()
            print(f"Health check result: {result}")
            
            if not result.get('gemini_healthy'):
                # Let's manually trace through the health_check
                print("\n   Manual trace of health_check:")
                
                test_prompt = 'Say "OK"'
                config = types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=10
                )
                
                print(f"   Prompt: {test_prompt}")
                print(f"   Config: {config}")
                print(f"   Model: {service.config.model_type.value}")
                
                try:
                    print("   Attempting manual call...")
                    response = await service.client.aio.models.generate_content(
                        model=service.config.model_type.value,
                        contents=test_prompt,
                        config=config
                    )
                    print(f"   Manual response: {response.text if response else 'None'}")
                except Exception as manual_error:
                    print(f"   Manual error: {manual_error}")
                    print(f"   Error type: {type(manual_error).__name__}")
                    
                    # Check if it's an import error or module issue
                    import traceback
                    print("\n   Full traceback:")
                    traceback.print_exc()
                    
        except Exception as e:
            print(f"❌ health_check error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 6: Check imports and module structure
        print("\n📝 Test 6: Module structure check")
        print("-" * 40)
        
        print(f"genai module: {genai}")
        print(f"genai.__version__ (if exists): {getattr(genai, '__version__', 'N/A')}")
        print(f"genai.Client: {genai.Client}")
        
        # Check if we're using the right package
        import pkg_resources
        try:
            version = pkg_resources.get_distribution('google-genai').version
            print(f"google-genai version: {version}")
        except:
            print("google-genai package not found")
        
        try:
            old_version = pkg_resources.get_distribution('google-generativeai').version
            print(f"⚠️  google-generativeai (old package) version: {old_version}")
            print("   You might have both packages installed!")
        except:
            print("✅ google-generativeai (old package) not found - good!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(deep_debug_service())
    sys.exit(0 if success else 1)
