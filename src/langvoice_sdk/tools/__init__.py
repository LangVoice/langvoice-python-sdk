"""AI agent tools for LangVoice SDK.

Supports multiple AI frameworks:
- OpenAI: LangVoiceOpenAITools
- LangChain: LangVoiceLangChainToolkit
- AutoGen: LangVoiceAutoGenToolkit
- CrewAI: LangVoiceCrewAIToolkit
- Generic: LangVoiceToolkit (works with any framework)
"""

from langvoice_sdk.tools.openai_tools import (
    get_openai_tools,
    create_openai_tts_function,
    handle_openai_tool_call,
    LangVoiceOpenAITools,
)

from langvoice_sdk.tools.generic_tools import (
    LangVoiceToolkit,
    get_langvoice_toolkit,
)

__all__ = [
    # OpenAI
    "get_openai_tools",
    "create_openai_tts_function",
    "handle_openai_tool_call",
    "LangVoiceOpenAITools",
    # Generic
    "LangVoiceToolkit",
    "get_langvoice_toolkit",
]


# Lazy imports for optional dependencies
def get_langchain_tools():
    """Get LangChain tools (requires langchain-core)."""
    from langvoice_sdk.tools.langchain_tools import (
        LangVoiceTTSTool,
        LangVoiceMultiVoiceTool,
        LangVoiceVoicesTool,
        LangVoiceLanguagesTool,
        LangVoiceLangChainToolkit,
        get_all_langchain_tools,
    )
    return {
        "LangVoiceTTSTool": LangVoiceTTSTool,
        "LangVoiceMultiVoiceTool": LangVoiceMultiVoiceTool,
        "LangVoiceVoicesTool": LangVoiceVoicesTool,
        "LangVoiceLanguagesTool": LangVoiceLanguagesTool,
        "LangVoiceLangChainToolkit": LangVoiceLangChainToolkit,
        "get_all_langchain_tools": get_all_langchain_tools,
    }


def get_autogen_toolkit():
    """Get AutoGen toolkit."""
    from langvoice_sdk.tools.autogen_tools import LangVoiceAutoGenToolkit
    return LangVoiceAutoGenToolkit


def get_crewai_toolkit():
    """Get CrewAI toolkit."""
    from langvoice_sdk.tools.crewai_tools import LangVoiceCrewAIToolkit
    return LangVoiceCrewAIToolkit

