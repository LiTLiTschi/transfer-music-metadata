"""
File matcher for finding matching audio files.

Matches source files to target files based on various strategies.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Callable
from .metadata.reader import MetadataReader


class FileMatcher:
    """Match source audio files to target audio files."""

    def __init__(self, matching_strategy: str = 'filename'):
        """
        Initialize the matcher.

        Args:
            matching_strategy: Strategy for matching files
                - 'filename': Match by filename (without extension)
                - 'metadata': Match by title and artist metadata
                - 'both': Try filename first, then metadata
        """
        self.matching_strategy = matching_strategy.lower()

        if self.matching_strategy not in ['filename', 'metadata', 'both']:
            raise ValueError(f"Invalid matching strategy: {matching_strategy}")

    def find_matches(self, source_file: Path, target_files: List[Path]) -> List[Path]:
        """
        Find all target files that match the source file.

        Args:
            source_file: Source audio file
            target_files: List of potential target files

        Returns:
            List of matching target files (can be empty or contain multiple matches)
        """
        if self.matching_strategy == 'filename':
            return self._match_by_filename(source_file, target_files)
        elif self.matching_strategy == 'metadata':
            return self._match_by_metadata(source_file, target_files)
        elif self.matching_strategy == 'both':
            # Try filename first
            matches = self._match_by_filename(source_file, target_files)
            if matches:
                return matches
            # Fall back to metadata
            return self._match_by_metadata(source_file, target_files)

        return []

    def _match_by_filename(self, source_file: Path, target_files: List[Path]) -> List[Path]:
        """
        Match files by filename (without extension).

        Args:
            source_file: Source audio file
            target_files: List of potential target files

        Returns:
            List of matching target files
        """
        source_stem = source_file.stem.lower()
        matches = []

        for target_file in target_files:
            target_stem = target_file.stem.lower()
            if source_stem == target_stem:
                matches.append(target_file)

        return matches

    def _match_by_metadata(self, source_file: Path, target_files: List[Path]) -> List[Path]:
        """
        Match files by metadata (title and artist).

        Args:
            source_file: Source audio file
            target_files: List of potential target files

        Returns:
            List of matching target files
        """
        matches = []

        try:
            # Read source metadata
            source_reader = MetadataReader(str(source_file))
            source_title = source_reader.read_tag('title')
            source_artist = source_reader.read_tag('artist')

            # Skip if source has no metadata
            if not source_title and not source_artist:
                return []

            # Normalize for comparison
            source_title = self._normalize_text(source_title) if source_title else None
            source_artist = self._normalize_text(source_artist) if source_artist else None

            for target_file in target_files:
                try:
                    target_reader = MetadataReader(str(target_file))
                    target_title = target_reader.read_tag('title')
                    target_artist = target_reader.read_tag('artist')

                    # Normalize for comparison
                    target_title = self._normalize_text(target_title) if target_title else None
                    target_artist = self._normalize_text(target_artist) if target_artist else None

                    # Check if both title and artist match (if available)
                    title_match = (source_title == target_title) if source_title and target_title else False
                    artist_match = (source_artist == target_artist) if source_artist and target_artist else False

                    # Consider it a match if both match, or if only one is available and it matches
                    if source_title and source_artist:
                        # Both available in source - need both to match
                        if title_match and artist_match:
                            matches.append(target_file)
                    elif source_title:
                        # Only title available in source
                        if title_match:
                            matches.append(target_file)
                    elif source_artist:
                        # Only artist available in source
                        if artist_match:
                            matches.append(target_file)

                except Exception:
                    # Skip files that can't be read
                    continue

        except Exception:
            # Source file can't be read
            return []

        return matches

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison.

        Args:
            text: Text to normalize

        Returns:
            Normalized text (lowercase, stripped)
        """
        if not text:
            return ''
        return text.lower().strip()

    def create_match_report(self, source_file: Path, matches: List[Path]) -> Dict[str, Any]:
        """
        Create a report of match results.

        Args:
            source_file: Source file
            matches: List of matched files

        Returns:
            Dictionary with match information
        """
        return {
            'source': source_file,
            'source_name': source_file.name,
            'match_count': len(matches),
            'matches': matches,
            'match_names': [m.name for m in matches],
            'strategy': self.matching_strategy,
        }
