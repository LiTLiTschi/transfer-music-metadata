"""
Metadata reader for audio files.

Provides a unified interface to read metadata from different audio formats.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Any
import mutagen
from mutagen.id3 import ID3, APIC, COMM
from mutagen.mp4 import MP4, MP4Cover
from mutagen.flac import FLAC, Picture
from mutagen.wave import WAVE
from mutagen.aiff import AIFF

from .mappings import TAG_MAPPINGS, SUPPORTED_EXTENSIONS
from .converters import extract_image_data


class MetadataReader:
    """Read metadata from audio files in a format-agnostic way."""

    def __init__(self, file_path: str):
        """
        Initialize the metadata reader.

        Args:
            file_path: Path to the audio file
        """
        self.file_path = Path(file_path)
        self.format_type = self._detect_format()
        self.audio_file = None

        if self.format_type:
            try:
                self.audio_file = mutagen.File(str(self.file_path))
            except Exception as e:
                raise ValueError(f"Failed to load audio file {file_path}: {e}")

    def _detect_format(self) -> Optional[str]:
        """
        Detect the audio format based on file extension.

        Returns:
            Format type string or None if unsupported
        """
        ext = self.file_path.suffix.lower()
        return SUPPORTED_EXTENSIONS.get(ext)

    def read_tag(self, tag_name: str) -> Optional[Any]:
        """
        Read a specific tag from the audio file.

        Args:
            tag_name: Unified tag name (e.g., 'initial_key', 'album')

        Returns:
            Tag value or None if not found
        """
        if not self.audio_file or not self.format_type:
            return None

        mappings = TAG_MAPPINGS.get(self.format_type, {})
        format_tag = mappings.get(tag_name)

        if not format_tag:
            return None

        try:
            if self.format_type == 'mp3':
                return self._read_mp3_tag(tag_name, format_tag)
            elif self.format_type == 'm4a':
                return self._read_m4a_tag(tag_name, format_tag)
            elif self.format_type == 'flac':
                return self._read_flac_tag(tag_name, format_tag)
            elif self.format_type in ['wav', 'aiff']:
                return self._read_wav_aiff_tag(tag_name, format_tag)
        except Exception as e:
            # Log error but don't crash
            return None

        return None

    def _read_mp3_tag(self, tag_name: str, format_tag: str) -> Optional[Any]:
        """Read tag from MP3 file."""
        if tag_name == 'cover_art':
            # Handle APIC frames
            apic_frames = [v for k, v in self.audio_file.tags.items() if k.startswith('APIC')]
            if apic_frames:
                return extract_image_data(apic_frames[0].data, apic_frames[0].mime)
            return None
        elif tag_name == 'comment':
            # Handle COMM frames
            comm_frames = [v for k, v in self.audio_file.tags.items() if k.startswith('COMM')]
            if comm_frames:
                return str(comm_frames[0].text[0]) if comm_frames[0].text else None
            return None
        else:
            # Handle text frames
            if format_tag in self.audio_file.tags:
                tag_value = self.audio_file.tags[format_tag]
                if hasattr(tag_value, 'text'):
                    return str(tag_value.text[0]) if tag_value.text else None
                return str(tag_value)
            return None

    def _read_m4a_tag(self, tag_name: str, format_tag: str) -> Optional[Any]:
        """Read tag from M4A file."""
        if tag_name == 'cover_art':
            # Handle cover art
            if 'covr' in self.audio_file.tags:
                covers = self.audio_file.tags['covr']
                if covers:
                    cover = covers[0]
                    # Determine mime type from imageformat
                    mime = 'image/jpeg' if cover.imageformat == MP4Cover.FORMAT_JPEG else 'image/png'
                    return extract_image_data(bytes(cover), mime)
            return None
        elif tag_name in ['initial_key', 'label']:
            # Handle freeform atoms
            if format_tag in self.audio_file.tags:
                values = self.audio_file.tags[format_tag]
                if values:
                    # Freeform atoms return bytes
                    return values[0].decode('utf-8') if isinstance(values[0], bytes) else str(values[0])
            return None
        else:
            # Handle standard atoms
            if format_tag in self.audio_file.tags:
                values = self.audio_file.tags[format_tag]
                if values:
                    return str(values[0])
            return None

    def _read_flac_tag(self, tag_name: str, format_tag: str) -> Optional[Any]:
        """Read tag from FLAC file."""
        if tag_name == 'cover_art':
            # Handle pictures
            if self.audio_file.pictures:
                pic = self.audio_file.pictures[0]
                return extract_image_data(pic.data, pic.mime)
            return None
        else:
            # Handle vorbis comments
            if format_tag.lower() in self.audio_file:
                values = self.audio_file[format_tag.lower()]
                if values:
                    return values[0]
            return None

    def _read_wav_aiff_tag(self, tag_name: str, format_tag: str) -> Optional[Any]:
        """Read tag from WAV/AIFF file (uses ID3v2 if available)."""
        if not hasattr(self.audio_file, 'tags') or self.audio_file.tags is None:
            return None

        # WAV/AIFF can have ID3 tags
        return self._read_mp3_tag(tag_name, format_tag)

    def read_all_tags(self, tag_names: list) -> Dict[str, Any]:
        """
        Read multiple tags at once.

        Args:
            tag_names: List of unified tag names

        Returns:
            Dictionary mapping tag names to values
        """
        result = {}
        for tag_name in tag_names:
            value = self.read_tag(tag_name)
            if value is not None:
                result[tag_name] = value
        return result

    def get_filename_without_ext(self) -> str:
        """Get the filename without extension."""
        return self.file_path.stem

    def get_format(self) -> Optional[str]:
        """Get the detected format type."""
        return self.format_type
