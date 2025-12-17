"""AutoGen tools for LangVoice TTS.

Provides tools compatible with Microsoft AutoGen framework.
"""

import json
import base64
from typing import Any, Dict, List, Optional, Callable

from langvoice_sdk.client import LangVoiceClient


def langvoice_text_to_speech(
    text: str,
    voice: str = "heart",
    language: str = "american_english",
    speed: float = 1.0,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convert text to speech using LangVoice API.
    
    Args:
        text: Text to convert to speech (max 5000 characters).
        voice: Voice ID (e.g., 'heart', 'michael', 'emma').
        language: Language code (e.g., 'american_english', 'british_english').
        speed: Speech speed from 0.5 to 2.0.
        api_key: LangVoice API key.
    
    Returns:
        Dictionary with success status, audio_base64, duration, and characters_processed.
    """
    try:
        client = LangVoiceClient(api_key=api_key)
        response = client.generate(
            text=text,
            voice=voice,
            language=language,
            speed=speed,
        )
        return {
            "success": True,
            "audio_base64": base64.b64encode(response.audio_data).decode("utf-8"),
            "duration": response.duration,
            "characters_processed": response.characters_processed,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def langvoice_multi_voice_speech(
    text: str,
    language: str = "american_english",
    speed: float = 1.0,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate speech with multiple voices using bracket notation.
    
    Args:
        text: Text with [voice] markers (e.g., "[heart] Hello! [michael] Hi!").
        language: Language code for all voices.
        speed: Speech speed from 0.5 to 2.0.
        api_key: LangVoice API key.
    
    Returns:
        Dictionary with success status, audio_base64, and duration.
    """
    try:
        client = LangVoiceClient(api_key=api_key)
        response = client.generate_multi_voice(
            text=text,
            language=language,
            speed=speed,
        )
        return {
            "success": True,
            "audio_base64": base64.b64encode(response.audio_data).decode("utf-8"),
            "duration": response.duration,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def langvoice_list_voices(api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Get list of available voices.
    
    Args:
        api_key: LangVoice API key.
    
    Returns:
        Dictionary with success status and list of voices.
    """
    try:
        client = LangVoiceClient(api_key=api_key)
        voices = client.list_voices()
        return {
            "success": True,
            "voices": [{"id": v.id, "name": v.name} for v in voices],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def langvoice_list_languages(api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Get list of supported languages.
    
    Args:
        api_key: LangVoice API key.
    
    Returns:
        Dictionary with success status and list of languages.
    """
    try:
        client = LangVoiceClient(api_key=api_key)
        languages = client.list_languages()
        return {
            "success": True,
            "languages": [{"id": lang.id, "name": lang.name} for lang in languages],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


class LangVoiceAutoGenToolkit:
    """
    Convenience class for using LangVoice with Microsoft AutoGen.
    
    Set API key once and get all functions for AutoGen agents.
    
    Example:
        >>> from autogen import AssistantAgent, UserProxyAgent
        >>> from langvoice_sdk.tools.autogen_tools import LangVoiceAutoGenToolkit
        >>> 
        >>> # Initialize toolkit with API key
        >>> toolkit = LangVoiceAutoGenToolkit(api_key="your-langvoice-key")
        >>> 
        >>> # Register functions with AutoGen agent
        >>> assistant = AssistantAgent("assistant", llm_config=llm_config)
        >>> user_proxy = UserProxyAgent("user_proxy")
        >>> 
        >>> # Register all LangVoice functions
        >>> for func in toolkit.get_functions():
        ...     user_proxy.register_function(
        ...         function_map={func.__name__: func}
        ...     )
    """
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize toolkit with LangVoice API key."""
        self.api_key = api_key
        self._client = LangVoiceClient(api_key=api_key)
    
    def get_functions(self) -> List[Callable]:
        """Get all LangVoice functions for AutoGen."""
        return [
            self._wrap_function(langvoice_text_to_speech),
            self._wrap_function(langvoice_multi_voice_speech),
            self._wrap_function(langvoice_list_voices),
            self._wrap_function(langvoice_list_languages),
        ]
    
    def _wrap_function(self, func: Callable) -> Callable:
        """Wrap function to include API key."""
        api_key = self.api_key
        
        def wrapped(*args, **kwargs):
            kwargs.setdefault("api_key", api_key)
            return func(*args, **kwargs)
        
        wrapped.__name__ = func.__name__
        wrapped.__doc__ = func.__doc__
        return wrapped
    
    def get_function_schemas(self) -> List[Dict[str, Any]]:
        """Get OpenAI-compatible function schemas for AutoGen."""
        return [
            {
                "name": "langvoice_text_to_speech",
                "description": "Convert text to natural-sounding speech audio using LangVoice TTS API.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text to convert to speech. Maximum 5000 characters.",
                        },
                        "voice": {
                            "type": "string",
                            "description": "Voice ID to use (e.g., 'heart', 'michael', 'emma').",
                            "default": "heart",
                        },
                        "language": {
                            "type": "string",
                            "description": "Language code (e.g., 'american_english').",
                            "default": "american_english",
                        },
                        "speed": {
                            "type": "number",
                            "description": "Speech speed from 0.5 to 2.0.",
                            "default": 1.0,
                        },
                    },
                    "required": ["text"],
                },
            },
            {
                "name": "langvoice_multi_voice_speech",
                "description": "Generate speech with multiple voices using bracket notation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text with [voice] markers. Example: '[heart] Hello! [michael] Hi!'",
                        },
                        "language": {
                            "type": "string",
                            "description": "Language code for all voices.",
                            "default": "american_english",
                        },
                        "speed": {
                            "type": "number",
                            "description": "Speech speed from 0.5 to 2.0.",
                            "default": 1.0,
                        },
                    },
                    "required": ["text"],
                },
            },
            {
                "name": "langvoice_list_voices",
                "description": "Get a list of all available voices for text-to-speech generation.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "langvoice_list_languages",
                "description": "Get a list of all supported languages for text-to-speech generation.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        ]
    
    def text_to_speech(
        self,
        text: str,
        voice: str = "heart",
        language: str = "american_english",
        speed: float = 1.0,
    ) -> Dict[str, Any]:
        """Generate speech from text."""
        return langvoice_text_to_speech(
            text=text,
            voice=voice,
            language=language,
            speed=speed,
            api_key=self.api_key,
        )
    
    def save_audio_from_result(self, result: Dict[str, Any], output_path: str) -> bool:
        """Save audio from result to file."""
        if result.get("success") and "audio_base64" in result:
            audio_bytes = base64.b64decode(result["audio_base64"])
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            return True
        return False
