#!/usr/bin/env python3
"""
Debug script for Gemini API issues
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def debug_gemini():
    """Debug the Gemini API step by step"""
    
    print("🐛 Debugging Gemini API...")
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No GEMINI_API_KEY found")
        return
    else:
        print(f"✅ API key found: {api_key[:10]}...")
    
    try:
        # Test basic import
        print("1. Testing import...")
        from google import genai
        from google.genai import types
        print("   ✅ Import successful")
        
        # Test client creation
        print("2. Testing client creation...")
        client = genai.Client(api_key=api_key)
        print("   ✅ Client created")
        
        # Test simple generation
        print("3. Testing simple generation...")
        response = await asyncio.to_thread(
            client.models.generate_content,
            model='gemini-2.5-flash',
            contents='Say "Hello World"'
        )
        
        print(f"   Response: {response}")
        print(f"   Response.text: {response.text}")
        print(f"   Response type: {type(response)}")
        
        if hasattr(response, '__dict__'):
            print(f"   Response attributes: {list(response.__dict__.keys())}")
        
        if response.text:
            print("   ✅ Simple generation successful")
            print(f"   Generated text: {response.text}")
        else:
            print("   ❌ Empty response text")
            
        # Test with config
        print("4. Testing with config...")
        config = types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=50
        )
        
        response2 = await asyncio.to_thread(
            client.models.generate_content,
            model='gemini-2.5-flash',
            contents='Say "Test with config"',
            config=config
        )
        
        print(f"   Response2.text: {response2.text}")
        
        if response2.text:
            print("   ✅ Config generation successful")
        else:
            print("   ❌ Config generation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_gemini())
