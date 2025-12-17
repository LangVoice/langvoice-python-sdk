"""Custom exceptions for LangVoice SDK."""

from typing import Optional


class LangVoiceError(Exception):
    """Base exception for LangVoice SDK."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(LangVoiceError):
    """Raised when API key is invalid or missing."""

    def __init__(self, message: str = "Invalid or missing API key") -> None:
        super().__init__(message, status_code=401)


class RateLimitError(LangVoiceError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, status_code=429)


class ValidationError(LangVoiceError):
    """Raised when request validation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=400)


class APIError(LangVoiceError):
    """Raised when API returns an error."""

    pass
