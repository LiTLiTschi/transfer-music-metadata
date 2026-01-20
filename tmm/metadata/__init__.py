"""
Metadata handling module for TMM.
"""

from .reader import MetadataReader
from .writer import MetadataWriter
from .mappings import TAG_MAPPINGS

__all__ = ["MetadataReader", "MetadataWriter", "TAG_MAPPINGS"]
