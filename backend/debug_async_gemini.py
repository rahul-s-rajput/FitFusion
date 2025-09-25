#!/usr/bin/env python3
"""
Simple debug script to test google-genai async client
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_async_client():
    """Test the async client directly"""
    
    print("🐛 Testing Google GenAI Async Client...")
    print("-" * 50)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No GEMINI_API_KEY found")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    try:
        from google import genai
        from google.genai import types
        
        # Create client
        print("\n1. Creating client...")
        client = genai.Client(api_key=api_key)
        print("   ✅ Client created")
        
        # Test 1: Simple async generation
        print("\n2. Testing async generation...")
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents='Say "Hello from async"'
        )
        
        print(f"   Response: {response}")
        print(f"   Response.text: {response.text}")
        
        if response and response.text:
            print("   ✅ Async generation successful")
        else:
            print("   ❌ Empty response")
            return False
        
        # Test 2: Async with config
        print("\n3. Testing async with config...")
        config = types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=50
        )
        
        response2 = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents='Count to 5',
            config=config
        )
        
        print(f"   Response2.text: {response2.text}")
        
        if response2.text:
            print("   ✅ Async config generation successful")
        else:
            print("   ❌ Async config generation failed")
            return False
        
        # Test 3: JSON output
        print("\n4. Testing async JSON output...")
        config_json = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=200,
            response_mime_type="application/json"
        )
        
        response3 = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents='Generate a JSON object with name and age fields',
            config=config_json
        )
        
        print(f"   Response3.text: {response3.text}")
        
        if response3.text:
            import json
            try:
                data = json.loads(response3.text)
                print(f"   ✅ JSON parsed: {data}")
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON parse error: {e}")
                return False
        else:
            print("   ❌ Empty JSON response")
            return False
        
        print("\n" + "=" * 50)
        print("✅ All async client tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_async_client())
    exit(0 if success else 1)
