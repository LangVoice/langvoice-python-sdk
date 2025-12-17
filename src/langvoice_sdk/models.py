"""Data models for LangVoice SDK."""

from typing import List, Optional
from pydantic import BaseModel, Field


class Voice(BaseModel):
    """Voice model."""

    id: str
    name: str
    gender: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None


class Language(BaseModel):
    """Language model."""

    id: str
    name: str
    voices: Optional[List[str]] = None


class GenerateRequest(BaseModel):
    """Request model for TTS generation."""

    text: str = Field(..., max_length=5000, description="Text to convert to speech")
    voice: str = Field(..., description="Voice ID (e.g., 'heart', 'michael')")
    language: str = Field(..., description="Language code (e.g., 'american_english')")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed (0.5-2.0)")


class MultiVoiceRequest(BaseModel):
    """Request model for multi-voice TTS generation."""

    text: str = Field(
        ...,
        max_length=5000,
        description="Text with [voice] markers (e.g., '[heart] Hello [michael] Hi')",
    )
    language: str = Field(..., description="Language code for all voices")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed (0.5-2.0)")


class VoicesResponse(BaseModel):
    """Response model for voices endpoint."""

    voices: List[Voice]


class LanguagesResponse(BaseModel):
    """Response model for languages endpoint."""

    languages: List[Language]


class GenerateResponse(BaseModel):
    """Response metadata for TTS generation."""

    audio_data: bytes
    duration: Optional[float] = None
    generation_time: Optional[float] = None
    characters_processed: Optional[int] = None
