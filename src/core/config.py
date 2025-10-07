"""
Configuration settings for the KYC Document Processing API.
"""


from typing import Any, ClassVar
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Basic settings
    project_name: str = "NCB KYC Document Processing API"
    version: str = "2.0.0"
    debug: bool = False

    # Server settings - restrictive by default for security
    host: str = "127.0.0.1"  # Only local access by default, use 0.0.0.0 for container deployment
    port: int = 8080

    # Google Cloud settings
    project_id: str = Field(default="test-project", env="PROJECT_ID", description="Google Cloud Project ID")
    location: str = Field(default="us", env="LOCATION")

    # API settings
    api_prefix: str = "/api/v1"
    allowed_origins: list[str] = ["*"]
    enable_docs: bool = True

    # File processing limits
    max_file_size_mb: int = 20
    max_pages: int = 10
    timeout_seconds: int = 300

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Authentication (for future use)
    api_key_header: str = "X-API-Key"
    enable_auth: bool = False

    # Optional features
    enable_cache: bool = False
    redis_url: str | None = Field(default=None, description="Redis URL for caching")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


class DocumentAIConfig(BaseSettings):
    """Configuration for Document AI processors."""

    project_id: str = Field(default="inductive-choir-463216-s9", env="PROJECT_ID")
    location: str = Field(default="us", env="LOCATION")

    # Custom NCB Extractor configuration
    custom_extractor_id: str = Field(default="577a3e74c6c1cd44", env="CUSTOM_EXTRACTOR_ID")
    custom_extractor_version_id: str | None = Field(env="CUSTOM_EXTRACTOR_VERSION_ID", default="pretrained-foundation-model-v1.5-pro-2025-06-20")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    @property
    def PROJECT_ID(self) -> str:
        return self.project_id

    @property
    def LOCATION(self) -> str:
        return self.location

    @property
    def CUSTOM_EXTRACTOR_ID(self) -> str:
        return self.custom_extractor_id

    @property
    def CUSTOM_EXTRACTOR_VERSION_ID(self) -> str | None:
        return self.custom_extractor_version_id

    # Document type metadata for NCB KYC
    DOCUMENT_TYPES: ClassVar[dict[str, dict[str, Any]]] = {
        "ncb-kyc-form": {
            "description": "NCB Bank KYC Form",
            "category": "kyc-document",
            "extractor": "custom-ncb-extractor",
            "alias": "ncb-kyc",
            "supported_entities": [
                "Date", "CIF", "FirstName", "MiddleName", "LastName", "DateOfBirth",
                "CityOfBirth", "MaritalStatus", "Gender", "PassportNumber", "EmiratesIDNumber",
                "Residency", "NumberOfYears", "CountryOfResidence", "StreetName", "Area",
                "MakaniNumber", "BuildingNumber", "FlatVillaNumber", "CityEmirate", "POBox",
                "Country", "MobileNumber", "AlternativeNumber", "EmailAddress", "Employer",
                "Department", "Designation", "GrossMonthlyIncome", "NatureOfBusiness",
                "PercentageOfOwnership"
            ],
            "average_confidence": 0.90,
        }
    }

    # Confidence thresholds
    CONFIDENCE_THRESHOLDS: ClassVar[dict[str, float]] = {
        "ncb-kyc-form": 0.5,
        "default": 0.5,
    }


# Global settings instances
settings = Settings()
document_ai_config = DocumentAIConfig()