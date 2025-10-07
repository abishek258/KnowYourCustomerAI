from __future__ import annotations

import io
import time
import uuid
from typing import Any, Dict

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from loguru import logger

from src.models.request import ProcessingOptions
from src.models.response import (
    ErrorDetail,
    ErrorResponse,
    ExtractedField,
    ExtractedInformation,
    PageOneFields,
    PageTwoFields,
    ProcessResponse,
    ProcessingSummary,
)
from src.services.document_ai_client import DocumentAIClient


router = APIRouter()


def _create_extracted_field(field_data: Dict[str, Any]) -> ExtractedField | None:
    """Create an ExtractedField from field data."""
    if not field_data or not field_data.get("value"):
        return None
    
    return ExtractedField(
        value=field_data["value"],
        confidence=field_data.get("confidence", 0.0),
        page=field_data.get("page", 0),
        bounding_box=field_data.get("bounding_box")
    )


def _create_page_one_fields(page_one_data: Dict[str, Any]) -> PageOneFields:
    """Create PageOneFields from extracted data."""
    return PageOneFields(
        Date=_create_extracted_field(page_one_data.get("Date")),
        CIF=_create_extracted_field(page_one_data.get("CIF")),
        FirstName=_create_extracted_field(page_one_data.get("FirstName")),
        MiddleName=_create_extracted_field(page_one_data.get("MiddleName")),
        LastName=_create_extracted_field(page_one_data.get("LastName")),
        DateOfBirth=_create_extracted_field(page_one_data.get("DateOfBirth")),
        CityOfBirth=_create_extracted_field(page_one_data.get("CityOfBirth")),
        MaritalStatus=_create_extracted_field(page_one_data.get("MaritalStatus")),
        Gender=_create_extracted_field(page_one_data.get("Gender")),
        PassportNumber=_create_extracted_field(page_one_data.get("PassportNumber")),
        EmiratesIDNumber=_create_extracted_field(page_one_data.get("EmiratesIDNumber")),
        Residency=_create_extracted_field(page_one_data.get("Residency")),
        NumberOfYears=_create_extracted_field(page_one_data.get("NumberOfYears")),
        CountryOfResidence=_create_extracted_field(page_one_data.get("CountryOfResidence")),
        StreetName=_create_extracted_field(page_one_data.get("StreetName")),
        Area=_create_extracted_field(page_one_data.get("Area")),
        MakaniNumber=_create_extracted_field(page_one_data.get("MakaniNumber")),
        BuildingNumber=_create_extracted_field(page_one_data.get("BuildingNumber")),
        FlatVillaNumber=_create_extracted_field(page_one_data.get("FlatVillaNumber")),
        CityEmirate=_create_extracted_field(page_one_data.get("CityEmirate")),
        POBox=_create_extracted_field(page_one_data.get("POBox")),
        Country=_create_extracted_field(page_one_data.get("Country")),
        MobileNumber=_create_extracted_field(page_one_data.get("MobileNumber")),
        AlternativeNumber=_create_extracted_field(page_one_data.get("AlternativeNumber")),
        EmailAddress=_create_extracted_field(page_one_data.get("EmailAddress")),
    )


def _create_page_two_fields(page_two_data: Dict[str, Any]) -> PageTwoFields:
    """Create PageTwoFields from extracted data."""
    return PageTwoFields(
        Employer=_create_extracted_field(page_two_data.get("Employer")),
        Department=_create_extracted_field(page_two_data.get("Department")),
        Designation=_create_extracted_field(page_two_data.get("Designation")),
        GrossMonthlyIncome=_create_extracted_field(page_two_data.get("GrossMonthlyIncome")),
        NatureOfBusiness=_create_extracted_field(page_two_data.get("NatureOfBusiness")),
        PercentageOfOwnership=_create_extracted_field(page_two_data.get("PercentageOfOwnership")),
    )


@router.post("/process")
async def process_document(
    file: UploadFile = File(...),
    extractor_mode: str = Form("custom"),
) -> ProcessResponse:
    """
    Process NCB KYC document using custom extractor.
    
    Args:
        file: The uploaded PDF file
        extractor_mode: Processing mode (currently only supports 'custom')
    
    Returns:
        ProcessResponse: Extracted information and processing summary
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        content = await file.read()
        
        # Initialize Document AI client
        client = DocumentAIClient()
        DocumentAIClient.initialize()
        
        try:
            # Extract KYC information
            document = await client.extract_kyc_information(content)
            
            # Parse extracted fields
            extracted_data = client.parse_extracted_fields(document)
            
            # Create response objects
            page_one_fields = _create_page_one_fields(extracted_data["page_one"])
            page_two_fields = _create_page_two_fields(extracted_data["page_two"])
            
            extracted_information = ExtractedInformation(
                page_one=page_one_fields,
                page_two=page_two_fields
            )
            
            # Calculate processing summary
            processing_time = time.time() - start_time
            
            # Calculate average confidence
            all_fields = []
            for field_data in extracted_data["page_one"].values():
                if field_data and field_data.get("confidence"):
                    all_fields.append(field_data["confidence"])
            for field_data in extracted_data["page_two"].values():
                if field_data and field_data.get("confidence"):
                    all_fields.append(field_data["confidence"])
            
            average_confidence = sum(all_fields) / len(all_fields) if all_fields else 0.0
            
            # Count successful pages (pages with at least one extracted field)
            successful_pages = 0
            if any(extracted_data["page_one"].values()):
                successful_pages += 1
            if any(extracted_data["page_two"].values()):
                successful_pages += 1
            
            summary = ProcessingSummary(
                total_pages=2,  # NCB KYC forms are typically 2 pages
                successful_pages=successful_pages,
                failed_pages=2 - successful_pages,
                average_confidence=average_confidence,
                processing_time_seconds=processing_time,
                extractor_used="custom-ncb-extractor"
            )
            
            return ProcessResponse(
                request_id=request_id,
                filename=file.filename,
                processing_mode=extractor_mode,
                extracted_information=extracted_information,
                summary=summary
            )
            
        finally:
            DocumentAIClient.cleanup()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Processing failed")
        
        error_response = ErrorResponse(
            error=ErrorDetail(
                code="PROCESSING_ERROR",
                message="Failed to process document",
                details={"error_type": type(e).__name__, "error_message": str(e)}
            ),
            request_id=request_id
        )
        
        raise HTTPException(status_code=500, detail=error_response.dict())


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}


@router.get("/info")
async def get_api_info():
    """Get API information and supported fields."""
    try:
        client = DocumentAIClient()
        processor_info = client.get_processor_info()
        
        return {
            "api_name": "NCB Bank KYC Document Processing API",
            "version": "2.0.0",
            "description": "API for extracting information from NCB Bank KYC forms using custom Document AI extractor",
            "processor_info": processor_info,
            "supported_fields": {
                "page_one": [
                    "Date", "CIF", "FirstName", "MiddleName", "LastName", "DateOfBirth",
                    "CityOfBirth", "MaritalStatus", "Gender", "PassportNumber", "EmiratesIDNumber",
                    "Residency", "NumberOfYears", "CountryOfResidence", "StreetName", "Area",
                    "MakaniNumber", "BuildingNumber", "FlatVillaNumber", "CityEmirate", "POBox",
                    "Country", "MobileNumber", "AlternativeNumber", "EmailAddress"
                ],
                "page_two": [
                    "Employer", "Department", "Designation", "GrossMonthlyIncome",
                    "NatureOfBusiness", "PercentageOfOwnership"
                ]
            }
        }
    except Exception as e:
        logger.exception("Error in info endpoint")
        raise HTTPException(status_code=500, detail=str(e))