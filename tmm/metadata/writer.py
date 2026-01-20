"""
Metadata writer for audio files.

Provides a unified interface to write metadata to different audio formats.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Any
import mutagen
from mutagen.id3 import ID3, APIC, COMM, TKEY, TPUB, TALB, TIT2, TPE1
from mutagen.mp4 import MP4, MP4Cover
from mutagen.flac import FLAC, Picture
from mutagen.wave import WAVE
from mutagen.aiff import AIFF

from .mappings import TAG_MAPPINGS, SUPPORTED_EXTENSIONS
from .converters import prepare_image_data


class MetadataWriter:
    """Write metadata to audio files in a format-agnostic way."""

    def __init__(self, file_path: str):
        """
        Initialize the metadata writer.

        Args:
            file_path: Path to the audio file
        """
        self.file_path = Path(file_path)
        self.format_type = self._detect_format()
        self.audio_file = None

        if self.format_type:
            try:
                self.audio_file = mutagen.File(str(self.file_path))
                # Add tags if they don't exist
                if self.audio_file.tags is None:
                    self.audio_file.add_tags()
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

    def write_tag(self, tag_name: str, value: Any) -> bool:
        """
        Write a specific tag to the audio file.

        Args:
            tag_name: Unified tag name (e.g., 'initial_key', 'album')
            value: Value to write

        Returns:
            True if successful, False otherwise
        """
        if not self.audio_file or not self.format_type or value is None:
            return False

        mappings = TAG_MAPPINGS.get(self.format_type, {})
        format_tag = mappings.get(tag_name)

        if not format_tag:
            return False

        try:
            if self.format_type == 'mp3':
                return self._write_mp3_tag(tag_name, format_tag, value)
            elif self.format_type == 'm4a':
                return self._write_m4a_tag(tag_name, format_tag, value)
            elif self.format_type == 'flac':
                return self._write_flac_tag(tag_name, format_tag, value)
            elif self.format_type in ['wav', 'aiff']:
                return self._write_wav_aiff_tag(tag_name, format_tag, value)
        except Exception as e:
            # Log error but don't crash
            return False

        return False

    def _write_mp3_tag(self, tag_name: str, format_tag: str, value: Any) -> bool:
        """Write tag to MP3 file."""
        if tag_name == 'cover_art':
            # Handle APIC frames
            image_data, mime_type = prepare_image_data(value)
            if image_data:
                # Remove existing covers
                self.audio_file.tags.delall('APIC')
                # Add new cover
                self.audio_file.tags.add(
                    APIC(
                        encoding=3,  # UTF-8
                        mime=mime_type,
                        type=3,  # Cover (front)
                        desc='Cover',
                        data=image_data
                    )
                )
                return True
            return False
        elif tag_name == 'comment':
            # Handle COMM frames
            self.audio_file.tags.delall('COMM')
            self.audio_file.tags.add(
                COMM(
                    encoding=3,  # UTF-8
                    lang='eng',
                    desc='',
                    text=[str(value)]
                )
            )
            return True
        elif tag_name == 'initial_key':
            # Handle TKEY frame
            self.audio_file.tags.add(TKEY(encoding=3, text=[str(value)]))
            return True
        elif tag_name == 'label':
            # Handle TPUB frame
            self.audio_file.tags.add(TPUB(encoding=3, text=[str(value)]))
            return True
        elif tag_name == 'album':
            # Handle TALB frame
            self.audio_file.tags.add(TALB(encoding=3, text=[str(value)]))
            return True
        else:
            # Generic text frame handling
            frame_class = getattr(mutagen.id3, format_tag, None)
            if frame_class:
                self.audio_file.tags.add(frame_class(encoding=3, text=[str(value)]))
                return True
            return False

    def _write_m4a_tag(self, tag_name: str, format_tag: str, value: Any) -> bool:
        """Write tag to M4A file."""
        if tag_name == 'cover_art':
            # Handle cover art
            image_data, mime_type = prepare_image_data(value)
            if image_data:
                # Determine image format
                imageformat = MP4Cover.FORMAT_JPEG if 'jpeg' in mime_type or 'jpg' in mime_type else MP4Cover.FORMAT_PNG
                self.audio_file.tags['covr'] = [MP4Cover(image_data, imageformat=imageformat)]
                return True
            return False
        elif tag_name in ['initial_key', 'label']:
            # Handle freeform atoms
            # M4A freeform atoms need bytes
            self.audio_file.tags[format_tag] = [str(value).encode('utf-8')]
            return True
        else:
            # Handle standard atoms
            self.audio_file.tags[format_tag] = [str(value)]
            return True

    def _write_flac_tag(self, tag_name: str, format_tag: str, value: Any) -> bool:
        """Write tag to FLAC file."""
        if tag_name == 'cover_art':
            # Handle pictures
            image_data, mime_type = prepare_image_data(value)
            if image_data:
                # Clear existing pictures
                self.audio_file.clear_pictures()
                # Create new picture
                pic = Picture()
                pic.data = image_data
                pic.mime = mime_type
                pic.type = 3  # Cover (front)
                pic.desc = 'Cover'
                self.audio_file.add_picture(pic)
                return True
            return False
        else:
            # Handle vorbis comments
            self.audio_file[format_tag.lower()] = str(value)
            return True

    def _write_wav_aiff_tag(self, tag_name: str, format_tag: str, value: Any) -> bool:
        """Write tag to WAV/AIFF file (uses ID3v2)."""
        if not hasattr(self.audio_file, 'tags') or self.audio_file.tags is None:
            # Try to add tags
            try:
                self.audio_file.add_tags()
            except Exception:
                return False

        # WAV/AIFF can have ID3 tags
        return self._write_mp3_tag(tag_name, format_tag, value)

    def write_multiple_tags(self, tags: Dict[str, Any]) -> Dict[str, bool]:
        """
        Write multiple tags at once.

        Args:
            tags: Dictionary mapping tag names to values

        Returns:
            Dictionary mapping tag names to success status
        """
        results = {}
        for tag_name, value in tags.items():
            results[tag_name] = self.write_tag(tag_name, value)
        return results

    def save(self) -> bool:
        """
        Save changes to the file.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.audio_file.save()
            return True
        except Exception as e:
            return False

    def get_format(self) -> Optional[str]:
        """Get the detected format type."""
        return self.format_type
