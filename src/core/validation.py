"""
Input validation utilities for the KYC Document Processing API.
"""


from fastapi import HTTPException, UploadFile

from .config import settings

# Supported MIME types
SUPPORTED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/tiff",
    "image/tif",
}

# File extensions mapping
EXTENSION_TO_MIME = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
}


def validate_file_type(
    content_type: str | None, filename: str | None = None
) -> str:
    """
    Validate file type based on content type and filename.

    Args:
        content_type: MIME type from the request
        filename: Original filename (optional)

    Returns:
        Validated MIME type

    Raises:
        HTTPException: If file type is not supported
    """
    if not content_type:
        if filename:
            # Try to determine from filename extension
            extension = None
            if "." in filename:
                extension = "." + filename.split(".")[-1].lower()

            if extension in EXTENSION_TO_MIME:
                content_type = EXTENSION_TO_MIME[extension]
            else:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": {
                            "code": "INVALID_FILE_TYPE",
                            "message": f"Unsupported file extension: {extension}",
                            "supported_types": list(SUPPORTED_MIME_TYPES),
                        }
                    },
                )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "MISSING_CONTENT_TYPE",
                        "message": "Content-Type header is required",
                        "supported_types": list(SUPPORTED_MIME_TYPES),
                    }
                },
            )

    # Normalize content type
    content_type = content_type.lower().split(";")[0].strip()

    if content_type not in SUPPORTED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_FILE_TYPE",
                    "message": f"Unsupported file type: {content_type}",
                    "supported_types": list(SUPPORTED_MIME_TYPES),
                }
            },
        )

    return content_type


def validate_file_size(file_size: int) -> None:
    """
    Validate file size against maximum allowed size.

    Args:
        file_size: Size of the file in bytes

    Raises:
        HTTPException: If file is too large
    """
    max_size_bytes = settings.max_file_size_mb * 1024 * 1024

    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=413,
            detail={
                "error": {
                    "code": "FILE_TOO_LARGE",
                    "message": f"File size ({file_size} bytes) exceeds maximum allowed size",
                    "max_size_mb": settings.max_file_size_mb,
                    "max_size_bytes": max_size_bytes,
                }
            },
        )


async def validate_upload_file(file: UploadFile) -> bytes:
    """
    Validate an uploaded file and return its content.

    Args:
        file: FastAPI UploadFile object

    Returns:
        File content as bytes

    Raises:
        HTTPException: If validation fails
    """
    # Validate file type
    validate_file_type(file.content_type, file.filename)

    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "FILE_READ_ERROR",
                    "message": f"Failed to read file: {e!s}",
                }
            },
        )

    # Validate file size
    validate_file_size(len(content))

    # Basic file content validation
    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "EMPTY_FILE", "message": "File is empty"}},
        )

    return content


def validate_pages(pages: list[int] | None, total_pages: int) -> list[int]:
    """
    Validate page numbers against document.

    Args:
        pages: List of page numbers (0-based) to process
        total_pages: Total number of pages in document

    Returns:
        Validated list of page numbers

    Raises:
        HTTPException: If page numbers are invalid
    """
    if pages is None:
        # Process all pages
        return list(range(total_pages))

    if not pages:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "EMPTY_PAGES_LIST",
                    "message": "Pages list cannot be empty",
                }
            },
        )

    # Validate page numbers
    invalid_pages = [p for p in pages if p < 0 or p >= total_pages]
    if invalid_pages:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_PAGE_NUMBERS",
                    "message": f"Invalid page numbers: {invalid_pages}",
                    "total_pages": total_pages,
                    "valid_range": f"0-{total_pages - 1}",
                }
            },
        )

    # Check page limit
    if len(pages) > settings.max_pages:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "TOO_MANY_PAGES",
                    "message": f"Too many pages requested: {len(pages)}",
                    "max_pages": settings.max_pages,
                }
            },
        )

    return sorted(list(set(pages)))  # Remove duplicates and sort
