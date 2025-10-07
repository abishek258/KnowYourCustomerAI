"""Request models for NCB Bank KYC Document Processing API."""

from typing import Optional
from pydantic import BaseModel, Field


class ProcessingOptions(BaseModel):
    """Model for document processing options."""

    extractor_mode: str = Field(
        default="custom",
        description="Processing mode: 'custom' for custom NCB extractor"
    )
    confidence_threshold_override: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Override default confidence threshold (0.0-1.0)"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "extractor_mode": "custom",
                    "confidence_threshold_override": None
                },
                {
                    "extractor_mode": "custom",
                    "confidence_threshold_override": 0.8
                }
            ]
        }