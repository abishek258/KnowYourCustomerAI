# NCB KYC Document Processing API

A streamlined backend API for extracting information from NCB Bank KYC forms using a custom Document AI extractor.

## Overview

This API is designed to extract 25 specific fields from NCB Bank KYC forms across two pages:

### Page 1 Fields (25 fields)
- Date, CIF, FirstName, MiddleName, LastName
- DateOfBirth, CityOfBirth, MaritalStatus, Gender
- PassportNumber, EmiratesIDNumber, Residency, NumberOfYears
- CountryOfResidence, StreetName, Area, MakaniNumber
- BuildingNumber, FlatVillaNumber, CityEmirate, POBox
- Country, MobileNumber, AlternativeNumber, EmailAddress

### Page 2 Fields (6 fields)
- Employer, Department, Designation
- GrossMonthlyIncome, NatureOfBusiness, PercentageOfOwnership

## Setup

1. **Environment Configuration**
   ```bash
   cp env.template .env
   ```
   
   Update the `.env` file with your Google Cloud credentials:
   ```
   PROJECT_ID=your-project-id
   LOCATION=us
   CUSTOM_EXTRACTOR_ID=your-custom-extractor-processor-id
   CUSTOM_EXTRACTOR_VERSION_ID=your-custom-extractor-version-id
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the API**
   ```bash
   python -m src.api.main
   ```

## API Endpoints

### POST `/api/v1/documents/process`
Process a KYC document and extract information.

**Request:**
- `file`: PDF file (multipart/form-data)
- `extractor_mode`: "custom" (form data)

**Response:**
```json
{
  "request_id": "uuid",
  "filename": "document.pdf",
  "processing_mode": "custom",
  "extracted_information": {
    "page_one": {
      "FirstName": {
        "value": "John",
        "confidence": 0.95,
        "page": 0,
        "bounding_box": {...}
      },
      // ... other page 1 fields
    },
    "page_two": {
      "Employer": {
        "value": "ABC Company",
        "confidence": 0.92,
        "page": 1,
        "bounding_box": {...}
      },
      // ... other page 2 fields
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
```

### GET `/api/v1/documents/health`
Health check endpoint.

### GET `/api/v1/documents/info`
Get API information and supported fields.

## Testing

Run the test script to verify extraction:
```bash
python test_extraction.py
```

## Architecture

- **Models**: Pydantic models for request/response validation
- **Services**: Document AI client for processing
- **API Routes**: FastAPI endpoints for document processing
- **Configuration**: Environment-based settings for Google Cloud

## Key Features

- ✅ Custom Document AI extractor integration
- ✅ Structured field extraction (25 fields from page 1, 6 from page 2)
- ✅ Confidence scoring for each field
- ✅ Bounding box information for field locations
- ✅ Comprehensive error handling
- ✅ Async processing for better performance
- ✅ Clean, type-safe API responses

## File Structure

```
src/
├── api/
│   ├── main.py              # FastAPI app setup
│   └── routes/
│       └── process.py        # Document processing endpoints
├── core/
│   └── config.py            # Configuration settings
├── models/
│   ├── request.py           # Request models
│   └── response.py          # Response models
└── services/
    └── document_ai_client.py # Document AI integration
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `PROJECT_ID` | Google Cloud Project ID | Yes |
| `LOCATION` | Document AI location | Yes |
| `CUSTOM_EXTRACTOR_ID` | Custom extractor processor ID | Yes |
| `CUSTOM_EXTRACTOR_VERSION_ID` | Extractor version ID | No |

## Error Handling

The API provides detailed error responses with:
- Error codes and messages
- Request tracking IDs
- Timestamps
- Additional error details

## Performance

- Async processing for better concurrency
- Thread pool executor for Document AI calls
- Configurable timeouts and limits
- Efficient field parsing and validation
