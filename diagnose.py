#!/usr/bin/env python3
"""
Diagnostic script to debug initial key transfer issues.

This script will:
1. Check the source file for initial key tag
2. Check the target file before transfer
3. Attempt to write the tag
4. Check the target file after transfer
5. Report detailed information about each step
"""

import sys
import os
from pathlib import Path
import shutil

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_source_file(filepath):
    """Check if source file has initial key tag."""
    print_header("STEP 1: Checking Source File")
    print(f"File: {filepath}")

    if not os.path.exists(filepath):
        print(f"❌ ERROR: File does not exist!")
        return None

    print(f"✓ File exists (size: {os.path.getsize(filepath)} bytes)")

    try:
        from mutagen.mp3 import MP3
        audio = MP3(filepath)

        print(f"\nFile Type: MP3")
        print(f"Has tags: {audio.tags is not None}")

        if audio.tags:
            print(f"Tag type: {type(audio.tags)}")
            print(f"Number of tags: {len(audio.tags.keys())}")
            print(f"\nAll tags: {list(audio.tags.keys())}")

            # Check for TKEY
            if 'TKEY' in audio.tags:
                tkey = audio.tags['TKEY']
                print(f"\n✓ TKEY tag found!")
                print(f"  Value: {tkey.text}")
                print(f"  Encoding: {tkey.encoding}")
                return str(tkey.text[0]) if tkey.text else None
            else:
                print(f"\n❌ TKEY tag NOT found!")
                print(f"   This file does not have an initial key tag.")
                print(f"   You need to use a file that has been tagged with a key.")
                return None
        else:
            print(f"\n❌ File has no tags at all!")
            return None

    except Exception as e:
        print(f"❌ ERROR reading file: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_target_file_before(filepath):
    """Check target file before modification."""
    print_header("STEP 2: Checking Target File (Before)")
    print(f"File: {filepath}")

    if not os.path.exists(filepath):
        print(f"❌ ERROR: File does not exist!")
        return

    print(f"✓ File exists (size: {os.path.getsize(filepath)} bytes)")

    try:
        from mutagen.mp4 import MP4
        audio = MP4(filepath)

        print(f"\nFile Type: M4A/MP4")
        print(f"Has tags: {audio.tags is not None}")

        if audio.tags:
            print(f"Number of tags: {len(audio.tags.keys())}")
            print(f"\nAll tags present:")
            for key in sorted(audio.tags.keys()):
                value = audio.tags[key]
                print(f"  {key}: {value}")

            # Check for initial key
            key_tag = '----:com.apple.iTunes:initialkey'
            if key_tag in audio.tags:
                print(f"\n⚠ Initial key already exists: {audio.tags[key_tag]}")
            else:
                print(f"\n✓ Initial key NOT present (ready to write)")
        else:
            print(f"\n✓ File has no tags (ready to write)")

    except Exception as e:
        print(f"❌ ERROR reading file: {e}")
        import traceback
        traceback.print_exc()

def write_with_tmm(source_path, target_path, key_value):
    """Attempt to write using TMM classes."""
    print_header("STEP 3: Writing with TMM")

    try:
        from tmm.metadata.writer import MetadataWriter
        from tmm.metadata.reader import MetadataReader

        print(f"Source: {source_path}")
        print(f"Target: {target_path}")
        print(f"Key value: {key_value}")

        # Create backup
        backup_path = target_path + ".backup"
        shutil.copy(target_path, backup_path)
        print(f"\n✓ Created backup: {backup_path}")

        # Initialize writer
        print(f"\nInitializing MetadataWriter...")
        writer = MetadataWriter(str(target_path))
        print(f"  Format detected: {writer.format_type}")
        print(f"  Audio file loaded: {writer.audio_file is not None}")
        print(f"  Audio file type: {type(writer.audio_file)}")

        if writer.audio_file is not None:
            print(f"  Has tags: {writer.audio_file.tags is not None}")
            if writer.audio_file.tags is not None:
                print(f"  Tags type: {type(writer.audio_file.tags)}")

        # Write tag
        print(f"\nWriting initial_key tag...")
        result = writer.write_tag('initial_key', key_value)
        print(f"  write_tag() returned: {result}")

        if not result:
            print(f"  ❌ write_tag() returned False!")
            print(f"  Checking why...")

            # Debug
            if writer.audio_file is None:
                print(f"    - audio_file is None")
            if not writer.format_type:
                print(f"    - format_type is invalid: {writer.format_type}")
            if key_value is None:
                print(f"    - value is None")

            return False

        # Save
        print(f"\nSaving file...")
        save_result = writer.save()
        print(f"  save() returned: {save_result}")

        if not save_result:
            print(f"  ❌ save() failed!")
            return False

        print(f"\n✓ Write completed successfully")
        return True

    except Exception as e:
        print(f"❌ ERROR during write: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_target_file_after(filepath):
    """Check target file after modification."""
    print_header("STEP 4: Checking Target File (After)")
    print(f"File: {filepath}")

    try:
        from mutagen.mp4 import MP4
        audio = MP4(filepath)

        print(f"\nFile Type: M4A/MP4")
        print(f"Has tags: {audio.tags is not None}")

        if audio.tags:
            print(f"Number of tags: {len(audio.tags.keys())}")
            print(f"\nAll tags present:")
            for key in sorted(audio.tags.keys()):
                value = audio.tags[key]
                print(f"  {key}: {value}")

            # Check for initial key
            key_tag = '----:com.apple.iTunes:initialkey'
            if key_tag in audio.tags:
                value = audio.tags[key_tag]
                print(f"\n✅ SUCCESS! Initial key found: {value}")

                # Try to decode
                if value:
                    try:
                        decoded = value[0].decode('utf-8') if isinstance(value[0], bytes) else str(value[0])
                        print(f"   Decoded value: {decoded}")
                    except:
                        print(f"   Could not decode value")

                return True
            else:
                print(f"\n❌ FAILED! Initial key NOT found after write!")
                return False
        else:
            print(f"\n❌ File has no tags!")
            return False

    except Exception as e:
        print(f"❌ ERROR reading file: {e}")
        import traceback
        traceback.print_exc()
        return False

def read_with_tmm(filepath):
    """Try reading with TMM reader."""
    print_header("STEP 5: Reading with TMM Reader")

    try:
        from tmm.metadata.reader import MetadataReader

        reader = MetadataReader(str(filepath))
        print(f"Format detected: {reader.format_type}")

        value = reader.read_tag('initial_key')
        print(f"\nread_tag('initial_key') returned: {value}")

        if value:
            print(f"✅ TMM Reader successfully read the tag!")
            return True
        else:
            print(f"❌ TMM Reader could not read the tag!")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  TMM Initial Key Transfer Diagnostic Tool".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "═"*68 + "╝")

    # Check for test files
    source_file = "test_files/source/test_source.mp3"
    target_file = "test_files/target/test_source.m4a"

    if not os.path.exists(source_file):
        print(f"\n❌ ERROR: Source file not found: {source_file}")
        print(f"\nPlease follow TESTING_GUIDE.md to set up test files.")
        return 1

    if not os.path.exists(target_file):
        print(f"\n❌ ERROR: Target file not found: {target_file}")
        print(f"\nPlease follow TESTING_GUIDE.md to set up test files.")
        return 1

    # Run diagnostics
    key_value = check_source_file(source_file)

    if key_value is None:
        print(f"\n❌ Cannot continue: Source file has no initial key tag!")
        print(f"   Please use a file that has been tagged with a musical key.")
        return 1

    check_target_file_before(target_file)

    write_success = write_with_tmm(source_file, target_file, key_value)

    if not write_success:
        print(f"\n❌ Write failed! Check errors above.")
        return 1

    read_success = check_target_file_after(target_file)

    if read_success:
        read_with_tmm(target_file)

    # Final summary
    print_header("FINAL SUMMARY")

    if write_success and read_success:
        print("✅ SUCCESS! The initial key tag was written and verified!")
        print("\nThe bug appears to be fixed for these test files.")
        print("If it's still not working in your main workflow, there may be")
        print("a different issue with file matching or processing.")
        return 0
    else:
        print("❌ FAILED! The initial key tag was NOT written successfully!")
        print("\nPlease share this entire output for debugging.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
