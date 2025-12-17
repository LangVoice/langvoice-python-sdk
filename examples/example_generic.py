"""
LangVoice SDK - Generic/Universal Integration Example
======================================================

This example shows how to use LangVoice with ANY AI framework.
The generic toolkit works with: LlamaIndex, Semantic Kernel, Haystack, custom frameworks, etc.

Requirements:
    pip install langvoice
"""

from langvoice.tools import LangVoiceToolkit

# ============================================
# CONFIGURATION - Set your API key once
# ============================================
LANGVOICE_API_KEY = "your-langvoice-api-key"

# Initialize universal toolkit
toolkit = LangVoiceToolkit(api_key=LANGVOICE_API_KEY)


def basic_usage():
    """Basic text-to-speech generation."""
    print("=" * 50)
    print("Basic TTS Generation")
    print("=" * 50)
    
    # Generate speech
    result = toolkit.text_to_speech(
        text="Hello! This is a test of the LangVoice SDK.",
        voice="heart",
        language="american_english",
        speed=1.0,
    )
    
    if result["success"]:
        print(f"✅ Success!")
        print(f"   Duration: {result['duration']} seconds")
        print(f"   Characters: {result['characters_processed']}")
        
        # Save to file
        toolkit.save_audio(result, "output.mp3")
        print(f"   Saved to: output.mp3")
    else:
        print(f"❌ Error: {result['error']}")


def multi_voice_example():
    """Multi-voice speech generation."""
    print("\n" + "=" * 50)
    print("Multi-Voice Generation")
    print("=" * 50)
    
    result = toolkit.multi_voice_speech(
        text="[heart] Hello! Welcome to our podcast. [michael] Thanks for having me!",
        language="american_english",
    )
    
    if result["success"]:
        print(f"✅ Multi-voice speech generated!")
        print(f"   Duration: {result['duration']} seconds")
        toolkit.save_audio(result, "multi_voice.mp3")
        print(f"   Saved to: multi_voice.mp3")


def list_resources():
    """List available voices and languages."""
    print("\n" + "=" * 50)
    print("Available Voices")
    print("=" * 50)
    
    voices_result = toolkit.list_voices()
    if voices_result["success"]:
        for voice in voices_result["voices"]:
            print(f"  - {voice['id']}: {voice['name']}")
    
    print("\n" + "=" * 50)
    print("Supported Languages")
    print("=" * 50)
    
    languages_result = toolkit.list_languages()
    if languages_result["success"]:
        for lang in languages_result["languages"]:
            print(f"  - {lang['id']}: {lang['name']}")


def handle_tool_calls_example():
    """Example of handling tool calls from any LLM."""
    print("\n" + "=" * 50)
    print("Handling Tool Calls")
    print("=" * 50)
    
    # Simulate a tool call from an LLM
    tool_name = "langvoice_text_to_speech"
    arguments = {
        "text": "This simulates a tool call from any LLM!",
        "voice": "michael",
    }
    
    # Handle the tool call
    result = toolkit.handle_tool_call(tool_name, arguments)
    
    if result["success"]:
        print(f"✅ Tool call handled successfully!")
        print(f"   Duration: {result['duration']} seconds")
        toolkit.save_audio(result, "tool_call.mp3")
        print(f"   Saved to: tool_call.mp3")


def get_schemas_example():
    """Get function schemas for any framework."""
    print("\n" + "=" * 50)
    print("Function Schemas (for any framework)")
    print("=" * 50)
    
    schemas = toolkit.get_function_schemas()
    for schema in schemas:
        print(f"\n  📌 {schema['name']}")
        print(f"     {schema['description'][:60]}...")


# ============================================
# INTEGRATION WITH LLAMAINDEX
# ============================================
def llamaindex_example():
    """Example integration with LlamaIndex."""
    print("\n" + "=" * 50)
    print("LlamaIndex Integration")
    print("=" * 50)
    
    try:
        from llama_index.core.tools import FunctionTool
        
        # Create LlamaIndex tools from LangVoice
        def generate_speech(text: str, voice: str = "heart") -> str:
            result = toolkit.text_to_speech(text=text, voice=voice)
            if result["success"]:
                toolkit.save_audio(result, "llamaindex_output.mp3")
                return f"Speech generated! Duration: {result['duration']}s"
            return f"Error: {result['error']}"
        
        tts_tool = FunctionTool.from_defaults(
            fn=generate_speech,
            name="langvoice_tts",
            description="Generate speech from text using LangVoice",
        )
        
        print("✅ LlamaIndex FunctionTool created!")
        print(f"   Name: {tts_tool.metadata.name}")
        
    except ImportError:
        print("⚠️  LlamaIndex not installed. Run: pip install llama-index")


# ============================================
# INTEGRATION WITH SEMANTIC KERNEL
# ============================================
def semantic_kernel_example():
    """Example integration with Semantic Kernel."""
    print("\n" + "=" * 50)
    print("Semantic Kernel Integration")
    print("=" * 50)
    
    try:
        import semantic_kernel as sk
        from semantic_kernel.functions import kernel_function
        
        # Create a plugin class
        class LangVoicePlugin:
            def __init__(self, toolkit):
                self.toolkit = toolkit
            
            @kernel_function(
                name="generate_speech",
                description="Generate speech from text"
            )
            def generate_speech(self, text: str, voice: str = "heart") -> str:
                result = self.toolkit.text_to_speech(text=text, voice=voice)
                if result["success"]:
                    self.toolkit.save_audio(result, "sk_output.mp3")
                    return f"Speech generated! Duration: {result['duration']}s"
                return f"Error: {result['error']}"
        
        print("✅ Semantic Kernel plugin class created!")
        
    except ImportError:
        print("⚠️  Semantic Kernel not installed. Run: pip install semantic-kernel")


if __name__ == "__main__":
    basic_usage()
    multi_voice_example()
    list_resources()
    handle_tool_calls_example()
    get_schemas_example()
    llamaindex_example()
    semantic_kernel_example()
