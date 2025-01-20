#!/Applications/FontForge.app/Contents/MacOS/FFPython
import fontforge
import os
import sys
import argparse
import signal
from contextlib import contextmanager
import time


def is_google_drive_glyph(glyphname):
    """Check if glyph name indicates it's a Google Drive related glyph"""
    return "google" in glyphname.lower() or "drive" in glyphname.lower()


def is_excluded_glyph(glyph):
    """Check if glyph should be excluded based on Unicode properties."""
    try:
        # First check the glyph name for Google Drive indicators
        if is_google_drive_glyph(glyph.glyphname):
            return True, "google_drive"

        # Get Unicode value of the glyph
        univalue = glyph.unicode
        if univalue == -1:  # No unicode value assigned
            return False, None

        # Private Use Area ranges
        if (
            0xE000 <= univalue <= 0xF8FF  # Private Use Area
            or 0xF0000 <= univalue <= 0xFFFFD  # Supplementary Private Use Area-A
            or 0x100000 <= univalue <= 0x10FFFD
        ):  # Supplementary Private Use Area-B
            return True, "pua"

        # Emoji ranges
        if (
            0x1F300
            <= univalue
            <= 0x1F9FF  # Miscellaneous Symbols and Pictographs, Emoticons
            or 0x2600 <= univalue <= 0x26FF  # Miscellaneous Symbols
            or 0x2700 <= univalue <= 0x27BF
        ):  # Dingbats
            return True, "emoji"

        # Special symbols ranges
        if (
            0x2000 <= univalue <= 0x23FF  # Punctuation, Technical Symbols
            or 0x2460 <= univalue <= 0x24FF  # Enclosed Alphanumerics
            or 0x2500 <= univalue <= 0x257F  # Box Drawing
            or 0x2580 <= univalue <= 0x259F  # Block Elements
            or 0x25A0 <= univalue <= 0x25FF  # Geometric Shapes
            or 0x2700 <= univalue <= 0x27BF  # Dingbats
            or 0x2800 <= univalue <= 0x28FF  # Braille Patterns
            or 0x2900 <= univalue <= 0x297F  # Supplemental Arrows-B
            or 0x2980 <= univalue <= 0x29FF  # Miscellaneous Mathematical Symbols-B
            or 0x2B00 <= univalue <= 0x2BFF
        ):  # Miscellaneous Symbols and Arrows
            return True, "symbol"

        return False, None

    except Exception as e:
        print(f"Error checking glyph exclusion: {e}")
        return False, None


class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        signal.alarm(0)


def generate_bold_sfd(input_path, bold_weight=10, output_dir=None, force=False):
    print(f"Opening font file: {input_path}")
    try:
        font = fontforge.open(input_path)
    except Exception as e:
        print(f"Error opening font: {e}")
        return False

    print("Processing font metadata...")
    font.fontname = font.fontname + "-Bold"
    font.fullname = font.fullname + " Bold"
    font.weight = "Bold"

    print(f"Applying bold weight of {bold_weight}...")
    try:
        total_glyphs = len(list(font.glyphs()))
        skipped_refs = 0
        skipped_invalid = 0
        skipped_timeout = 0
        skipped_excluded = {"pua": 0, "emoji": 0, "symbol": 0, "google_drive": 0}
        processed_glyphs = 0

        for i, glyph in enumerate(font.glyphs()):
            if i % 10 == 0:
                print(f"Processing glyphs: {i}/{total_glyphs}")

            try:
                # Check if glyph is valid
                if not glyph.isWorthOutputting():
                    print(f"Skipping glyph {glyph.glyphname} - invalid or empty")
                    skipped_invalid += 1
                    continue

                # Check if glyph should be excluded
                is_excluded, reason = is_excluded_glyph(glyph)
                if is_excluded:
                    print(f"Skipping glyph {glyph.glyphname} - {reason}")
                    if reason:
                        skipped_excluded[reason] += 1
                    if reason == "google_drive":
                        print("\nFound Google Drive glyph - stopping processing...")
                        break
                    continue

                # Check for references
                if glyph.references:
                    print(f"Skipping glyph {glyph.glyphname} - contains references")
                    skipped_refs += 1
                    continue

                # Apply weight change with timeout
                try:
                    with time_limit(5):
                        start_time = time.time()
                        glyph.changeWeight(bold_weight)
                        end_time = time.time()
                        print(
                            f"Processed {glyph.glyphname} in {end_time - start_time:.2f} seconds"
                        )
                        processed_glyphs += 1
                except TimeoutException:
                    print(f"Timeout processing glyph {glyph.glyphname} - skipping")
                    skipped_timeout += 1
                    continue

            except Exception as e:
                print(f"Warning: Failed to process glyph {glyph.glyphname}: {e}")

        print(f"\nProcessing complete:")
        print(f"- Processed: {processed_glyphs} glyphs")
        print(f"- Skipped (references): {skipped_refs} glyphs")
        print(f"- Skipped (invalid): {skipped_invalid} glyphs")
        print(f"- Skipped (timeout): {skipped_timeout} glyphs")
        print(f"- Skipped (PUA): {skipped_excluded['pua']} glyphs")
        print(f"- Skipped (emoji): {skipped_excluded['emoji']} glyphs")
        print(f"- Skipped (symbols): {skipped_excluded['symbol']} glyphs")
        print(f"- Skipped (Google Drive): {skipped_excluded['google_drive']} glyphs")

    except Exception as e:
        print(f"Error during bold generation: {e}")
        return False

    if output_dir is None:
        output_dir = os.path.dirname(input_path) or "."

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}-bold.sfd")

    if os.path.exists(output_path) and not force:
        print(
            f"Error: Output file {output_path} already exists. Use --force to overwrite."
        )
        return False

    print(f"Saving to: {output_path}")
    try:
        font.save(output_path)
        print("Bold variant generated successfully!")
        return True
    except Exception as e:
        print(f"Error saving font: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate a bold variant of a font file."
    )
    parser.add_argument("input_file", help="Path to the input font file")
    parser.add_argument(
        "--weight", "-w", type=float, default=10, help="Bold weight value (default: 10)"
    )
    parser.add_argument(
        "--output-dir", "-o", help="Output directory (default: same as input file)"
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force overwrite of existing output files",
    )

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Error: Input file {args.input_file} does not exist.")
        sys.exit(1)

    if args.output_dir and not os.path.exists(args.output_dir):
        try:
            os.makedirs(args.output_dir)
        except Exception as e:
            print(f"Error creating output directory: {e}")
            sys.exit(1)

    success = generate_bold_sfd(
        args.input_file, args.weight, args.output_dir, args.force
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
