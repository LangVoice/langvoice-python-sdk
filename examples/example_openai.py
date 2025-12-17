"""
LangVoice SDK - OpenAI Integration Example
===========================================

This example shows how to use LangVoice with OpenAI function calling.
The cleanest way - set API key once, handle all tool calls easily.

Requirements:
    pip install openai langvoice
"""

import json
import base64
from openai import OpenAI
from langvoice.tools import LangVoiceOpenAITools

# ============================================
# CONFIGURATION - Set your API keys once
# ============================================
OPENAI_API_KEY = "your-openai-api-key"
LANGVOICE_API_KEY = "your-langvoice-api-key"

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
langvoice_tools = LangVoiceOpenAITools(api_key=LANGVOICE_API_KEY)


def main():
    # ============================================
    # MAKE REQUEST WITH LANGVOICE TOOLS
    # ============================================
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "Generate speech saying: Hello! Welcome to LangVoice SDK."}
        ],
        tools=langvoice_tools.get_tools()  # All LangVoice tools available
    )
    
    print(f"OpenAI Response: {response.choices[0].message.content}")
    print(f"Tool Calls: {len(response.choices[0].message.tool_calls or [])}")
    
    # ============================================
    # HANDLE TOOL CALLS - No API key needed!
    # ============================================
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            print(f"\n🔧 Tool: {tool_call.function.name}")
            print(f"   Arguments: {tool_call.function.arguments}")
            
            # Handle tool call - API key already configured!
            result = langvoice_tools.handle_call(tool_call)
            
            print(f"\n📊 Result:")
            print(f"   Success: {result.get('success')}")
            print(f"   Duration: {result.get('duration')} seconds")
            print(f"   Characters: {result.get('characters_processed')}")
            
            # Save audio to file
            if langvoice_tools.save_audio_from_result(result, "output.mp3"):
                print(f"\n✅ Audio saved to output.mp3")
    else:
        print("\n❌ No tool calls were made by the model.")


if __name__ == "__main__":
    main()
