"""
Command-line interface for TMM.

Handles argument parsing and user interaction.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .config import Config
from .processor import MetadataProcessor
from .utils import (
    setup_logging, get_logger, validate_directory,
    print_header, print_success, print_error, print_info
)
from . import __version__


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser.

    Returns:
        ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='tmm',
        description='Transfer Music Metadata - Transfer metadata tags between audio files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage - transfer from MP3s to M4As
  tmm --source /music/mp3 --target /music/m4a

  # Use custom config file
  tmm --source /music/mp3 --target /music/m4a --config config.yaml

  # Transfer specific tags only
  tmm --source /music/mp3 --target /music/m4a --tags initial_key,album

  # Dry run to preview changes
  tmm --source /music/mp3 --target /music/m4a --dry-run

  # Use metadata matching instead of filename
  tmm --source /music/mp3 --target /music/m4a --strategy metadata

  # Verbose output with debug logging
  tmm --source /music/mp3 --target /music/m4a --verbose

Supported formats: MP3, M4A, FLAC, WAV, AIFF
Supported tags: initial_key, label, comment, cover_art, album
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    # Required arguments
    parser.add_argument(
        '-s', '--source',
        required=True,
        help='Source directory containing audio files to read metadata from'
    )

    parser.add_argument(
        '-t', '--target',
        required=True,
        help='Target directory containing audio files to write metadata to'
    )

    # Optional arguments
    parser.add_argument(
        '-c', '--config',
        help='Path to configuration file (YAML)'
    )

    parser.add_argument(
        '--tags',
        help='Comma-separated list of tags to transfer (e.g., "initial_key,album,label")'
    )

    parser.add_argument(
        '--strategy',
        choices=['filename', 'metadata', 'both'],
        help='File matching strategy (default: filename)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )

    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not scan subdirectories'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output (debug level logging)'
    )

    parser.add_argument(
        '--log-file',
        help='Path to log file (default: tmm.log)'
    )

    parser.add_argument(
        '--no-console-log',
        action='store_true',
        help='Disable console logging (only log to file)'
    )

    parser.add_argument(
        '--generate-config',
        metavar='FILE',
        help='Generate a default configuration file and exit'
    )

    return parser


def parse_tags(tags_string: str) -> List[str]:
    """
    Parse comma-separated tags string.

    Args:
        tags_string: Comma-separated tags

    Returns:
        List of tag names
    """
    return [tag.strip() for tag in tags_string.split(',') if tag.strip()]


def run_cli(args: Optional[List[str]] = None) -> int:
    """
    Run the CLI application.

    Args:
        args: Command-line arguments (for testing)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Handle config generation
    if parsed_args.generate_config:
        try:
            config = Config()
            config.save_to_file(parsed_args.generate_config)
            print_success(f"Generated default configuration file: {parsed_args.generate_config}")
            return 0
        except Exception as e:
            print_error(f"Failed to generate configuration file: {e}")
            return 1

    # Validate required arguments
    try:
        source_dir = validate_directory(parsed_args.source, "Source directory")
        target_dir = validate_directory(parsed_args.target, "Target directory")
    except ValueError as e:
        print_error(str(e))
        return 1

    # Load configuration
    try:
        if parsed_args.config:
            config = Config.from_file(parsed_args.config)
            print_info(f"Loaded configuration from: {parsed_args.config}")
        else:
            config = Config()

        # Override with CLI arguments
        cli_config = {}

        if parsed_args.tags:
            cli_config['tags_to_transfer'] = parse_tags(parsed_args.tags)

        if parsed_args.strategy:
            cli_config['matching_strategy'] = parsed_args.strategy

        if parsed_args.dry_run:
            cli_config['dry_run'] = True

        if parsed_args.no_recursive:
            cli_config['recursive'] = False

        if parsed_args.verbose:
            cli_config['logging'] = {'level': 'DEBUG'}

        if parsed_args.log_file:
            if 'logging' not in cli_config:
                cli_config['logging'] = {}
            cli_config['logging']['file'] = parsed_args.log_file

        if parsed_args.no_console_log:
            if 'logging' not in cli_config:
                cli_config['logging'] = {}
            cli_config['logging']['console'] = False

        # Merge CLI config
        if cli_config:
            config._merge_config(cli_config)

    except Exception as e:
        print_error(f"Configuration error: {e}")
        return 1

    # Set up logging
    try:
        log_level = config.get_log_level()
        log_file = config.get_log_file()
        console = config.should_log_to_console()

        setup_logging(log_level, log_file, console)
        logger = get_logger()

    except Exception as e:
        print_error(f"Failed to set up logging: {e}")
        return 1

    # Print header
    print_header(f"Transfer Music Metadata v{__version__}")

    # Print configuration info
    if config.is_dry_run():
        print_info("DRY RUN MODE - No files will be modified")

    print_info(f"Source: {source_dir}")
    print_info(f"Target: {target_dir}")
    print_info(f"Tags: {', '.join(config.get_tags_to_transfer())}")
    print_info(f"Strategy: {config.get_matching_strategy()}")

    # Run processor
    try:
        processor = MetadataProcessor(config)
        stats = processor.process(str(source_dir), str(target_dir))

        # Print result
        if stats['transfers_successful'] > 0:
            print_success(f"Successfully transferred metadata to {stats['transfers_successful']} file(s)")
        elif stats['matches_found'] == 0:
            print_error("No matching files found")
            return 1
        else:
            print_error("No metadata was transferred")
            return 1

        if stats['transfers_failed'] > 0:
            print_error(f"Failed to transfer to {stats['transfers_failed']} file(s)")
            return 1

        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        logger.exception("Unexpected error occurred")
        print_error(f"Error: {e}")
        return 1


def main():
    """Main entry point."""
    sys.exit(run_cli())
