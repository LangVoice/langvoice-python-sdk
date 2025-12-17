"""LangChain tools for LangVoice TTS."""

import base64
from typing import Optional, Type, List, Any

try:
    from langchain_core.tools import BaseTool
    from langchain_core.callbacks import CallbackManagerForToolRun
    from pydantic import BaseModel, Field

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseTool = object  # type: ignore
    BaseModel = object  # type: ignore

from langvoice_sdk.client import LangVoiceClient


def _check_langchain() -> None:
    """Check if LangChain is available."""
    if not LANGCHAIN_AVAILABLE:
        raise ImportError(
            "langchain-core is required for LangChain tools. "
            "Install with: pip install langvoice[langchain]"
        )


if LANGCHAIN_AVAILABLE:

    class TTSInput(BaseModel):
        """Input schema for TTS tool."""

        text: str = Field(description="Text to convert to speech. Maximum 5000 characters.")
        voice: str = Field(
            default="heart",
            description="Voice ID (e.g., 'heart', 'michael', 'emma')",
        )
        language: str = Field(
            default="american_english",
            description="Language code (e.g., 'american_english', 'british_english')",
        )
        speed: float = Field(
            default=1.0,
            description="Speech speed from 0.5 (slow) to 2.0 (fast)",
            ge=0.5,
            le=2.0,
        )

    class MultiVoiceInput(BaseModel):
        """Input schema for multi-voice TTS tool."""

        text: str = Field(
            description="Text with [voice] markers. Example: '[heart] Hello! [michael] Hi!'"
        )
        language: str = Field(
            default="american_english",
            description="Language code for all voices",
        )
        speed: float = Field(
            default=1.0,
            description="Speech speed from 0.5 to 2.0",
            ge=0.5,
            le=2.0,
        )

    class LangVoiceTTSTool(BaseTool):
        """LangChain tool for text-to-speech generation."""

        name: str = "langvoice_tts"
        description: str = (
            "Convert text to natural-sounding speech audio using LangVoice TTS. "
            "Saves audio to output.mp3 and returns confirmation with duration."
        )
        args_schema: Type[BaseModel] = TTSInput
        return_direct: bool = False

        api_key: Optional[str] = None
        output_file: Optional[str] = "output.mp3"
        _client: Optional[LangVoiceClient] = None

        def __init__(
            self,
            api_key: Optional[str] = None,
            output_file: Optional[str] = "output.mp3",
            **kwargs: Any
        ) -> None:
            """Initialize the tool with API key and optional output file path."""
            super().__init__(**kwargs)
            self.api_key = api_key
            self.output_file = output_file
            self._client = None

        @property
        def client(self) -> LangVoiceClient:
            """Get or create the LangVoice client."""
            if self._client is None:
                self._client = LangVoiceClient(api_key=self.api_key)
            return self._client

        def _run(
            self,
            text: str,
            voice: str = "heart",
            language: str = "american_english",
            speed: float = 1.0,
            run_manager: Optional[CallbackManagerForToolRun] = None,
        ) -> str:
            """Execute the TTS generation."""
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
                    return (
                        f"✅ Speech generated! Duration: {response.duration}s. "
                        f"Audio (base64): {audio_base64[:100]}..."
                    )
            except Exception as e:
                return f"❌ Error generating speech: {str(e)}"

    class LangVoiceMultiVoiceTool(BaseTool):
        """LangChain tool for multi-voice speech generation."""

        name: str = "langvoice_multi_voice"
        description: str = (
            "Generate speech with multiple voices using bracket notation. "
            "Use [voice_name] to switch voices. Example: '[heart] Hello! [michael] Hi there!'"
        )
        args_schema: Type[BaseModel] = MultiVoiceInput
        return_direct: bool = False

        api_key: Optional[str] = None
        _client: Optional[LangVoiceClient] = None

        def __init__(self, api_key: Optional[str] = None, **kwargs: Any) -> None:
            """Initialize the tool with API key."""
            super().__init__(**kwargs)
            self.api_key = api_key
            self._client = None

        @property
        def client(self) -> LangVoiceClient:
            """Get or create the LangVoice client."""
            if self._client is None:
                self._client = LangVoiceClient(api_key=self.api_key)
            return self._client

        def _run(
            self,
            text: str,
            language: str = "american_english",
            speed: float = 1.0,
            run_manager: Optional[CallbackManagerForToolRun] = None,
        ) -> str:
            """Execute the multi-voice TTS generation."""
            try:
                response = self.client.generate_multi_voice(
                    text=text,
                    language=language,
                    speed=speed,
                )
                audio_base64 = base64.b64encode(response.audio_data).decode("utf-8")
                return (
                    f"Successfully generated multi-voice speech. "
                    f"Duration: {response.duration}s. "
                    f"Audio available in base64 format."
                )
            except Exception as e:
                return f"Error generating multi-voice speech: {str(e)}"

    class LangVoiceVoicesTool(BaseTool):
        """LangChain tool for listing available voices."""

        name: str = "langvoice_list_voices"
        description: str = "Get a list of all available voices for text-to-speech generation."
        return_direct: bool = False

        api_key: Optional[str] = None
        _client: Optional[LangVoiceClient] = None

        def __init__(self, api_key: Optional[str] = None, **kwargs: Any) -> None:
            """Initialize the tool with API key."""
            super().__init__(**kwargs)
            self.api_key = api_key
            self._client = None

        @property
        def client(self) -> LangVoiceClient:
            """Get or create the LangVoice client."""
            if self._client is None:
                self._client = LangVoiceClient(api_key=self.api_key)
            return self._client

        def _run(
            self,
            run_manager: Optional[CallbackManagerForToolRun] = None,
        ) -> str:
            """Get available voices."""
            try:
                voices = self.client.list_voices()
                voice_list = ", ".join([f"{v.id} ({v.name})" for v in voices])
                return f"Available voices: {voice_list}"
            except Exception as e:
                return f"Error listing voices: {str(e)}"

    class LangVoiceLanguagesTool(BaseTool):
        """LangChain tool for listing supported languages."""

        name: str = "langvoice_list_languages"
        description: str = "Get a list of all supported languages for text-to-speech generation."
        return_direct: bool = False

        api_key: Optional[str] = None
        _client: Optional[LangVoiceClient] = None

        def __init__(self, api_key: Optional[str] = None, **kwargs: Any) -> None:
            """Initialize the tool with API key."""
            super().__init__(**kwargs)
            self.api_key = api_key
            self._client = None

        @property
        def client(self) -> LangVoiceClient:
            """Get or create the LangVoice client."""
            if self._client is None:
                self._client = LangVoiceClient(api_key=self.api_key)
            return self._client

        def _run(
            self,
            run_manager: Optional[CallbackManagerForToolRun] = None,
        ) -> str:
            """Get supported languages."""
            try:
                languages = self.client.list_languages()
                lang_list = ", ".join([f"{lang.id} ({lang.name})" for lang in languages])
                return f"Supported languages: {lang_list}"
            except Exception as e:
                return f"Error listing languages: {str(e)}"

    class LangVoiceLangChainToolkit:
        """
        Convenience class for using LangVoice with LangChain.
        
        Set API key once and get all tools easily.
        
        Example:
            >>> from langchain_openai import ChatOpenAI
            >>> from langchain.agents import create_openai_functions_agent, AgentExecutor
            >>> from langvoice_sdk.tools.langchain_tools import LangVoiceLangChainToolkit
            >>> 
            >>> # Initialize once with API key
            >>> toolkit = LangVoiceLangChainToolkit(api_key="your-langvoice-key")
            >>> 
            >>> # Get all tools
            >>> tools = toolkit.get_tools()
            >>> 
            >>> # Create agent
            >>> llm = ChatOpenAI(model="gpt-4")
            >>> agent_executor = AgentExecutor(agent=agent, tools=tools)
        """

        def __init__(self, api_key: Optional[str] = None) -> None:
            """Initialize toolkit with LangVoice API key."""
            self.api_key = api_key
            self._client = LangVoiceClient(api_key=api_key)

        def get_tools(self) -> List[BaseTool]:
            """Get all LangVoice tools."""
            return [
                LangVoiceTTSTool(api_key=self.api_key),
                LangVoiceMultiVoiceTool(api_key=self.api_key),
                LangVoiceVoicesTool(api_key=self.api_key),
                LangVoiceLanguagesTool(api_key=self.api_key),
            ]

        def get_tts_tool(self) -> LangVoiceTTSTool:
            """Get the text-to-speech tool."""
            return LangVoiceTTSTool(api_key=self.api_key)

        def get_multi_voice_tool(self) -> LangVoiceMultiVoiceTool:
            """Get the multi-voice tool."""
            return LangVoiceMultiVoiceTool(api_key=self.api_key)

        def get_voices_tool(self) -> LangVoiceVoicesTool:
            """Get the list voices tool."""
            return LangVoiceVoicesTool(api_key=self.api_key)

        def get_languages_tool(self) -> LangVoiceLanguagesTool:
            """Get the list languages tool."""
            return LangVoiceLanguagesTool(api_key=self.api_key)

    def get_all_langchain_tools(api_key: Optional[str] = None) -> List[BaseTool]:
        """
        Get all LangVoice tools for LangChain.

        Args:
            api_key: LangVoice API key.

        Returns:
            List of LangChain tool instances.

        Example:
            >>> from langchain.agents import initialize_agent, AgentType
            >>> from langchain_openai import ChatOpenAI
            >>> from langvoice_sdk.tools.langchain_tools import get_all_langchain_tools
            >>> 
            >>> tools = get_all_langchain_tools(api_key="your-langvoice-key")
            >>> llm = ChatOpenAI(model="gpt-4")
            >>> agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS)
        """
        _check_langchain()
        return [
            LangVoiceTTSTool(api_key=api_key),
            LangVoiceMultiVoiceTool(api_key=api_key),
            LangVoiceVoicesTool(api_key=api_key),
            LangVoiceLanguagesTool(api_key=api_key),
        ]

else:
    # Stub classes when LangChain is not available
    class LangVoiceTTSTool:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            _check_langchain()

    class LangVoiceMultiVoiceTool:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            _check_langchain()

    class LangVoiceVoicesTool:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            _check_langchain()

    class LangVoiceLanguagesTool:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            _check_langchain()

    class LangVoiceLangChainToolkit:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            _check_langchain()

    def get_all_langchain_tools(api_key: Optional[str] = None) -> List[Any]:
        _check_langchain()
        return []
