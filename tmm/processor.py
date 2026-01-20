"""
Main processor for transferring metadata between audio files.

Orchestrates the entire metadata transfer workflow.
"""

from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm

from .scanner import AudioFileScanner
from .matcher import FileMatcher
from .metadata.reader import MetadataReader
from .metadata.writer import MetadataWriter
from .config import Config
from .utils import get_logger, format_path


class MetadataProcessor:
    """Process metadata transfers between audio files."""

    def __init__(self, config: Config):
        """
        Initialize the processor.

        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = get_logger()

        # Statistics
        self.stats = {
            'source_files': 0,
            'target_files': 0,
            'matches_found': 0,
            'transfers_attempted': 0,
            'transfers_successful': 0,
            'transfers_failed': 0,
            'tags_transferred': {},
            'errors': [],
        }

    def process(self, source_dir: str, target_dir: str) -> Dict[str, Any]:
        """
        Process metadata transfer from source to target directory.

        Args:
            source_dir: Source directory path
            target_dir: Target directory path

        Returns:
            Dictionary with processing statistics
        """
        self.logger.info(f"Starting metadata transfer")
        self.logger.info(f"Source directory: {source_dir}")
        self.logger.info(f"Target directory: {target_dir}")
        self.logger.info(f"Dry run mode: {self.config.is_dry_run()}")

        # Step 1: Scan directories
        self.logger.info("Scanning directories...")
        source_files = self._scan_source_directory(source_dir)
        target_files = self._scan_target_directory(target_dir)

        self.stats['source_files'] = len(source_files)
        self.stats['target_files'] = len(target_files)

        self.logger.info(f"Found {len(source_files)} source files")
        self.logger.info(f"Found {len(target_files)} target files")

        if not source_files:
            self.logger.warning("No source files found!")
            return self.stats

        if not target_files:
            self.logger.warning("No target files found!")
            return self.stats

        # Step 2: Process each source file
        matcher = FileMatcher(self.config.get_matching_strategy())
        tags_to_transfer = self.config.get_tags_to_transfer()

        self.logger.info(f"Tags to transfer: {', '.join(tags_to_transfer)}")
        self.logger.info(f"Matching strategy: {self.config.get_matching_strategy()}")

        # Initialize tag statistics
        for tag in tags_to_transfer:
            self.stats['tags_transferred'][tag] = 0

        # Process with progress bar
        with tqdm(source_files, desc="Processing files", unit="file") as pbar:
            for source_file in pbar:
                pbar.set_description(f"Processing {source_file.name}")
                self._process_source_file(source_file, target_files, matcher, tags_to_transfer)

        # Print summary
        self._print_summary()

        return self.stats

    def _scan_source_directory(self, directory: str) -> List[Path]:
        """Scan source directory for audio files."""
        extensions = self.config.get_source_extensions()
        scanner = AudioFileScanner(extensions=set(extensions))
        return scanner.scan_directory(directory, recursive=self.config.is_recursive())

    def _scan_target_directory(self, directory: str) -> List[Path]:
        """Scan target directory for audio files."""
        extensions = self.config.get_target_extensions()
        scanner = AudioFileScanner(extensions=set(extensions))
        return scanner.scan_directory(directory, recursive=self.config.is_recursive())

    def _process_source_file(self, source_file: Path, target_files: List[Path],
                            matcher: FileMatcher, tags_to_transfer: List[str]):
        """
        Process a single source file.

        Args:
            source_file: Source file path
            target_files: List of all target files
            matcher: File matcher instance
            tags_to_transfer: List of tags to transfer
        """
        try:
            # Find matching target files
            matches = matcher.find_matches(source_file, target_files)

            if not matches:
                self.logger.debug(f"No matches found for: {source_file.name}")
                return

            self.stats['matches_found'] += len(matches)
            self.logger.info(f"Found {len(matches)} match(es) for: {source_file.name}")

            # Read metadata from source file
            source_metadata = self._read_source_metadata(source_file, tags_to_transfer)

            if not source_metadata:
                self.logger.warning(f"No metadata to transfer from: {source_file.name}")
                return

            # Transfer to each matching target file
            for target_file in matches:
                self._transfer_metadata(source_file, target_file, source_metadata, tags_to_transfer)

        except Exception as e:
            error_msg = f"Error processing {source_file.name}: {e}"
            self.logger.error(error_msg)
            self.stats['errors'].append(error_msg)

    def _read_source_metadata(self, source_file: Path, tags: List[str]) -> Dict[str, Any]:
        """
        Read metadata from source file.

        Args:
            source_file: Source file path
            tags: Tags to read

        Returns:
            Dictionary of metadata values
        """
        try:
            reader = MetadataReader(str(source_file))
            return reader.read_all_tags(tags)
        except Exception as e:
            self.logger.error(f"Failed to read metadata from {source_file.name}: {e}")
            return {}

    def _transfer_metadata(self, source_file: Path, target_file: Path,
                          source_metadata: Dict[str, Any], tags_to_transfer: List[str]):
        """
        Transfer metadata from source to target file.

        Args:
            source_file: Source file path
            target_file: Target file path
            source_metadata: Metadata from source file
            tags_to_transfer: Tags to transfer
        """
        self.stats['transfers_attempted'] += 1

        try:
            self.logger.info(f"  → {source_file.name} → {target_file.name}")

            # Read existing target metadata
            target_reader = MetadataReader(str(target_file))

            # Determine which tags to write based on overwrite policy
            tags_to_write = {}
            for tag in tags_to_transfer:
                if tag not in source_metadata:
                    continue

                policy = self.config.get_overwrite_policy(tag)
                source_value = source_metadata[tag]

                if policy == 'always':
                    tags_to_write[tag] = source_value
                elif policy == 'never':
                    continue
                elif policy == 'if_empty':
                    target_value = target_reader.read_tag(tag)
                    if not target_value:
                        tags_to_write[tag] = source_value

            if not tags_to_write:
                self.logger.debug(f"    No tags to write based on overwrite policy")
                return

            # Log tags being transferred
            for tag in tags_to_write:
                self.logger.debug(f"    Writing {tag}")

            # Write metadata (unless dry run)
            if self.config.is_dry_run():
                self.logger.info(f"    [DRY RUN] Would write: {', '.join(tags_to_write.keys())}")
                self.stats['transfers_successful'] += 1
                for tag in tags_to_write:
                    self.stats['tags_transferred'][tag] += 1
            else:
                writer = MetadataWriter(str(target_file))
                results = writer.write_multiple_tags(tags_to_write)

                # Save changes
                if writer.save():
                    self.stats['transfers_successful'] += 1
                    # Count successful tag writes
                    for tag, success in results.items():
                        if success:
                            self.stats['tags_transferred'][tag] += 1
                    self.logger.info(f"    Successfully wrote {sum(results.values())} tags")
                else:
                    self.stats['transfers_failed'] += 1
                    self.logger.error(f"    Failed to save changes to {target_file.name}")

        except Exception as e:
            self.stats['transfers_failed'] += 1
            error_msg = f"Failed to transfer metadata to {target_file.name}: {e}"
            self.logger.error(f"    {error_msg}")
            self.stats['errors'].append(error_msg)

    def _print_summary(self):
        """Print processing summary."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Source files scanned: {self.stats['source_files']}")
        self.logger.info(f"Target files scanned: {self.stats['target_files']}")
        self.logger.info(f"Matches found: {self.stats['matches_found']}")
        self.logger.info(f"Transfer attempts: {self.stats['transfers_attempted']}")
        self.logger.info(f"Successful transfers: {self.stats['transfers_successful']}")
        self.logger.info(f"Failed transfers: {self.stats['transfers_failed']}")

        if self.stats['tags_transferred']:
            self.logger.info("\nTags transferred:")
            for tag, count in self.stats['tags_transferred'].items():
                self.logger.info(f"  {tag}: {count}")

        if self.stats['errors']:
            self.logger.warning(f"\nErrors encountered: {len(self.stats['errors'])}")
            self.logger.warning("Check log file for details")

        self.logger.info("=" * 60)
