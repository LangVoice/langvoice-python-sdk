"""OpenAI function calling tools for LangVoice."""

import json
import base64
from typing import Any, Dict, List, Optional, Callable

from langvoice.client import LangVoiceClient


# OpenAI tool definitions
LANGVOICE_TTS_TOOL = {
    "type": "function",
    "function": {
        "name": "langvoice_text_to_speech",
        "description": "Convert text to natural-sounding speech audio using LangVoice TTS API. Returns base64-encoded MP3 audio.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to convert to speech. Maximum 5000 characters.",
                },
                "voice": {
                    "type": "string",
                    "description": "Voice ID to use for speech generation.",
                    "enum": [
                        "heart", "bella", "nicole", "sarah", "nova", "sky", "jessica",
                        "river", "michael", "fenrir", "eric", "liam", "onyx", "adam",
                        "emma", "isabella", "alice", "lily", "george", "fable", "lewis", "daniel"
                    ],
                    "default": "heart",
                },
                "language": {
                    "type": "string",
                    "description": "Language code for the speech.",
                    "enum": [
                        "american_english", "british_english", "spanish", "french",
                        "hindi", "italian", "japanese", "brazilian_portuguese", "mandarin_chinese"
                    ],
                    "default": "american_english",
                },
                "speed": {
                    "type": "number",
                    "description": "Speech speed from 0.5 (slow) to 2.0 (fast). Default is 1.0.",
                    "minimum": 0.5,
                    "maximum": 2.0,
                    "default": 1.0,
                },
            },
            "required": ["text"],
        },
    },
}

LANGVOICE_MULTI_VOICE_TOOL = {
    "type": "function",
    "function": {
        "name": "langvoice_multi_voice_speech",
        "description": "Generate speech with multiple voices using bracket notation. Use [voice_name] to switch voices in the text.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text with voice markers. Example: '[heart] Hello! [michael] Hi there!'",
                },
                "language": {
                    "type": "string",
                    "description": "Language code for all voices.",
                    "enum": [
                        "american_english", "british_english", "spanish", "french",
                        "hindi", "italian", "japanese", "brazilian_portuguese", "mandarin_chinese"
                    ],
                    "default": "american_english",
                },
                "speed": {
                    "type": "number",
                    "description": "Speech speed from 0.5 to 2.0.",
                    "minimum": 0.5,
                    "maximum": 2.0,
                    "default": 1.0,
                },
            },
            "required": ["text"],
        },
    },
}

LANGVOICE_LIST_VOICES_TOOL = {
    "type": "function",
    "function": {
        "name": "langvoice_list_voices",
        "description": "Get a list of all available voices for text-to-speech generation.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}

LANGVOICE_LIST_LANGUAGES_TOOL = {
    "type": "function",
    "function": {
        "name": "langvoice_list_languages",
        "description": "Get a list of all supported languages for text-to-speech generation.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}


def get_openai_tools() -> List[Dict[str, Any]]:
    """
    Get all LangVoice tools formatted for OpenAI function calling.

    Returns:
        List of tool definitions compatible with OpenAI's API.

    Example:
        >>> from openai import OpenAI
        >>> from langvoice.tools import get_openai_tools
        >>>
        >>> client = OpenAI()
        >>> response = client.chat.completions.create(
        ...     model="gpt-4",
        ...     messages=[{"role": "user", "content": "Say hello in a friendly voice"}],
        ...     tools=get_openai_tools()
        ... )
    """
    return [
        LANGVOICE_TTS_TOOL,
        LANGVOICE_MULTI_VOICE_TOOL,
        LANGVOICE_LIST_VOICES_TOOL,
        LANGVOICE_LIST_LANGUAGES_TOOL,
    ]


def create_openai_tts_function(
    api_key: Optional[str] = None,
    return_base64: bool = True,
) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """
    Create a function that handles OpenAI tool calls for LangVoice TTS.

    Args:
        api_key: LangVoice API key.
        return_base64: If True, return audio as base64 string. Otherwise return bytes.

    Returns:
        Function that processes tool call arguments and returns results.

    Example:
        >>> from langvoice.tools import create_openai_tts_function
        >>> tts_function = create_openai_tts_function(api_key="your-key")
        >>> result = tts_function({"text": "Hello world", "voice": "heart"})
    """
    client = LangVoiceClient(api_key=api_key)

    def tts_function(arguments: Dict[str, Any]) -> Dict[str, Any]:
        text = arguments.get("text", "")
        voice = arguments.get("voice", "heart")
        language = arguments.get("language", "american_english")
        speed = arguments.get("speed", 1.0)

        response = client.generate(
            text=text,
            voice=voice,
            language=language,
            speed=speed,
        )

        result = {
            "success": True,
            "duration": response.duration,
            "characters_processed": response.characters_processed,
        }

        if return_base64:
            result["audio_base64"] = base64.b64encode(response.audio_data).decode("utf-8")
        else:
            result["audio_bytes"] = response.audio_data

        return result

    return tts_function


def handle_openai_tool_call(
    tool_name: str,
    arguments: Dict[str, Any],
    api_key: Optional[str] = None,
) -> str:
    """
    Handle an OpenAI tool call for LangVoice functions.

    Args:
        tool_name: Name of the tool being called.
        arguments: Arguments passed to the tool.
        api_key: LangVoice API key.

    Returns:
        JSON string result to pass back to OpenAI.

    Example:
        >>> # In your OpenAI tool call handler:
        >>> for tool_call in response.choices[0].message.tool_calls:
        ...     args = json.loads(tool_call.function.arguments)
        ...     result = handle_openai_tool_call(
        ...         tool_call.function.name,
        ...         args,
        ...         api_key="your-langvoice-key"
        ...     )
    """
    client = LangVoiceClient(api_key=api_key)

    try:
        if tool_name == "langvoice_text_to_speech":
            response = client.generate(
                text=arguments.get("text", ""),
                voice=arguments.get("voice", "heart"),
                language=arguments.get("language", "american_english"),
                speed=arguments.get("speed", 1.0),
            )
            result = {
                "success": True,
                "audio_base64": base64.b64encode(response.audio_data).decode("utf-8"),
                "duration": response.duration,
                "characters_processed": response.characters_processed,
            }

        elif tool_name == "langvoice_multi_voice_speech":
            response = client.generate_multi_voice(
                text=arguments.get("text", ""),
                language=arguments.get("language", "american_english"),
                speed=arguments.get("speed", 1.0),
            )
            result = {
                "success": True,
                "audio_base64": base64.b64encode(response.audio_data).decode("utf-8"),
                "duration": response.duration,
            }

        elif tool_name == "langvoice_list_voices":
            voices = client.list_voices()
            result = {
                "success": True,
                "voices": [{"id": v.id, "name": v.name} for v in voices],
            }

        elif tool_name == "langvoice_list_languages":
            languages = client.list_languages()
            result = {
                "success": True,
                "languages": [{"id": lang.id, "name": lang.name} for lang in languages],
            }

        else:
            result = {"success": False, "error": f"Unknown tool: {tool_name}"}

    except Exception as e:
        result = {"success": False, "error": str(e)}

    return json.dumps(result)


# Convenience class for OpenAI integration
class LangVoiceOpenAITools:
    """
    Helper class for integrating LangVoice with OpenAI function calling.

    Example:
        >>> from openai import OpenAI
        >>> from langvoice.tools.openai_tools import LangVoiceOpenAITools
        >>>
        >>> openai_client = OpenAI()
        >>> langvoice_tools = LangVoiceOpenAITools(api_key="your-langvoice-key")
        >>>
        >>> # Create completion with tools
        >>> response = openai_client.chat.completions.create(
        ...     model="gpt-4",
        ...     messages=[{"role": "user", "content": "Generate speech saying hello"}],
        ...     tools=langvoice_tools.get_tools()
        ... )
        >>>
        >>> # Handle tool calls
        >>> if response.choices[0].message.tool_calls:
        ...     for tool_call in response.choices[0].message.tool_calls:
        ...         result = langvoice_tools.handle_call(tool_call)
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize with LangVoice API key."""
        self.client = LangVoiceClient(api_key=api_key)

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get tool definitions for OpenAI."""
        return get_openai_tools()

    def handle_call(self, tool_call: Any) -> Dict[str, Any]:
        """
        Handle an OpenAI tool call object.

        Args:
            tool_call: OpenAI tool call object with function.name and function.arguments.

        Returns:
            Dictionary with result data.
        """
        arguments = json.loads(tool_call.function.arguments)
        result_json = handle_openai_tool_call(
            tool_call.function.name,
            arguments,
            api_key=self.client.api_key,
        )
        return json.loads(result_json)

    def save_audio_from_result(self, result: Dict[str, Any], output_path: str) -> bool:
        """
        Save audio from a tool call result to a file.

        Args:
            result: Result dictionary from handle_call.
            output_path: Path to save the MP3 file.

        Returns:
            True if successful, False otherwise.
        """
        if result.get("success") and "audio_base64" in result:
            audio_bytes = base64.b64decode(result["audio_base64"])
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            return True
        return False
