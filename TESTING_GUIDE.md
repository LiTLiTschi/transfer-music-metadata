# Testing Guide - Debug Initial Key Transfer

Follow these steps to help debug the initial key transfer issue.

## Step 1: Download the Repository

Open PowerShell and run:

```powershell
# Navigate to a working directory
cd H:\

# Clone the repository
git clone https://github.com/LiTLiTschi/transfer-music-metadata.git
cd transfer-music-metadata

# Checkout the correct branch
git checkout claude/audio-metadata-transfer-XaUzU

# Verify you're on the right branch
git branch
```

You should see `* claude/audio-metadata-transfer-XaUzU`

## Step 2: Create Test Directory Structure

```powershell
# Create test directories
mkdir test_files
mkdir test_files\source
mkdir test_files\target
```

## Step 3: Add Your Test Files

**IMPORTANT:** Copy files that you KNOW have the initial key tag in the source file.

### 3.1: Copy Source File (MP3 with Initial Key)

```powershell
# Copy ONE MP3 file that has an Initial Key tag to the source folder
# Example (adjust the path to your actual file):
copy "H:\music\your_dj_tracks\song_with_key.mp3" test_files\source\test_source.mp3
```

### 3.2: Copy Target File (M4A to receive the tag)

```powershell
# Copy ONE M4A file to the target folder
# Example (adjust the path to your actual file):
copy "H:\music\your_m4a_library\song.m4a" test_files\target\test_source.m4a
```

**IMPORTANT:** Name the target file the SAME as the source (except extension) so they match!
- Source: `test_source.mp3`
- Target: `test_source.m4a`

## Step 4: Verify the Source File Has Initial Key

Let's check that your source MP3 actually has the initial key tag:

```powershell
python -c "from mutagen.mp3 import MP3; audio = MP3('test_files/source/test_source.mp3'); print('Tags:', list(audio.tags.keys()) if audio.tags else 'No tags'); print('Has TKEY:', 'TKEY' in audio.tags if audio.tags else False); print('TKEY value:', audio.tags['TKEY'].text if audio.tags and 'TKEY' in audio.tags else 'Not found')"
```

This should show:
- `Has TKEY: True`
- `TKEY value: ['08A']` (or whatever your key is)

**If it shows `Has TKEY: False`**, your source file doesn't have the initial key tag! You need to find a file that does.

## Step 5: Add Test Files to Git

```powershell
# Stage the test files
git add test_files/

# Commit them
git commit -m "Add test files for debugging initial key transfer"

# Push to the branch
git push origin claude/audio-metadata-transfer-XaUzU
```

## Step 6: Run TMM with Verbose Logging

Now run the transfer with verbose output:

```powershell
python -m tmm --source test_files/source --target test_files/target --verbose --tags initial_key
```

## Step 7: Capture the Output

**COPY THE ENTIRE OUTPUT** from Step 6 and send it to me.

Also, verify if the tag was written:

```powershell
python -c "from mutagen.mp4 import MP4; audio = MP4('test_files/target/test_source.m4a'); print('All tags:', dict(audio.tags) if audio.tags else 'No tags'); print('Has initialkey:', '----:com.apple.iTunes:initialkey' in audio.tags if audio.tags else False)"
```

## Step 8: Share Results

Send me:

1. ✅ The output from Step 4 (source verification)
2. ✅ The complete output from Step 6 (TMM run)
3. ✅ The output from Step 7 (target verification)
4. ✅ Confirm that you pushed the test files to git

Once I have this information and the test files in the repo, I can:
- See exactly what's in your source file
- See exactly what's in your target file
- Debug the exact transfer process
- Fix any remaining issues

---

## Alternative: If Git Push Fails

If you can't push the files (they might be too large), instead run this diagnostic script:

```powershell
# Save this as diagnose.py in the transfer-music-metadata folder
python diagnose.py
```

(I'll create the diagnose.py script next if needed)

---

## What to Check

Before we start, verify:
- [ ] Source MP3 actually has TKEY tag (use Mp3tag or similar to check)
- [ ] You're using files with the SAME name (except extension)
- [ ] You installed the latest version from git
