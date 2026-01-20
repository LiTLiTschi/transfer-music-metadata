# Transfer Music Metadata (TMM)

A powerful Python-based command-line tool for transferring metadata tags between audio files. Supports MP3, M4A, FLAC, WAV, and AIFF formats with a focus on **Initial Key** and **M4A** format as priorities.

## Features

- **Multi-Format Support**: Transfer metadata between MP3, M4A, FLAC, WAV, and AIFF files
- **Priority Tags**: Special focus on Initial Key, Label, Comment, Cover Art, and Album
- **Flexible Matching**: Match files by filename or metadata (title/artist)
- **Multiple Matches**: Process all matching target files (no early exit)
- **Configurable Overwrite**: Per-tag policies (always, never, if_empty)
- **Dry Run Mode**: Preview changes before applying them
- **Recursive Scanning**: Automatically scans subdirectories
- **Progress Tracking**: Real-time progress bars and detailed logging
- **Error Resilient**: Continues processing even if individual files fail

## Supported Tags

- **Initial Key** (PRIORITY) - Musical key of the track
- **Label** - Record label
- **Comment** - Comments and notes
- **Cover Art** (Image) - Album artwork
- **Album** - Album name
- Title, Artist (used for matching)

## Supported Formats

| Format | Read | Write | Notes |
|--------|------|-------|-------|
| MP3    | ✓    | ✓     | ID3v2 tags |
| M4A    | ✓    | ✓     | **PRIORITY FORMAT** - MP4 atoms |
| FLAC   | ✓    | ✓     | Vorbis comments |
| WAV    | ✓    | ✓     | ID3v2 tags (limited support) |
| AIFF   | ✓    | ✓     | ID3v2 tags |

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/LiTLiTschi/transfer-music-metadata.git
cd transfer-music-metadata

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Dependencies

- Python 3.8+
- mutagen >= 1.47.0
- pyyaml >= 6.0
- colorama >= 0.4.6
- tqdm >= 4.66.0

## Usage

### Basic Usage

Transfer metadata from MP3 files to M4A files:

```bash
tmm --source /path/to/mp3s --target /path/to/m4as
```

### Common Examples

**Preview changes (dry run):**
```bash
tmm --source /music/mp3 --target /music/m4a --dry-run
```

**Transfer specific tags only:**
```bash
tmm --source /music/mp3 --target /music/m4a --tags initial_key,album
```

**Use metadata matching instead of filename:**
```bash
tmm --source /music/mp3 --target /music/m4a --strategy metadata
```

**Use custom configuration file:**
```bash
tmm --source /music/mp3 --target /music/m4a --config my_config.yaml
```

**Verbose output with debug logging:**
```bash
tmm --source /music/mp3 --target /music/m4a --verbose
```

**Don't scan subdirectories:**
```bash
tmm --source /music/mp3 --target /music/m4a --no-recursive
```

### Command-Line Options

```
Required Arguments:
  -s, --source SOURCE      Source directory with files to read metadata from
  -t, --target TARGET      Target directory with files to write metadata to

Optional Arguments:
  -c, --config FILE        Path to configuration file (YAML)
  --tags TAGS              Comma-separated list of tags to transfer
  --strategy STRATEGY      Matching strategy: filename, metadata, or both
  --dry-run                Preview changes without modifying files
  --no-recursive           Don't scan subdirectories
  -v, --verbose            Enable verbose output (debug logging)
  --log-file FILE          Path to log file (default: tmm.log)
  --no-console-log         Disable console logging
  --generate-config FILE   Generate default config file and exit
  --version                Show version and exit
```

## Configuration

### Generate Default Configuration

```bash
tmm --generate-config config.yaml
```

### Configuration File Format

```yaml
# Tags to transfer
tags_to_transfer:
  - initial_key  # PRIORITY
  - label
  - comment
  - cover_art
  - album

# Matching strategy: filename, metadata, or both
matching_strategy: filename

# Overwrite policy per tag: always, never, if_empty
overwrite_policy:
  initial_key: always    # PRIORITY - always overwrite
  label: if_empty
  comment: if_empty
  cover_art: if_empty
  album: if_empty

# File extensions
file_extensions:
  source: [".mp3"]
  target: [".m4a", ".wav", ".mp3", ".flac"]

# Logging
logging:
  level: INFO
  file: tmm.log
  console: true

# General options
dry_run: false
recursive: true
```

## How It Works

1. **Scan Directories**: Recursively scans source and target directories for audio files
2. **Match Files**: For each source file, finds matching target file(s) based on strategy:
   - **Filename**: Matches files with the same name (ignoring extension)
   - **Metadata**: Matches files with the same title and artist tags
   - **Both**: Tries filename first, then falls back to metadata
3. **Read Metadata**: Reads specified tags from source file
4. **Apply Policy**: Checks overwrite policy for each tag:
   - **always**: Overwrites existing tag
   - **never**: Skips if tag exists
   - **if_empty**: Only writes if target tag is empty
5. **Write Metadata**: Writes tags to target file(s)
6. **Report**: Generates summary of operations

**Important**: The tool processes **ALL** matching target files for each source file (doesn't skip after first match).

## Tag Mappings

### MP3 (ID3v2)
- Initial Key: `TKEY`
- Label: `TPUB`
- Comment: `COMM`
- Cover Art: `APIC`
- Album: `TALB`

### M4A (MP4 Atoms)
- Initial Key: `----:com.apple.iTunes:initialkey` (freeform)
- Label: `----:com.apple.iTunes:LABEL` (freeform)
- Comment: `©cmt`
- Cover Art: `covr`
- Album: `©alb`

### FLAC (Vorbis Comments)
- Initial Key: `INITIALKEY`
- Label: `LABEL`
- Comment: `COMMENT`
- Cover Art: `METADATA_BLOCK_PICTURE`
- Album: `ALBUM`

### WAV/AIFF (ID3v2)
- Same as MP3 (when ID3v2 tags are supported)
- Note: WAV has limited metadata support

## Examples

### Transfer from DJ software exports

If you have tracks tagged in Rekordbox/Traktor (MP3) and want to transfer the key information to your M4A library:

```bash
tmm --source ~/DJ/Rekordbox --target ~/Music/Library --tags initial_key
```

### Sync entire metadata set

Transfer all supported tags to M4A files:

```bash
tmm --source ~/Music/Source --target ~/Music/M4A --tags initial_key,label,comment,cover_art,album
```

### Preview changes first

Always recommended to check what will be modified:

```bash
tmm --source ~/Music/Source --target ~/Music/M4A --dry-run --verbose
```

## Error Handling

- **Corrupted Files**: Skipped with error logged
- **Missing Metadata**: Only available tags are transferred
- **Permission Errors**: Logged and processing continues
- **Format Incompatibilities**: Handled gracefully (e.g., WAV with no ID3 support)
- **Multiple Matches**: All matches are processed independently

## Logging

Logs are written to `tmm.log` by default and include:
- Files processed
- Matches found
- Tags transferred
- Errors encountered
- Summary statistics

Use `--verbose` for detailed debug information.

## Limitations

- **WAV Files**: Limited metadata support (not all applications write ID3v2 tags to WAV)
- **Image Formats**: Cover art is transferred as-is (JPEG/PNG supported)
- **Tag Compatibility**: Some specialized tags may not be supported by all formats

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built with [Mutagen](https://github.com/quodlibet/mutagen) - Python audio metadata library
- Uses [tqdm](https://github.com/tqdm/tqdm) for progress bars
- Color output via [colorama](https://github.com/tartley/colorama)

## Support

For issues, questions, or feature requests, please open an issue on GitHub:
https://github.com/LiTLiTschi/transfer-music-metadata/issues

---

**Version**: 1.0.0
**Author**: Transfer Music Metadata
**Repository**: https://github.com/LiTLiTschi/transfer-music-metadata
