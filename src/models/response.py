"""Response models for NCB Bank KYC Document Processing API."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Model for error details."""

    code: str = Field(..., description="Error code identifier")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(default=None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": {
                        "validation_errors": ["File format not supported"],
                        "invalid_fields": ["file"]
                    }
                },
                {
                    "code": "PROCESSING_ERROR",
                    "message": "Failed to process document",
                    "details": {"error_type": "document_ai_timeout"}
                }
            ]
        }


class ErrorResponse(BaseModel):
    """Model for error responses."""

    error: ErrorDetail = Field(..., description="Error details")
    request_id: Optional[str] = Field(default=None, description="Request identifier for tracking")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class HealthResponse(BaseModel):
    """Model for health check response."""

    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "status": "healthy",
                    "version": "2.0.0",
                    "timestamp": "2024-10-03T06:30:00Z"
                }
            ]
        }


class ExtractedField(BaseModel):
    """Model for a single extracted field."""

    value: str = Field(..., description="Extracted value")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    page: int = Field(..., ge=0, description="Page number where field was found")
    bounding_box: Optional[dict] = Field(default=None, description="Bounding box coordinates")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "value": "John",
                    "confidence": 0.95,
                    "page": 0,
                    "bounding_box": {"x": 0.1, "y": 0.2, "width": 0.1, "height": 0.05}
                }
            ]
        }


class PageOneFields(BaseModel):
    """Model for fields extracted from page 1."""
    
    Date: Optional[ExtractedField] = Field(default=None, description="Date field")
    CIF: Optional[ExtractedField] = Field(default=None, description="CIF number")
    FirstName: Optional[ExtractedField] = Field(default=None, description="First name")
    MiddleName: Optional[ExtractedField] = Field(default=None, description="Middle name")
    LastName: Optional[ExtractedField] = Field(default=None, description="Last name")
    DateOfBirth: Optional[ExtractedField] = Field(default=None, description="Date of birth")
    CityOfBirth: Optional[ExtractedField] = Field(default=None, description="City of birth")
    MaritalStatus: Optional[ExtractedField] = Field(default=None, description="Marital status")
    Gender: Optional[ExtractedField] = Field(default=None, description="Gender")
    PassportNumber: Optional[ExtractedField] = Field(default=None, description="Passport number")
    EmiratesIDNumber: Optional[ExtractedField] = Field(default=None, description="Emirates ID number")
    Residency: Optional[ExtractedField] = Field(default=None, description="Residency status")
    NumberOfYears: Optional[ExtractedField] = Field(default=None, description="Number of years")
    CountryOfResidence: Optional[ExtractedField] = Field(default=None, description="Country of residence")
    StreetName: Optional[ExtractedField] = Field(default=None, description="Street name")
    Area: Optional[ExtractedField] = Field(default=None, description="Area")
    MakaniNumber: Optional[ExtractedField] = Field(default=None, description="Makani number")
    BuildingNumber: Optional[ExtractedField] = Field(default=None, description="Building number")
    FlatVillaNumber: Optional[ExtractedField] = Field(default=None, description="Flat/Villa number")
    CityEmirate: Optional[ExtractedField] = Field(default=None, description="City/Emirate")
    POBox: Optional[ExtractedField] = Field(default=None, description="PO Box")
    Country: Optional[ExtractedField] = Field(default=None, description="Country")
    MobileNumber: Optional[ExtractedField] = Field(default=None, description="Mobile number")
    AlternativeNumber: Optional[ExtractedField] = Field(default=None, description="Alternative number")
    EmailAddress: Optional[ExtractedField] = Field(default=None, description="Email address")


class PageTwoFields(BaseModel):
    """Model for fields extracted from page 2."""
    
    Employer: Optional[ExtractedField] = Field(default=None, description="Employer name")
    Department: Optional[ExtractedField] = Field(default=None, description="Department")
    Designation: Optional[ExtractedField] = Field(default=None, description="Designation")
    GrossMonthlyIncome: Optional[ExtractedField] = Field(default=None, description="Gross monthly income")
    NatureOfBusiness: Optional[ExtractedField] = Field(default=None, description="Nature of business")
    PercentageOfOwnership: Optional[ExtractedField] = Field(default=None, description="Percentage of ownership")


class ExtractedInformation(BaseModel):
    """Model for all extracted information."""
    
    page_one: PageOneFields = Field(..., description="Fields from page 1")
    page_two: PageTwoFields = Field(..., description="Fields from page 2")


class ProcessingSummary(BaseModel):
    """Model for processing summary information."""

    total_pages: int = Field(..., ge=0, description="Total number of pages processed")
    successful_pages: int = Field(..., ge=0, description="Number of successfully processed pages")
    failed_pages: int = Field(..., ge=0, description="Number of failed pages")
    average_confidence: float = Field(..., ge=0.0, le=1.0, description="Average confidence across all extractions")
    processing_time_seconds: float = Field(..., ge=0.0, description="Total processing time in seconds")
    extractor_used: str = Field(..., description="Extractor that was used")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "total_pages": 2,
                    "successful_pages": 2,
                    "failed_pages": 0,
                    "average_confidence": 0.91,
                    "processing_time_seconds": 8.5,
                    "extractor_used": "custom-ncb-extractor"
                }
            ]
        }


class ProcessResponse(BaseModel):
    """Model for document processing response."""

    request_id: str = Field(..., description="Unique request identifier")
    filename: str = Field(..., description="Original filename")
    processing_mode: str = Field(..., description="Processing mode used")
    extracted_information: ExtractedInformation = Field(..., description="All extracted information")
    summary: ProcessingSummary = Field(..., description="Processing summary")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Processing timestamp")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "request_id": "09c771f6-ca28-4285-ad61-095701366967",
                    "filename": "kyc_document.pdf",
                    "processing_mode": "custom",
                    "extracted_information": {
                        "page_one": {
                            "FirstName": {
                                "value": "John",
                                "confidence": 0.95,
                                "page": 0
                            },
                            "LastName": {
                                "value": "Doe",
                                "confidence": 0.94,
                                "page": 0
                            }
                        },
                        "page_two": {
                            "Employer": {
                                "value": "ABC Company",
                            "confidence": 0.92,
                                "page": 1
                            }
                        }
                    },
                    "summary": {
                        "total_pages": 2,
                        "successful_pages": 2,
                        "failed_pages": 0,
                        "average_confidence": 0.91,
                        "processing_time_seconds": 8.5,
                        "extractor_used": "custom-ncb-extractor"
                    },
                    "timestamp": "2024-10-03T15:49:47Z"
                }
            ]
        }