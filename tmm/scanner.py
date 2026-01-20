"""
File scanner for audio files.

Recursively scans directories for audio files.
"""

import os
from pathlib import Path
from typing import List, Set
from .metadata.mappings import SUPPORTED_EXTENSIONS


class AudioFileScanner:
    """Scanner for finding audio files in directories."""

    def __init__(self, extensions: Set[str] = None):
        """
        Initialize the scanner.

        Args:
            extensions: Set of file extensions to scan for (e.g., {'.mp3', '.m4a'})
                       If None, uses all supported extensions
        """
        if extensions is None:
            self.extensions = set(SUPPORTED_EXTENSIONS.keys())
        else:
            self.extensions = {ext.lower() if ext.startswith('.') else f'.{ext.lower()}'
                             for ext in extensions}

    def scan_directory(self, directory: str, recursive: bool = True) -> List[Path]:
        """
        Scan a directory for audio files.

        Args:
            directory: Path to directory to scan
            recursive: Whether to scan subdirectories

        Returns:
            List of Path objects for found audio files
        """
        directory_path = Path(directory)

        if not directory_path.exists():
            raise ValueError(f"Directory does not exist: {directory}")

        if not directory_path.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")

        audio_files = []

        if recursive:
            # Use rglob for recursive search
            for ext in self.extensions:
                audio_files.extend(directory_path.rglob(f'*{ext}'))
        else:
            # Use glob for non-recursive search
            for ext in self.extensions:
                audio_files.extend(directory_path.glob(f'*{ext}'))

        # Sort by path for consistent ordering
        return sorted(audio_files)

    def scan_multiple_directories(self, directories: List[str], recursive: bool = True) -> List[Path]:
        """
        Scan multiple directories for audio files.

        Args:
            directories: List of directory paths
            recursive: Whether to scan subdirectories

        Returns:
            List of Path objects for found audio files (deduplicated)
        """
        all_files = []
        seen_paths = set()

        for directory in directories:
            files = self.scan_directory(directory, recursive)
            for file_path in files:
                # Resolve to absolute path to avoid duplicates
                abs_path = file_path.resolve()
                if abs_path not in seen_paths:
                    seen_paths.add(abs_path)
                    all_files.append(file_path)

        return sorted(all_files)

    def get_file_info(self, file_path: Path) -> dict:
        """
        Get basic information about an audio file.

        Args:
            file_path: Path to the audio file

        Returns:
            Dictionary with file information
        """
        stat = file_path.stat()
        return {
            'path': file_path,
            'name': file_path.name,
            'stem': file_path.stem,
            'extension': file_path.suffix.lower(),
            'size': stat.st_size,
            'modified': stat.st_mtime,
        }
