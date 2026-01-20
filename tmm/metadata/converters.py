"""
Data type converters for metadata values.

Handles conversion between different metadata representations (e.g., image formats).
"""

from typing import Tuple, Optional, Any


def extract_image_data(data: bytes, mime_type: str) -> Tuple[bytes, str]:
    """
    Extract and normalize image data.

    Args:
        data: Raw image data
        mime_type: MIME type of the image

    Returns:
        Tuple of (image_data, mime_type)
    """
    # Normalize MIME type
    mime_type = mime_type.lower()
    if 'jpeg' in mime_type or 'jpg' in mime_type:
        mime_type = 'image/jpeg'
    elif 'png' in mime_type:
        mime_type = 'image/png'

    return (data, mime_type)


def prepare_image_data(value: Any) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Prepare image data for writing.

    Args:
        value: Image data (can be tuple of (data, mime) or just data)

    Returns:
        Tuple of (image_data, mime_type) or (None, None) if invalid
    """
    if value is None:
        return (None, None)

    # If value is a tuple, assume it's (data, mime_type)
    if isinstance(value, tuple) and len(value) == 2:
        data, mime_type = value
        if isinstance(data, bytes):
            return (data, mime_type)

    # If value is bytes, assume JPEG (most common)
    if isinstance(value, bytes):
        # Try to detect format from magic bytes
        mime_type = detect_image_format(value)
        return (value, mime_type)

    return (None, None)


def detect_image_format(data: bytes) -> str:
    """
    Detect image format from magic bytes.

    Args:
        data: Image data

    Returns:
        MIME type string
    """
    if data.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg'
    elif data.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png'
    elif data.startswith(b'GIF87a') or data.startswith(b'GIF89a'):
        return 'image/gif'
    elif data.startswith(b'BM'):
        return 'image/bmp'
    else:
        # Default to JPEG
        return 'image/jpeg'
