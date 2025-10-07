"""
Test script for NCB KYC Document Processing API.
"""

import asyncio
import os
from pathlib import Path

from src.services.document_ai_client import DocumentAIClient


async def test_extraction():
    """Test the custom extractor with a sample PDF."""
    
    # Initialize the client
    client = DocumentAIClient()
    DocumentAIClient.initialize()
    
    try:
        # Test with the sample PDF
        test_pdf_path = Path("C:/Users/abish/Desktop/kyc-extraction-ncb/test.pdf")
        
        if not test_pdf_path.exists():
            print(f"Test PDF not found at {test_pdf_path}")
            return
        
        print(f"Testing extraction with: {test_pdf_path}")
        
        # Read the PDF file
        with open(test_pdf_path, "rb") as f:
            file_content = f.read()
        
        print(f"PDF file size: {len(file_content)} bytes")
        
        # Test basic client functionality first
        print("Testing Document AI client configuration...")
        processor_info = client.get_processor_info()
        print(f"Processor info: {processor_info}")
        
        # Extract information with timeout
        print("Starting document extraction...")
        import asyncio
        
        try:
            document = await asyncio.wait_for(
                client.extract_kyc_information(file_content),
                timeout=60.0  # 60 second timeout
            )
            print("✅ Document extraction completed successfully!")
        except asyncio.TimeoutError:
            print("❌ Document extraction timed out after 60 seconds")
            return
        except Exception as e:
            print(f"❌ Document extraction failed: {e}")
            return
        
        # Parse extracted fields
        extracted_data = client.parse_extracted_fields(document)
        
        print("\n=== EXTRACTION RESULTS ===")
        print(f"Page 1 Fields:")
        for field_name, field_data in extracted_data["page_one"].items():
            if field_data and field_data.get("value"):
                print(f"  {field_name}: {field_data['value']} (confidence: {field_data['confidence']:.3f})")
        
        print(f"\nPage 2 Fields:")
        for field_name, field_data in extracted_data["page_two"].items():
            if field_data and field_data.get("value"):
                print(f"  {field_name}: {field_data['value']} (confidence: {field_data['confidence']:.3f})")
        
        # Calculate statistics
        total_fields = len(extracted_data["page_one"]) + len(extracted_data["page_two"])
        extracted_fields = sum(1 for page_data in extracted_data.values() 
                              for field_data in page_data.values() 
                              if field_data and field_data.get("value"))
        
        print(f"\n=== STATISTICS ===")
        print(f"Total fields: {total_fields}")
        print(f"Extracted fields: {extracted_fields}")
        print(f"Extraction rate: {extracted_fields/total_fields*100:.1f}%")
        
        if extracted_fields > 0:
            all_confidences = [field_data["confidence"] 
                             for page_data in extracted_data.values() 
                             for field_data in page_data.values() 
                             if field_data and field_data.get("value")]
            avg_confidence = sum(all_confidences) / len(all_confidences)
            print(f"Average confidence: {avg_confidence:.3f}")
        
    except Exception as e:
        print(f"Error during extraction: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        DocumentAIClient.cleanup()


if __name__ == "__main__":
    asyncio.run(test_extraction())
