"""CrewAI tools for LangVoice TTS.

Provides tools compatible with CrewAI framework.
"""

import base64
from typing import Any, Dict, List, Optional, Type

try:
    from crewai.tools import BaseTool as CrewAIBaseTool
    from pydantic import BaseModel, Field
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    CrewAIBaseTool = object  # type: ignore
    BaseModel = object  # type: ignore

from langvoice_sdk.client import LangVoiceClient


def _check_crewai() -> None:
    """Check if CrewAI is available."""
    if not CREWAI_AVAILABLE:
        raise ImportError(
            "crewai is required for CrewAI tools. "
            "Install with: pip install crewai"
        )


if CREWAI_AVAILABLE:

    class TTSInput(BaseModel):
        """Input for text-to-speech tool."""
        text: str = Field(description="Text to convert to speech")
        voice: str = Field(default="heart", description="Voice ID")
        language: str = Field(default="american_english", description="Language code")
        speed: float = Field(default=1.0, description="Speech speed 0.5-2.0")

    class MultiVoiceInput(BaseModel):
        """Input for multi-voice tool."""
        text: str = Field(description="Text with [voice] markers")
        language: str = Field(default="american_english", description="Language code")
        speed: float = Field(default=1.0, description="Speech speed 0.5-2.0")

    class LangVoiceTTSTool(CrewAIBaseTool):
        """CrewAI tool for text-to-speech generation."""
        
        name: str = "langvoice_text_to_speech"
        description: str = "Convert text to speech and save to output.mp3. Returns confirmation with duration."
        args_schema: Type[BaseModel] = TTSInput
        
        api_key: Optional[str] = None
        output_file: Optional[str] = "output.mp3"
        _client: Optional[LangVoiceClient] = None
        
        def __init__(self, api_key: Optional[str] = None, output_file: Optional[str] = "output.mp3", **kwargs):
            super().__init__(**kwargs)
            self.api_key = api_key
            self.output_file = output_file
        
        @property
        def client(self) -> LangVoiceClient:
            if self._client is None:
                self._client = LangVoiceClient(api_key=self.api_key)
            return self._client
        
        def _run(
            self,
            text: str,
            voice: str = "heart",
            language: str = "american_english",
            speed: float = 1.0,
        ) -> str:
            try:
                response = self.client.generate(
                    text=text,
                    voice=voice,
                    language=language,
                    speed=speed,
                )
                
                # Save audio to file if output_file is set
                if self.output_file:
                    with open(self.output_file, "wb") as f:
                        f.write(response.audio_data)
                    return (
                        f"✅ Speech generated and saved to {self.output_file}! "
                        f"Duration: {response.duration}s, "
                        f"Characters: {response.characters_processed}"
                    )
                else:
                    audio_base64 = base64.b64encode(response.audio_data).decode("utf-8")
                    return f"✅ Speech generated! Duration: {response.duration}s. Audio (base64): {audio_base64[:100]}..."
            except Exception as e:
                return f"❌ Error generating speech: {str(e)}"

    class LangVoiceMultiVoiceTool(CrewAIBaseTool):
        """CrewAI tool for multi-voice speech generation."""
        
        name: str = "langvoice_multi_voice"
        description: str = "Generate speech with multiple voices using [voice] markers."
        args_schema: Type[BaseModel] = MultiVoiceInput
        
        api_key: Optional[str] = None
        _client: Optional[LangVoiceClient] = None
        
        def __init__(self, api_key: Optional[str] = None, **kwargs):
            super().__init__(**kwargs)
            self.api_key = api_key
        
        @property
        def client(self) -> LangVoiceClient:
            if self._client is None:
                self._client = LangVoiceClient(api_key=self.api_key)
            return self._client
        
        def _run(
            self,
            text: str,
            language: str = "american_english",
            speed: float = 1.0,
        ) -> str:
            try:
                response = self.client.generate_multi_voice(
                    text=text,
                    language=language,
                    speed=speed,
                )
                return f"Multi-voice speech generated. Duration: {response.duration}s"
            except Exception as e:
                return f"Error: {str(e)}"

    class LangVoiceVoicesTool(CrewAIBaseTool):
        """CrewAI tool for listing voices."""
        
        name: str = "langvoice_list_voices"
        description: str = "Get all available voices for text-to-speech."
        
        api_key: Optional[str] = None
        _client: Optional[LangVoiceClient] = None
        
        def __init__(self, api_key: Optional[str] = None, **kwargs):
            super().__init__(**kwargs)
            self.api_key = api_key
        
        @property
        def client(self) -> LangVoiceClient:
            if self._client is None:
                self._client = LangVoiceClient(api_key=self.api_key)
            return self._client
        
        def _run(self) -> str:
            try:
                voices = self.client.list_voices()
                return "Available voices: " + ", ".join([f"{v.id} ({v.name})" for v in voices])
            except Exception as e:
                return f"Error: {str(e)}"

    class LangVoiceLanguagesTool(CrewAIBaseTool):
        """CrewAI tool for listing languages."""
        
        name: str = "langvoice_list_languages"
        description: str = "Get all supported languages for text-to-speech."
        
        api_key: Optional[str] = None
        _client: Optional[LangVoiceClient] = None
        
        def __init__(self, api_key: Optional[str] = None, **kwargs):
            super().__init__(**kwargs)
            self.api_key = api_key
        
        @property
        def client(self) -> LangVoiceClient:
            if self._client is None:
                self._client = LangVoiceClient(api_key=self.api_key)
            return self._client
        
        def _run(self) -> str:
            try:
                languages = self.client.list_languages()
                return "Supported languages: " + ", ".join([f"{l.id} ({l.name})" for l in languages])
            except Exception as e:
                return f"Error: {str(e)}"

    class LangVoiceCrewAIToolkit:
        """
        Convenience class for using LangVoice with CrewAI.
        
        Example:
            >>> from crewai import Agent, Task, Crew
            >>> from langvoice_sdk.tools.crewai_tools import LangVoiceCrewAIToolkit
            >>> 
            >>> toolkit = LangVoiceCrewAIToolkit(api_key="your-langvoice-key")
            >>> 
            >>> agent = Agent(
            ...     role="Voice Generator",
            ...     goal="Generate natural speech",
            ...     tools=toolkit.get_tools()
            ... )
        """
        
        def __init__(self, api_key: Optional[str] = None) -> None:
            self.api_key = api_key
        
        def get_tools(self) -> List[CrewAIBaseTool]:
            """Get all LangVoice tools for CrewAI."""
            return [
                LangVoiceTTSTool(api_key=self.api_key),
                LangVoiceMultiVoiceTool(api_key=self.api_key),
                LangVoiceVoicesTool(api_key=self.api_key),
                LangVoiceLanguagesTool(api_key=self.api_key),
            ]

    def get_all_crewai_tools(api_key: Optional[str] = None) -> List[CrewAIBaseTool]:
        """Get all LangVoice tools for CrewAI."""
        _check_crewai()
        return [
            LangVoiceTTSTool(api_key=api_key),
            LangVoiceMultiVoiceTool(api_key=api_key),
            LangVoiceVoicesTool(api_key=api_key),
            LangVoiceLanguagesTool(api_key=api_key),
        ]

else:
    # Stub classes
    class LangVoiceTTSTool:  # type: ignore
        def __init__(self, *args, **kwargs):
            _check_crewai()

    class LangVoiceMultiVoiceTool:  # type: ignore
        def __init__(self, *args, **kwargs):
            _check_crewai()

    class LangVoiceVoicesTool:  # type: ignore
        def __init__(self, *args, **kwargs):
            _check_crewai()

    class LangVoiceLanguagesTool:  # type: ignore
        def __init__(self, *args, **kwargs):
            _check_crewai()

    class LangVoiceCrewAIToolkit:  # type: ignore
        def __init__(self, *args, **kwargs):
            _check_crewai()

    def get_all_crewai_tools(api_key: Optional[str] = None) -> List:
        _check_crewai()
        return []
