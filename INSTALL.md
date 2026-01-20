# Installation Guide

## Windows Installation

### Method 1: Direct Installation from GitHub (Recommended)

Open PowerShell or Command Prompt and run:

```powershell
pip install git+https://github.com/LiTLiTschi/transfer-music-metadata.git@claude/audio-metadata-transfer-XaUzU
```

### Method 2: Clone and Install

```powershell
# Clone the repository
git clone https://github.com/LiTLiTschi/transfer-music-metadata.git
cd transfer-music-metadata

# Checkout the branch
git checkout claude/audio-metadata-transfer-XaUzU

# Install
pip install -e .
```

### Verify Installation

```powershell
# Check version
tmm --version

# Should output: tmm 1.0.0
```

### Troubleshooting on Windows

**If you get "tmm is not recognized":**
- Make sure Python Scripts directory is in your PATH
- Usually: `C:\Users\YourName\anaconda3\Scripts` or `C:\Python3X\Scripts`
- Or use: `python -m tmm` instead of `tmm`

**If you get module import errors:**
```powershell
# Reinstall with force
pip install --force-reinstall git+https://github.com/LiTLiTschi/transfer-music-metadata.git@claude/audio-metadata-transfer-XaUzU
```

## macOS / Linux Installation

### Direct Installation from GitHub

```bash
pip install git+https://github.com/LiTLiTschi/transfer-music-metadata.git@claude/audio-metadata-transfer-XaUzU
```

### Clone and Install

```bash
git clone https://github.com/LiTLiTschi/transfer-music-metadata.git
cd transfer-music-metadata
git checkout claude/audio-metadata-transfer-XaUzU
pip install -e .
```

## Using with Anaconda (Windows/Mac/Linux)

If you're using Anaconda (like the user in the error message):

```bash
# Activate your environment
conda activate base

# Install from GitHub
pip install git+https://github.com/LiTLiTschi/transfer-music-metadata.git@claude/audio-metadata-transfer-XaUzU

# Verify
tmm --version
```

## Quick Start After Installation

### 1. Generate a configuration file

```bash
tmm --generate-config my_config.yaml
```

### 2. Preview what will be transferred (dry run)

```bash
# Windows PowerShell (use forward slashes or escape backslashes)
tmm --source H:/music/source --target H:/music/target --dry-run

# Or use python -m tmm if tmm command not found
python -m tmm --source H:/music/source --target H:/music/target --dry-run
```

### 3. Run the actual transfer

```bash
tmm --source H:/music/source --target H:/music/target
```

## Common Usage Examples

### Transfer only Initial Key (Priority Tag)

```bash
tmm --source /path/to/source --target /path/to/target --tags initial_key
```

### Transfer all tags with verbose output

```bash
tmm --source /path/to/source --target /path/to/target --verbose
```

### Use metadata matching instead of filename

```bash
tmm --source /path/to/source --target /path/to/target --strategy metadata
```

### Use custom configuration

```bash
tmm --source /path/to/source --target /path/to/target --config my_config.yaml
```

## Upgrading

To get the latest version:

```bash
pip install --upgrade --force-reinstall git+https://github.com/LiTLiTschi/transfer-music-metadata.git@claude/audio-metadata-transfer-XaUzU
```

## Uninstalling

```bash
pip uninstall transfer-music-metadata
```

## Getting Help

```bash
# Show all available options
tmm --help

# Show version
tmm --version
```

## Support

For issues or questions:
- Check the [README.md](README.md) for full documentation
- Check the [QUICKSTART.md](QUICKSTART.md) for quick examples
- Report issues on GitHub: https://github.com/LiTLiTschi/transfer-music-metadata/issues
