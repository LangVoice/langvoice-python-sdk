"""Main LangVoice API client."""

import os
from pathlib import Path
from typing import Optional, Union, List

import requests

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
    LangVoiceError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    APIError,
)


class LangVoiceClient:
    """LangVoice API client for text-to-speech generation."""

    BASE_URL = "https://www.langvoice.pro/api"

    # Available voices
    AMERICAN_VOICES = [
        "heart", "bella", "nicole", "sarah", "nova", "sky", "jessica",
        "river", "michael", "fenrir", "eric", "liam", "onyx", "adam"
    ]
    BRITISH_VOICES = [
        "emma", "isabella", "alice", "lily", "george", "fable", "lewis", "daniel"
    ]
    ALL_VOICES = AMERICAN_VOICES + BRITISH_VOICES

    # Supported languages
    LANGUAGES = [
        "american_english", "british_english", "spanish", "french",
        "hindi", "italian", "japanese", "brazilian_portuguese", "mandarin_chinese"
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60,
    ) -> None:
        """
        Initialize the LangVoice client.

        Args:
            api_key: API key for authentication. If not provided, reads from
                     LANGVOICE_API_KEY environment variable.
            base_url: Base URL for the API. Defaults to https://www.langvoice.pro/api
            timeout: Request timeout in seconds. Defaults to 60.
        """
        self.api_key = api_key or os.getenv("LANGVOICE_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Pass api_key or set LANGVOICE_API_KEY environment variable."
            )

        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        })

    def _handle_response(self, response: requests.Response) -> requests.Response:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code == 401:
            raise AuthenticationError()
        elif response.status_code == 429:
            raise RateLimitError()
        elif response.status_code == 400:
            try:
                error_data = response.json()
                message = error_data.get("error", "Validation error")
            except Exception:
                message = response.text or "Validation error"
            raise ValidationError(message)
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("error", f"API error: {response.status_code}")
            except Exception:
                message = response.text or f"API error: {response.status_code}"
            raise APIError(message, status_code=response.status_code)
        return response

    def generate(
        self,
        text: str,
        voice: str = "heart",
        language: str = "american_english",
        speed: float = 1.0,
        output_path: Optional[Union[str, Path]] = None,
    ) -> GenerateResponse:
        """
        Generate speech from text.

        Args:
            text: Text to convert to speech (max 5000 characters).
            voice: Voice ID (e.g., 'heart', 'michael').
            language: Language code (e.g., 'american_english').
            speed: Speech speed from 0.5 to 2.0. Defaults to 1.0.
            output_path: Optional path to save the audio file.

        Returns:
            GenerateResponse with audio data and metadata.

        Example:
            >>> client = LangVoiceClient(api_key="your-api-key")
            >>> response = client.generate("Hello world!", voice="heart")
            >>> with open("output.mp3", "wb") as f:
            ...     f.write(response.audio_data)
        """
        request = GenerateRequest(text=text, voice=voice, language=language, speed=speed)

        response = self._session.post(
            f"{self.base_url}/tts/generate",
            json=request.model_dump(),
            timeout=self.timeout,
        )
        self._handle_response(response)

        audio_data = response.content

        if output_path:
            Path(output_path).write_bytes(audio_data)

        return GenerateResponse(
            audio_data=audio_data,
            duration=self._parse_float_header(response.headers.get("X-Audio-Duration")),
            generation_time=self._parse_float_header(response.headers.get("X-Generation-Time")),
            characters_processed=self._parse_int_header(
                response.headers.get("X-Characters-Processed")
            ),
        )

    def generate_multi_voice(
        self,
        text: str,
        language: str = "american_english",
        speed: float = 1.0,
        output_path: Optional[Union[str, Path]] = None,
    ) -> GenerateResponse:
        """
        Generate speech with multiple voices.

        Args:
            text: Text with [voice] markers (e.g., "[heart] Hello [michael] Hi there").
            language: Language code for all voices.
            speed: Speech speed from 0.5 to 2.0. Defaults to 1.0.
            output_path: Optional path to save the audio file.

        Returns:
            GenerateResponse with audio data and metadata.

        Example:
            >>> client = LangVoiceClient(api_key="your-api-key")
            >>> response = client.generate_multi_voice(
            ...     "[heart] Welcome! [michael] Thanks for joining us.",
            ...     language="american_english"
            ... )
        """
        request = MultiVoiceRequest(text=text, language=language, speed=speed)

        response = self._session.post(
            f"{self.base_url}/tts/multi-voice-text",
            json=request.model_dump(),
            timeout=self.timeout,
        )
        self._handle_response(response)

        audio_data = response.content

        if output_path:
            Path(output_path).write_bytes(audio_data)

        return GenerateResponse(
            audio_data=audio_data,
            duration=self._parse_float_header(response.headers.get("X-Audio-Duration")),
            generation_time=self._parse_float_header(response.headers.get("X-Generation-Time")),
            characters_processed=self._parse_int_header(
                response.headers.get("X-Characters-Processed")
            ),
        )

    def list_voices(self) -> List[Voice]:
        """
        Get all available voices.

        Returns:
            List of Voice objects.

        Example:
            >>> client = LangVoiceClient(api_key="your-api-key")
            >>> voices = client.list_voices()
            >>> for voice in voices:
            ...     print(f"{voice.id}: {voice.name}")
        """
        response = self._session.get(
            f"{self.base_url}/tts/voices",
            timeout=self.timeout,
        )
        self._handle_response(response)

        data = VoicesResponse(**response.json())
        return data.voices

    def list_languages(self) -> List[Language]:
        """
        Get all supported languages.

        Returns:
            List of Language objects.

        Example:
            >>> client = LangVoiceClient(api_key="your-api-key")
            >>> languages = client.list_languages()
            >>> for lang in languages:
            ...     print(f"{lang.id}: {lang.name}")
        """
        response = self._session.get(
            f"{self.base_url}/tts/languages",
            timeout=self.timeout,
        )
        self._handle_response(response)

        data = LanguagesResponse(**response.json())
        return data.languages

    def text_to_speech(
        self,
        text: str,
        voice: str = "heart",
        language: str = "american_english",
        speed: float = 1.0,
    ) -> bytes:
        """
        Simple method to convert text to speech and return audio bytes.

        This is a convenience method for quick TTS generation.

        Args:
            text: Text to convert.
            voice: Voice ID.
            language: Language code.
            speed: Speech speed.

        Returns:
            Audio data as bytes (MP3 format).
        """
        response = self.generate(text=text, voice=voice, language=language, speed=speed)
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

    def close(self) -> None:
        """Close the HTTP session."""
        self._session.close()

    def __enter__(self) -> "LangVoiceClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Context manager exit."""
        self.close()
