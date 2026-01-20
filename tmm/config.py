"""
Configuration management for TMM.

Handles loading and validating configuration from files and command-line arguments.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml

from .metadata.mappings import DEFAULT_TAGS


class Config:
    """Configuration container for TMM."""

    # Default configuration values
    DEFAULTS = {
        'tags_to_transfer': DEFAULT_TAGS,
        'matching_strategy': 'filename',
        'overwrite_policy': {
            'initial_key': 'always',
            'label': 'if_empty',
            'comment': 'if_empty',
            'cover_art': 'if_empty',
            'album': 'if_empty',
        },
        'file_extensions': {
            'source': ['.mp3'],
            'target': ['.m4a', '.wav', '.mp3', '.flac'],
        },
        'logging': {
            'level': 'INFO',
            'file': 'tmm.log',
            'console': True,
        },
        'dry_run': False,
        'recursive': True,
    }

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration.

        Args:
            config_dict: Dictionary with configuration values
        """
        self.config = self.DEFAULTS.copy()

        if config_dict:
            self._merge_config(config_dict)

    def _merge_config(self, config_dict: Dict[str, Any]):
        """
        Merge user config with defaults.

        Args:
            config_dict: User configuration dictionary
        """
        for key, value in config_dict.items():
            if key in self.config and isinstance(self.config[key], dict) and isinstance(value, dict):
                # Merge nested dictionaries
                self.config[key].update(value)
            else:
                self.config[key] = value

    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """
        Load configuration from a YAML file.

        Args:
            config_path: Path to configuration file

        Returns:
            Config instance
        """
        config_file = Path(config_path)

        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_file, 'r') as f:
            config_dict = yaml.safe_load(f)

        return cls(config_dict)

    @classmethod
    def from_args(cls, args: Dict[str, Any]) -> 'Config':
        """
        Create configuration from command-line arguments.

        Args:
            args: Dictionary of command-line arguments

        Returns:
            Config instance
        """
        config_dict = {}

        # Map CLI args to config structure
        if 'tags' in args and args['tags']:
            config_dict['tags_to_transfer'] = args['tags']

        if 'strategy' in args and args['strategy']:
            config_dict['matching_strategy'] = args['strategy']

        if 'dry_run' in args:
            config_dict['dry_run'] = args['dry_run']

        if 'verbose' in args and args['verbose']:
            config_dict['logging'] = {'level': 'DEBUG'}

        if 'no_recursive' in args and args['no_recursive']:
            config_dict['recursive'] = False

        return cls(config_dict)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self.config.get(key, default)

    def get_tags_to_transfer(self) -> List[str]:
        """Get list of tags to transfer."""
        return self.config['tags_to_transfer']

    def get_matching_strategy(self) -> str:
        """Get file matching strategy."""
        return self.config['matching_strategy']

    def get_overwrite_policy(self, tag: str) -> str:
        """
        Get overwrite policy for a specific tag.

        Args:
            tag: Tag name

        Returns:
            Overwrite policy ('always', 'never', 'if_empty')
        """
        return self.config['overwrite_policy'].get(tag, 'if_empty')

    def get_source_extensions(self) -> List[str]:
        """Get list of source file extensions."""
        return self.config['file_extensions']['source']

    def get_target_extensions(self) -> List[str]:
        """Get list of target file extensions."""
        return self.config['file_extensions']['target']

    def is_dry_run(self) -> bool:
        """Check if in dry-run mode."""
        return self.config['dry_run']

    def is_recursive(self) -> bool:
        """Check if recursive scanning is enabled."""
        return self.config['recursive']

    def get_log_level(self) -> str:
        """Get logging level."""
        return self.config['logging']['level']

    def get_log_file(self) -> str:
        """Get log file path."""
        return self.config['logging']['file']

    def should_log_to_console(self) -> bool:
        """Check if console logging is enabled."""
        return self.config['logging']['console']

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Configuration dictionary
        """
        return self.config.copy()

    def save_to_file(self, file_path: str):
        """
        Save configuration to a YAML file.

        Args:
            file_path: Path to save configuration
        """
        with open(file_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
