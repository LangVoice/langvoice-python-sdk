"""Tests for LangVoice client."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from langvoice_sdk import langvoice_sdkClient
from langvoice_sdk.exceptions import (
    AuthenticationError,
    RateLimitError,
    ValidationError,
    APIError,
)
from langvoice_sdk.models import GenerateRequest, Voice, Language


class TestLangVoiceClient:
    """Tests for LangVoiceClient."""

    def test_init_with_api_key(self) -> None:
        """Test client initialization with API key."""
        client = LangVoiceClient(api_key="test-key")
        assert client.api_key == "test-key"

    def test_init_without_api_key_raises_error(self) -> None:
        """Test that missing API key raises AuthenticationError."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(AuthenticationError):
                LangVoiceClient(api_key=None)

    def test_init_with_env_var(self) -> None:
        """Test client initialization with environment variable."""
        with patch.dict("os.environ", {"LANGVOICE_API_KEY": "env-key"}):
            client = LangVoiceClient()
            assert client.api_key == "env-key"

    @patch("langvoice.client.requests.Session")
    def test_generate_success(self, mock_session_class: Mock) -> None:
        """Test successful TTS generation."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio data"
        mock_response.headers = {
            "X-Audio-Duration": "2.5s",
            "X-Generation-Time": "0.3s",
            "X-Characters-Processed": "20",
        }
        mock_session.post.return_value = mock_response

        client = LangVoiceClient(api_key="test-key")
        response = client.generate(text="Hello world", voice="heart")

        assert response.audio_data == b"fake audio data"
        assert response.duration == 2.5
        assert response.characters_processed == 20

    @patch("langvoice.client.requests.Session")
    def test_generate_authentication_error(self, mock_session_class: Mock) -> None:
        """Test that 401 response raises AuthenticationError."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 401
        mock_session.post.return_value = mock_response

        client = LangVoiceClient(api_key="invalid-key")
        with pytest.raises(AuthenticationError):
            client.generate(text="Hello", voice="heart")

    @patch("langvoice.client.requests.Session")
    def test_generate_rate_limit_error(self, mock_session_class: Mock) -> None:
        """Test that 429 response raises RateLimitError."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 429
        mock_session.post.return_value = mock_response

        client = LangVoiceClient(api_key="test-key")
        with pytest.raises(RateLimitError):
            client.generate(text="Hello", voice="heart")

    @patch("langvoice.client.requests.Session")
    def test_list_voices(self, mock_session_class: Mock) -> None:
        """Test listing voices."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "voices": [
                {"id": "heart", "name": "Heart"},
                {"id": "michael", "name": "Michael"},
            ]
        }
        mock_session.get.return_value = mock_response

        client = LangVoiceClient(api_key="test-key")
        voices = client.list_voices()

        assert len(voices) == 2
        assert voices[0].id == "heart"
        assert voices[1].id == "michael"

    @patch("langvoice.client.requests.Session")
    def test_list_languages(self, mock_session_class: Mock) -> None:
        """Test listing languages."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "languages": [
                {"id": "american_english", "name": "American English"},
                {"id": "british_english", "name": "British English"},
            ]
        }
        mock_session.get.return_value = mock_response

        client = LangVoiceClient(api_key="test-key")
        languages = client.list_languages()

        assert len(languages) == 2
        assert languages[0].id == "american_english"

    def test_context_manager(self) -> None:
        """Test client as context manager."""
        with patch("langvoice.client.requests.Session"):
            with LangVoiceClient(api_key="test-key") as client:
                assert client.api_key == "test-key"


class TestModels:
    """Tests for data models."""

    def test_generate_request_validation(self) -> None:
        """Test GenerateRequest validation."""
        request = GenerateRequest(
            text="Hello",
            voice="heart",
            language="american_english",
            speed=1.0,
        )
        assert request.text == "Hello"
        assert request.speed == 1.0

    def test_generate_request_speed_bounds(self) -> None:
        """Test speed parameter bounds."""
        with pytest.raises(ValueError):
            GenerateRequest(
                text="Hello",
                voice="heart",
                language="american_english",
                speed=3.0,  # Too high
            )

    def test_voice_model(self) -> None:
        """Test Voice model."""
        voice = Voice(id="heart", name="Heart", gender="female")
        assert voice.id == "heart"
        assert voice.name == "Heart"


class TestOpenAITools:
    """Tests for OpenAI tools."""

    def test_get_openai_tools(self) -> None:
        """Test getting OpenAI tool definitions."""
        from langvoice_sdk.tools import get_openai_tools

        tools = get_openai_tools()
        assert len(tools) == 3
        assert tools[0]["function"]["name"] == "langvoice_text_to_speech"

    @patch("langvoice.tools.openai_tools.LangVoiceClient")
    def test_handle_tool_call(self, mock_client_class: Mock) -> None:
        """Test handling OpenAI tool calls."""
        from langvoice_sdk.tools import handle_openai_tool_call

        mock_client = Mock()
        mock_client.list_voices.return_value = [
            Voice(id="heart", name="Heart"),
        ]
        mock_client_class.return_value = mock_client

        result = handle_openai_tool_call(
            "langvoice_list_voices",
            {},
            api_key="test-key",
        )

        data = json.loads(result)
        assert data["success"] is True
        assert len(data["voices"]) == 1
