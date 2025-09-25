#!/usr/bin/env python3
"""
Debug script to isolate the health check issue
"""

import os
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_service_health_check():
    """Test the service health check specifically"""
    
    print("🐛 Testing Service Health Check...")
    print("-" * 50)
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No GEMINI_API_KEY found")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    try:
        # Import after adding to path
        from src.services.gemini_service import GeminiService, GeminiConfig, ModelType
        
        print("\n1. Creating service...")
        config = GeminiConfig(
            api_key=api_key,
            model_type=ModelType.GEMINI_2_5_FLASH,
            temperature=0.7,
            max_output_tokens=1000
        )
        
        service = GeminiService(config)
        print("   ✅ Service created")
        
        print("\n2. Running health check...")
        health_result = await service.health_check()
        
        print(f"\n   Health check result:")
        print(f"   - Healthy: {health_result.get('gemini_healthy', False)}")
        print(f"   - Model: {health_result.get('model_type', 'N/A')}")
        print(f"   - Response: {health_result.get('response_received', 'None')}")
        print(f"   - Error: {health_result.get('error', 'None')}")
        print(f"   - Timestamp: {health_result.get('timestamp', 'N/A')}")
        
        if health_result.get('gemini_healthy'):
            print("\n✅ Health check passed!")
            return True
        else:
            print("\n❌ Health check failed!")
            # Let's test the client directly for comparison
            print("\n3. Testing direct async client for comparison...")
            
            from google import genai
            from google.genai import types
            
            direct_client = genai.Client(api_key=api_key)
            
            test_config = types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=10
            )
            
            try:
                direct_response = await direct_client.aio.models.generate_content(
                    model='gemini-2.5-flash',
                    contents='Say "OK"',
                    config=test_config
                )
                
                print(f"   Direct response: {direct_response.text if direct_response else 'None'}")
                
                if direct_response and direct_response.text:
                    print("   ✅ Direct client works but service doesn't - checking service client...")
                    
                    # Try to use the service's client directly
                    try:
                        service_response = await service.client.aio.models.generate_content(
                            model='gemini-2.5-flash',
                            contents='Say "OK from service client"',
                            config=test_config
                        )
                        print(f"   Service client response: {service_response.text if service_response else 'None'}")
                        
                        if service_response and service_response.text:
                            print("   ✅ Service client works directly - issue is in health_check method")
                        else:
                            print("   ❌ Service client doesn't work directly")
                            
                    except Exception as service_client_error:
                        print(f"   ❌ Service client error: {service_client_error}")
                else:
                    print("   ❌ Direct client also failed")
                    
            except Exception as direct_error:
                print(f"   ❌ Direct client error: {direct_error}")
            
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_service_health_check())
    sys.exit(0 if success else 1)
