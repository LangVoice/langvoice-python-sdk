"""Generic/Universal tools for LangVoice TTS.

Works with any AI agent framework that supports function calling.
Compatible with: LlamaIndex, Semantic Kernel, Haystack, and custom frameworks.
"""

import base64
import json
from typing import Any, Dict, List, Optional, Callable, Union

from langvoice.client import LangVoiceClient


class LangVoiceToolkit:
    """
    Universal toolkit for using LangVoice with any AI framework.
    
    This is a framework-agnostic implementation that provides:
    - Raw functions for direct use
    - Function schemas for tool registration
    - Convenience methods for common operations
    
    Example:
        >>> from langvoice.tools.generic_tools import LangVoiceToolkit
        >>> 
        >>> # Initialize with API key
        >>> toolkit = LangVoiceToolkit(api_key="your-langvoice-key")
        >>> 
        >>> # Use directly
        >>> result = toolkit.text_to_speech("Hello world!")
        >>> toolkit.save_audio(result, "output.mp3")
        >>> 
        >>> # Get function schemas for any framework
        >>> schemas = toolkit.get_function_schemas()
        >>> 
        >>> # Handle tool calls from any LLM
        >>> result = toolkit.handle_tool_call("langvoice_text_to_speech", {"text": "Hello"})
    """
    
    # Tool names
    TOOL_TTS = "langvoice_text_to_speech"
    TOOL_MULTI_VOICE = "langvoice_multi_voice_speech"
    TOOL_LIST_VOICES = "langvoice_list_voices"
    TOOL_LIST_LANGUAGES = "langvoice_list_languages"
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize toolkit with LangVoice API key."""
        self.api_key = api_key
        self._client = LangVoiceClient(api_key=api_key)
    
    @property
    def client(self) -> LangVoiceClient:
        """Get the LangVoice client."""
        return self._client
    
    # =========================================
    # CORE TOOL FUNCTIONS
    # =========================================
    
    def text_to_speech(
        self,
        text: str,
        voice: str = "heart",
        language: str = "american_english",
        speed: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Convert text to speech.
        
        Args:
            text: Text to convert (max 5000 characters).
            voice: Voice ID (e.g., 'heart', 'michael').
            language: Language code (e.g., 'american_english').
            speed: Speech speed from 0.5 to 2.0.
        
        Returns:
            Dictionary with success, audio_base64, duration, characters_processed.
        """
        try:
            response = self._client.generate(
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
    
    def multi_voice_speech(
        self,
        text: str,
        language: str = "american_english",
        speed: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Generate speech with multiple voices.
        
        Args:
            text: Text with [voice] markers.
            language: Language code.
            speed: Speech speed from 0.5 to 2.0.
        
        Returns:
            Dictionary with success, audio_base64, duration.
        """
        try:
            response = self._client.generate_multi_voice(
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
    
    def list_voices(self) -> Dict[str, Any]:
        """Get available voices."""
        try:
            voices = self._client.list_voices()
            return {
                "success": True,
                "voices": [{"id": v.id, "name": v.name} for v in voices],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_languages(self) -> Dict[str, Any]:
        """Get supported languages."""
        try:
            languages = self._client.list_languages()
            return {
                "success": True,
                "languages": [{"id": lang.id, "name": lang.name} for lang in languages],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # =========================================
    # TOOL CALL HANDLER
    # =========================================
    
    def handle_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Union[Dict[str, Any], str]:
        """
        Handle a tool call by name.
        
        Args:
            tool_name: Name of the tool to call.
            arguments: Arguments for the tool.
        
        Returns:
            Result dictionary or JSON string.
        """
        if tool_name == self.TOOL_TTS:
            return self.text_to_speech(
                text=arguments.get("text", ""),
                voice=arguments.get("voice", "heart"),
                language=arguments.get("language", "american_english"),
                speed=arguments.get("speed", 1.0),
            )
        elif tool_name == self.TOOL_MULTI_VOICE:
            return self.multi_voice_speech(
                text=arguments.get("text", ""),
                language=arguments.get("language", "american_english"),
                speed=arguments.get("speed", 1.0),
            )
        elif tool_name == self.TOOL_LIST_VOICES:
            return self.list_voices()
        elif tool_name == self.TOOL_LIST_LANGUAGES:
            return self.list_languages()
        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
    
    def handle_tool_call_json(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> str:
        """Handle tool call and return JSON string result."""
        result = self.handle_tool_call(tool_name, arguments)
        return json.dumps(result)
    
    # =========================================
    # FUNCTION SCHEMAS
    # =========================================
    
    def get_function_schemas(self) -> List[Dict[str, Any]]:
        """
        Get OpenAI-compatible function schemas.
        
        These can be used with any framework that supports OpenAI function format.
        """
        return [
            {
                "name": self.TOOL_TTS,
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
                            "description": "Voice ID (e.g., 'heart', 'michael', 'emma').",
                            "enum": [
                                "heart", "bella", "nicole", "sarah", "nova", "sky", "jessica",
                                "river", "michael", "fenrir", "eric", "liam", "onyx", "adam",
                                "emma", "isabella", "alice", "lily", "george", "fable", "lewis", "daniel"
                            ],
                            "default": "heart",
                        },
                        "language": {
                            "type": "string",
                            "description": "Language code.",
                            "enum": [
                                "american_english", "british_english", "spanish", "french",
                                "hindi", "italian", "japanese", "brazilian_portuguese", "mandarin_chinese"
                            ],
                            "default": "american_english",
                        },
                        "speed": {
                            "type": "number",
                            "description": "Speech speed from 0.5 (slow) to 2.0 (fast).",
                            "minimum": 0.5,
                            "maximum": 2.0,
                            "default": 1.0,
                        },
                    },
                    "required": ["text"],
                },
            },
            {
                "name": self.TOOL_MULTI_VOICE,
                "description": "Generate speech with multiple voices using bracket notation. Use [voice_name] to switch voices.",
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
                "name": self.TOOL_LIST_VOICES,
                "description": "Get a list of all available voices for text-to-speech generation.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": self.TOOL_LIST_LANGUAGES,
                "description": "Get a list of all supported languages for text-to-speech generation.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        ]
    
    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Get tools in OpenAI function calling format."""
        return [
            {"type": "function", "function": schema}
            for schema in self.get_function_schemas()
        ]
    
    # =========================================
    # UTILITY METHODS
    # =========================================
    
    def save_audio(self, result: Dict[str, Any], output_path: str) -> bool:
        """
        Save audio from result to file.
        
        Args:
            result: Result from text_to_speech or multi_voice_speech.
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
    
    def get_audio_bytes(self, result: Dict[str, Any]) -> Optional[bytes]:
        """Extract audio bytes from result."""
        if result.get("success") and "audio_base64" in result:
            return base64.b64decode(result["audio_base64"])
        return None


# Convenience function
def get_langvoice_toolkit(api_key: Optional[str] = None) -> LangVoiceToolkit:
    """Create a LangVoice toolkit instance."""
    return LangVoiceToolkit(api_key=api_key)
