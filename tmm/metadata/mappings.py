"""
Tag name mappings for different audio formats.

This module defines how metadata tags are named in different audio file formats.
"""

# Tag mappings for each format
# Format: {unified_tag_name: format_specific_tag_name}
TAG_MAPPINGS = {
    'mp3': {
        'initial_key': 'TKEY',
        'label': 'TPUB',  # Publisher field, commonly used for labels
        'comment': 'COMM::eng',  # COMM frame with language code
        'cover_art': 'APIC:',  # Album Picture
        'album': 'TALB',
        'title': 'TIT2',
        'artist': 'TPE1',
    },
    'm4a': {
        'initial_key': '----:com.apple.iTunes:initialkey',  # Freeform atom
        'label': '----:com.apple.iTunes:LABEL',  # Freeform atom
        'comment': '©cmt',  # Comment atom
        'cover_art': 'covr',  # Cover art atom
        'album': '©alb',  # Album atom
        'title': '©nam',  # Title atom
        'artist': '©ART',  # Artist atom
    },
    'flac': {
        'initial_key': 'INITIALKEY',
        'label': 'LABEL',
        'comment': 'COMMENT',
        'cover_art': 'METADATA_BLOCK_PICTURE',  # Base64 encoded picture
        'album': 'ALBUM',
        'title': 'TITLE',
        'artist': 'ARTIST',
    },
    'wav': {
        # WAV files can use ID3v2 tags (same as MP3)
        'initial_key': 'TKEY',
        'label': 'TPUB',
        'comment': 'COMM::eng',
        'cover_art': 'APIC:',
        'album': 'TALB',
        'title': 'TIT2',
        'artist': 'TPE1',
    },
    'aiff': {
        # AIFF can also use ID3v2 tags
        'initial_key': 'TKEY',
        'label': 'TPUB',
        'comment': 'COMM::eng',
        'cover_art': 'APIC:',
        'album': 'TALB',
        'title': 'TIT2',
        'artist': 'TPE1',
    },
}

# Supported audio file extensions
SUPPORTED_EXTENSIONS = {
    '.mp3': 'mp3',
    '.m4a': 'm4a',
    '.m4b': 'm4a',  # Audiobook format, same as m4a
    '.m4p': 'm4a',  # Protected AAC
    '.flac': 'flac',
    '.wav': 'wav',
    '.wave': 'wav',
    '.aiff': 'aiff',
    '.aif': 'aiff',
}

# Tags that should be transferred (configurable)
DEFAULT_TAGS = [
    'initial_key',  # PRIORITY
    'label',
    'comment',
    'cover_art',
    'album',
]

# Tags used for matching files
MATCHING_TAGS = [
    'title',
    'artist',
    'album',
]
