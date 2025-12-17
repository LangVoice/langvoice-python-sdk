"""LangVoice Python SDK - Text-to-Speech API wrapper with AI agent integrations."""

from langvoice_sdk.client import LangVoiceClient
from langvoice_sdk.models import (
    Voice,
    Language,
    GenerateRequest,
    MultiVoiceRequest,
    VoicesResponse,
    LanguagesResponse,
)
from langvoice_sdk.exceptions import (
    LangVoiceError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    APIError,
)

__version__ = "0.1.0"
__all__ = [
    "LangVoiceClient",
    "Voice",
    "Language",
    "GenerateRequest",
    "MultiVoiceRequest",
    "VoicesResponse",
    "LanguagesResponse",
    "LangVoiceError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "APIError",
]
