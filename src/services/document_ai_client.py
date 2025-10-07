"""
Async Document AI client for processing NCB KYC documents.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional

from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from google.cloud.documentai_v1.types import Document
from loguru import logger

from src.core.config import DocumentAIConfig


class DocumentAIClient:
    """Async wrapper for Google Cloud Document AI operations."""

    _executor: ThreadPoolExecutor | None = None

    def __init__(self, location: str = None):
        self.config = DocumentAIConfig()
        self.location = location or self.config.LOCATION
        self.project_id = self.config.PROJECT_ID

        opts = ClientOptions(api_endpoint=f"{self.location}-documentai.googleapis.com")
        self.client = documentai.DocumentProcessorServiceClient(client_options=opts)

        logger.info(f"Initialized DocumentAI client for location: {self.location}")

    @classmethod
    def initialize(cls) -> None:
        """Initialize the thread pool executor."""
        if cls._executor is None:
            cls._executor = ThreadPoolExecutor(
                max_workers=4, thread_name_prefix="docai"
            )
            logger.info("Initialized DocumentAI thread pool executor")

    @classmethod
    def cleanup(cls) -> None:
        """Cleanup the thread pool executor."""
        if cls._executor:
            cls._executor.shutdown(wait=True)
            cls._executor = None
            logger.info("Cleaned up DocumentAI thread pool executor")

    def _build_processor_name(
        self, processor_id: str, version_id: Optional[str] = None
    ) -> str:
        """Build the full processor resource name."""
        if version_id:
            return self.client.processor_version_path(
                self.project_id, self.location, processor_id, version_id
            )
        else:
            return self.client.processor_path(
                self.project_id, self.location, processor_id
            )

    def _process_document_sync(
        self,
        file_content: bytes,
        processor_id: str,
        version_id: Optional[str] = None,
        mime_type: str = "application/pdf",
        field_mask: Optional[str] = None,
        pages: Optional[list[int]] = None,
    ) -> Document:
        """
        Synchronous document processing (runs in thread pool).

        Args:
            file_content: Document content as bytes
            processor_id: Document AI processor ID
            version_id: Processor version ID
            mime_type: MIME type of the document
            field_mask: Optional field mask for response
            pages: Optional list of specific pages to process (0-based)

        Returns:
            Document: Processed document result
        """
        processor_name = self._build_processor_name(processor_id, version_id)

        raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)

        process_options = None
        if pages:
            # Convert 0-based to 1-based for IndividualPageSelector (API requirement)
            one_based_pages = [p + 1 for p in pages]
            process_options = documentai.ProcessOptions(
                individual_page_selector=documentai.ProcessOptions.IndividualPageSelector(
                    pages=one_based_pages
                )
            )

        request = documentai.ProcessRequest(
            name=processor_name,
            raw_document=raw_document,
            field_mask=field_mask,
            process_options=process_options,
        )

        logger.debug(f"Processing document with processor: {processor_id[:8]}...")
        
        # Add timeout to prevent infinite loops
        import time
        start_time = time.time()
        timeout_seconds = 300  # 5 minutes timeout
        
        try:
            result = self.client.process_document(request=request)
            processing_time = time.time() - start_time
            logger.info(f"Document processing completed in {processing_time:.2f} seconds")
            return result.document
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Document processing failed after {processing_time:.2f} seconds: {e}")
            raise

    async def process_document(
        self,
        file_content: bytes,
        processor_id: str,
        version_id: Optional[str] = None,
        mime_type: str = "application/pdf",
        field_mask: Optional[str] = None,
        pages: Optional[list[int]] = None,
    ) -> Document:
        """
        Async document processing.

        Args:
            file_content: Document content as bytes
            processor_id: Document AI processor ID
            version_id: Processor version ID
            mime_type: MIME type of the document
            field_mask: Optional field mask for response
            pages: Optional list of specific pages to process (0-based)

        Returns:
            Document: Processed document result
        """
        if self._executor is None:
            raise RuntimeError(
                "DocumentAI client not initialized. Call initialize() first."
            )

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._process_document_sync,
            file_content,
            processor_id,
            version_id,
            mime_type,
            field_mask,
            pages,
        )

    async def extract_kyc_information(
        self,
        file_content: bytes,
        mime_type: str = "application/pdf",
    ) -> Document:
        """
        Extract KYC information using the custom NCB extractor.

        Args:
            file_content: Document content as bytes
            mime_type: MIME type of the document

        Returns:
            Document: Processed document result with extracted fields
        """
        logger.info("Extracting KYC information with custom NCB extractor")

        try:
            # Try with specific version first if available
            if self.config.CUSTOM_EXTRACTOR_VERSION_ID:
                return await self.process_document(
                    file_content=file_content,
                    processor_id=self.config.CUSTOM_EXTRACTOR_ID,
                    version_id=self.config.CUSTOM_EXTRACTOR_VERSION_ID,
                    mime_type=mime_type,
                )
            else:
                # Use default deployed version
                return await self.process_document(
                    file_content=file_content,
                    processor_id=self.config.CUSTOM_EXTRACTOR_ID,
                    version_id=None,
                    mime_type=mime_type,
                )
        except Exception as e:
            logger.error(f"Failed to extract with custom NCB extractor: {e}")
            raise

    def parse_extracted_fields(self, document: Document) -> Dict[str, Any]:
        """
        Parse the extracted fields from Document AI response.

        Args:
            document: Processed Document AI document

        Returns:
            Dictionary containing parsed field information
        """
        extracted_fields = {
            "page_one": {},
            "page_two": {}
        }

        # Get entities from the document
        entities = document.entities if hasattr(document, 'entities') else []

        # Define field mappings for page 1
        page_one_fields = [
            "Date", "CIF", "FirstName", "MiddleName", "LastName", "DateOfBirth",
            "CityOfBirth", "MaritalStatus", "Gender", "PassportNumber", "EmiratesIDNumber",
            "Residency", "NumberOfYears", "CountryOfResidence", "StreetName", "Area",
            "MakaniNumber", "BuildingNumber", "FlatVillaNumber", "CityEmirate", "POBox",
            "Country", "MobileNumber", "AlternativeNumber", "EmailAddress"
        ]

        # Define field mappings for page 2
        page_two_fields = [
            "Employer", "Department", "Designation", "GrossMonthlyIncome",
            "NatureOfBusiness", "PercentageOfOwnership"
        ]

        # Process entities and map them to pages
        for entity in entities:
            field_name = entity.type_
            confidence = entity.confidence if hasattr(entity, 'confidence') else 0.0
            value = entity.mention_text if hasattr(entity, 'mention_text') else ""
            
            # Determine which page this field belongs to
            if field_name in page_one_fields:
                page_num = 0
                page_key = "page_one"
            elif field_name in page_two_fields:
                page_num = 1
                page_key = "page_two"
            else:
                continue  # Skip unknown fields

            # Extract bounding box information if available
            bounding_box = None
            if hasattr(entity, 'page_anchor') and entity.page_anchor:
                page_anchor = entity.page_anchor.page_refs[0] if entity.page_anchor.page_refs else None
                if page_anchor and hasattr(page_anchor, 'bounding_poly'):
                    # Convert bounding poly to simple bounding box
                    vertices = page_anchor.bounding_poly.normalized_vertices
                    if vertices:
                        x_coords = [v.x for v in vertices]
                        y_coords = [v.y for v in vertices]
                        bounding_box = {
                            "x": min(x_coords),
                            "y": min(y_coords),
                            "width": max(x_coords) - min(x_coords),
                            "height": max(y_coords) - min(y_coords)
                        }

            extracted_fields[page_key][field_name] = {
                "value": value,
                "confidence": confidence,
                "page": page_num,
                "bounding_box": bounding_box
            }

        return extracted_fields

    def get_processor_info(self) -> Dict[str, Any]:
        """Get information about the custom NCB processor."""
        return {
            "custom_extractor": {
                "id": self.config.CUSTOM_EXTRACTOR_ID,
                "version": self.config.CUSTOM_EXTRACTOR_VERSION_ID,
                "name": "custom-ncb-extractor",
                "description": "Custom NCB Bank KYC Form Extractor",
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
        }