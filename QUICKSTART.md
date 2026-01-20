# Quick Start Guide

Get started with Transfer Music Metadata (TMM) in 5 minutes!

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install TMM
pip install -e .
```

## Basic Usage

### 1. Check what will be transferred (Dry Run)

```bash
tmm --source /path/to/source --target /path/to/target --dry-run
```

This shows you what would be transferred without making any changes.

### 2. Transfer metadata

```bash
tmm --source /path/to/source --target /path/to/target
```

That's it! TMM will:
- Find all MP3 files in source directory
- Find all M4A, FLAC, WAV files in target directory
- Match files by filename
- Transfer Initial Key, Label, Comment, Cover Art, and Album tags

## Common Scenarios

### Scenario 1: Transfer DJ key data from Rekordbox to iTunes library

```bash
# Transfer only the musical key
tmm --source ~/Music/Rekordbox --target ~/Music/iTunes --tags initial_key
```

### Scenario 2: Transfer all metadata to M4A files

```bash
# First, preview what will happen
tmm --source ~/Music/MP3 --target ~/Music/M4A --dry-run

# If it looks good, do the transfer
tmm --source ~/Music/MP3 --target ~/Music/M4A
```

### Scenario 3: Match files by metadata instead of filename

Useful if files have different names but same title/artist tags:

```bash
tmm --source ~/Music/Source --target ~/Music/Target --strategy metadata
```

## Understanding the Output

```
✓ Successfully transferred metadata to 42 file(s)

SUMMARY
============================================================
Source files scanned: 100
Target files scanned: 150
Matches found: 42
Transfer attempts: 42
Successful transfers: 42
Failed transfers: 0

Tags transferred:
  initial_key: 42
  label: 38
  comment: 15
  cover_art: 40
  album: 42
============================================================
```

- **Matches found**: Number of target files that matched source files
- **Successful transfers**: Files successfully updated
- **Tags transferred**: How many times each tag was written

## Customization

### Create a config file

```bash
# Generate default config
tmm --generate-config my_config.yaml

# Edit my_config.yaml to your preferences
# Then use it:
tmm --source ~/Music/Source --target ~/Music/Target --config my_config.yaml
```

### Common config tweaks

**Always overwrite all tags:**
```yaml
overwrite_policy:
  initial_key: always
  label: always
  comment: always
  cover_art: always
  album: always
```

**Transfer more tag types:**
```yaml
tags_to_transfer:
  - initial_key
  - label
  - comment
  - cover_art
  - album
  - title
  - artist
```

**Match by metadata:**
```yaml
matching_strategy: metadata
```

## Tips

1. **Always try --dry-run first** to preview changes
2. **Use --verbose** for detailed logs when troubleshooting
3. **Check tmm.log** for detailed information about what happened
4. **Backup your files** before running metadata operations (though TMM only modifies tags, not audio data)

## Troubleshooting

**"No matches found"**
- Try using `--strategy metadata` instead of filename matching
- Check that source and target files have similar names or metadata

**"WAV files not getting metadata"**
- WAV has limited metadata support in many applications
- Consider using FLAC instead for lossless with full metadata support

**"Permission denied errors"**
- Make sure you have write permissions to target directory
- On macOS, you may need to grant terminal permission to access Music folder

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the [default_config.yaml](config/default_config.yaml) for all options
- Check out the tag mappings for different formats in the README

## Getting Help

- Check the verbose logs: `tmm --source ... --target ... --verbose`
- Look at the log file: `cat tmm.log`
- Open an issue on GitHub with your log file

Happy metadata transferring! 🎵
