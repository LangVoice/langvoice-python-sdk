"""
LangVoice SDK - CrewAI Integration Example
==========================================

This example shows how to use LangVoice with CrewAI.

Requirements:
    pip install crewai langvoice
"""

from crewai import Agent, Task, Crew, Process
from langvoice_sdk.tools.crewai_tools import langvoice_sdkCrewAIToolkit

# ============================================
# CONFIGURATION - Set your API keys once
# ============================================
OPENAI_API_KEY = "your-openai-api-key"
LANGVOICE_API_KEY = "your-langvoice-api-key"

# Initialize LangVoice toolkit
toolkit = LangVoiceCrewAIToolkit(api_key=LANGVOICE_API_KEY)


def main():
    # ============================================
    # CREATE CREWAI AGENTS WITH LANGVOICE TOOLS
    # ============================================
    
    # Get all LangVoice tools
    tools = toolkit.get_tools()
    print(f"Available tools: {[t.name for t in tools]}")
    
    # Voice Generator Agent
    voice_agent = Agent(
        role="Voice Generator",
        goal="Generate natural-sounding speech from text",
        backstory="You are an expert at creating high-quality voice content.",
        tools=tools,
        verbose=True,
    )
    
    # Create task
    voice_task = Task(
        description="Generate speech saying 'Hello from CrewAI! This is a test of the LangVoice SDK.'",
        expected_output="Confirmation that speech was generated with duration info",
        agent=voice_agent,
    )
    
    # ============================================
    # CREATE AND RUN CREW
    # ============================================
    crew = Crew(
        agents=[voice_agent],
        tasks=[voice_task],
        process=Process.sequential,
        verbose=True,
    )
    
    result = crew.kickoff()
    print(f"\n📊 Crew Result: {result}")


# Alternative: Simple usage without Crew
def simple_usage():
    """Simple usage of LangVoice with CrewAI toolkit."""
    from langvoice_sdk.tools.crewai_tools import langvoice_sdkTTSTool
    
    # Create TTS tool
    tts_tool = LangVoiceTTSTool(api_key=LANGVOICE_API_KEY)
    
    # Generate speech
    result = tts_tool._run(
        text="Hello from CrewAI!",
        voice="heart",
        language="american_english",
    )
    
    print(f"✅ Result: {result}")


if __name__ == "__main__":
    # Uncomment to run with Crew:
    # main()
    
    # Or use simple mode:
    simple_usage()
