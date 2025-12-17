"""Async LangVoice API client."""

import os
from pathlib import Path
from typing import Optional, Union, List

try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from langvoice_sdk.models import (
    Voice,
    Language,
    GenerateRequest,
    MultiVoiceRequest,
    VoicesResponse,
    LanguagesResponse,
    GenerateResponse,
)
from langvoice_sdk.exceptions import (
    AuthenticationError,
    RateLimitError,
    ValidationError,
    APIError,
)


class AsyncLangVoiceClient:
    """Async LangVoice API client for text-to-speech generation."""

    BASE_URL = "https://www.langvoice.pro/api"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60,
    ) -> None:
        """
        Initialize the async LangVoice client.

        Args:
            api_key: API key for authentication.
            base_url: Base URL for the API.
            timeout: Request timeout in seconds.
        """
        if not AIOHTTP_AVAILABLE:
            raise ImportError(
                "aiohttp is required for async client. "
                "Install with: pip install langvoice[async]"
            )

        self.api_key = api_key or os.getenv("LANGVOICE_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Pass api_key or set LANGVOICE_API_KEY environment variable."
            )

        self.base_url = base_url or self.BASE_URL
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json",
                },
                timeout=self.timeout,
            )
        return self._session

    async def _handle_response(self, response: aiohttp.ClientResponse) -> None:
        """Handle API response and raise appropriate exceptions."""
        if response.status == 401:
            raise AuthenticationError()
        elif response.status == 429:
            raise RateLimitError()
        elif response.status == 400:
            try:
                error_data = await response.json()
                message = error_data.get("error", "Validation error")
            except Exception:
                message = await response.text() or "Validation error"
            raise ValidationError(message)
        elif response.status >= 400:
            try:
                error_data = await response.json()
                message = error_data.get("error", f"API error: {response.status}")
            except Exception:
                message = await response.text() or f"API error: {response.status}"
            raise APIError(message, status_code=response.status)

    async def generate(
        self,
        text: str,
        voice: str = "heart",
        language: str = "american_english",
        speed: float = 1.0,
        output_path: Optional[Union[str, Path]] = None,
    ) -> GenerateResponse:
        """
        Generate speech from text asynchronously.

        Args:
            text: Text to convert to speech.
            voice: Voice ID.
            language: Language code.
            speed: Speech speed.
            output_path: Optional path to save the audio file.

        Returns:
            GenerateResponse with audio data and metadata.
        """
        request = GenerateRequest(text=text, voice=voice, language=language, speed=speed)
        session = await self._get_session()

        async with session.post(
            f"{self.base_url}/tts/generate",
            json=request.model_dump(),
        ) as response:
            await self._handle_response(response)
            audio_data = await response.read()

            if output_path:
                Path(output_path).write_bytes(audio_data)

            return GenerateResponse(
                audio_data=audio_data,
                duration=self._parse_float_header(response.headers.get("X-Audio-Duration")),
                generation_time=self._parse_float_header(
                    response.headers.get("X-Generation-Time")
                ),
                characters_processed=self._parse_int_header(
                    response.headers.get("X-Characters-Processed")
                ),
            )

    async def generate_multi_voice(
        self,
        text: str,
        language: str = "american_english",
        speed: float = 1.0,
        output_path: Optional[Union[str, Path]] = None,
    ) -> GenerateResponse:
        """Generate speech with multiple voices asynchronously."""
        request = MultiVoiceRequest(text=text, language=language, speed=speed)
        session = await self._get_session()

        async with session.post(
            f"{self.base_url}/tts/multi-voice-text",
            json=request.model_dump(),
        ) as response:
            await self._handle_response(response)
            audio_data = await response.read()

            if output_path:
                Path(output_path).write_bytes(audio_data)

            return GenerateResponse(
                audio_data=audio_data,
                duration=self._parse_float_header(response.headers.get("X-Audio-Duration")),
                generation_time=self._parse_float_header(
                    response.headers.get("X-Generation-Time")
                ),
                characters_processed=self._parse_int_header(
                    response.headers.get("X-Characters-Processed")
                ),
            )

    async def list_voices(self) -> List[Voice]:
        """Get all available voices asynchronously."""
        session = await self._get_session()

        async with session.get(f"{self.base_url}/tts/voices") as response:
            await self._handle_response(response)
            data = VoicesResponse(**(await response.json()))
            return data.voices

    async def list_languages(self) -> List[Language]:
        """Get all supported languages asynchronously."""
        session = await self._get_session()

        async with session.get(f"{self.base_url}/tts/languages") as response:
            await self._handle_response(response)
            data = LanguagesResponse(**(await response.json()))
            return data.languages

    async def text_to_speech(
        self,
        text: str,
        voice: str = "heart",
        language: str = "american_english",
        speed: float = 1.0,
    ) -> bytes:
        """Simple async method to convert text to speech."""
        response = await self.generate(text=text, voice=voice, language=language, speed=speed)
        return response.audio_data

    @staticmethod
    def _parse_float_header(value: Optional[str]) -> Optional[float]:
        """Parse float from header value."""
        if value:
            try:
                return float(value.rstrip("s"))
            except ValueError:
                pass
        return None

    @staticmethod
    def _parse_int_header(value: Optional[str]) -> Optional[int]:
        """Parse int from header value."""
        if value:
            try:
                return int(value)
            except ValueError:
                pass
        return None

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "AsyncLangVoiceClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Async context manager exit."""
        await self.close()
