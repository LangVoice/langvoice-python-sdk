"""
LangVoice SDK - AutoGen Integration Example
============================================

This example shows how to use LangVoice with Microsoft AutoGen.

Requirements:
    pip install pyautogen langvoice
"""

from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
from langvoice.tools.autogen_tools import LangVoiceAutoGenToolkit

# ============================================
# CONFIGURATION - Set your API keys once
# ============================================
OPENAI_API_KEY = "your-openai-api-key"
LANGVOICE_API_KEY = "your-langvoice-api-key"

# Initialize LangVoice toolkit
toolkit = LangVoiceAutoGenToolkit(api_key=LANGVOICE_API_KEY)


def main():
    # ============================================
    # CONFIGURE LLM
    # ============================================
    llm_config = {
        "config_list": [
            {
                "model": "gpt-4o",
                "api_key": OPENAI_API_KEY,
            }
        ],
        "functions": toolkit.get_function_schemas(),
    }
    
    # ============================================
    # CREATE AUTOGEN AGENTS
    # ============================================
    
    # Assistant agent with LangVoice capabilities
    assistant = AssistantAgent(
        name="voice_assistant",
        system_message="""You are a helpful assistant with text-to-speech capabilities.
        You can generate speech using the langvoice_text_to_speech function.
        You can also list available voices and languages.""",
        llm_config=llm_config,
    )
    
    # User proxy agent to execute functions
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        code_execution_config={"work_dir": "output"},
    )
    
    # Register LangVoice functions
    for func in toolkit.get_functions():
        user_proxy.register_function(
            function_map={func.__name__: func}
        )
    
    # ============================================
    # RUN CONVERSATION
    # ============================================
    user_proxy.initiate_chat(
        assistant,
        message="Generate speech saying 'Hello from AutoGen!' and save it to output.mp3"
    )


# Alternative: Simple usage without agents
def simple_usage():
    """Simple usage of LangVoice with AutoGen toolkit."""
    toolkit = LangVoiceAutoGenToolkit(api_key=LANGVOICE_API_KEY)
    
    # Generate speech directly
    result = toolkit.text_to_speech(
        text="Hello from AutoGen!",
        voice="heart",
        language="american_english",
    )
    
    if result["success"]:
        toolkit.save_audio_from_result(result, "output.mp3")
        print(f"✅ Audio saved! Duration: {result['duration']}s")
    else:
        print(f"❌ Error: {result['error']}")


if __name__ == "__main__":
    # Uncomment to run with agents:
    # main()
    
    # Or use simple mode:
    simple_usage()
