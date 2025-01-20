#!/Applications/FontForge.app/Contents/MacOS/FFPython
import fontforge
import os
import sys
import argparse

defaults = {
    "bold_weight": 10
}

def check_output_paths(input_path, output_dir=None, overwrite=False):
    """Check if output files would be overwritten"""
    _, file_name = os.path.split(input_path)
    base_name, _ = os.path.splitext(file_name)

    # Use output_dir if specified, otherwise use input file's directory
    target_dir = output_dir if output_dir else os.path.dirname(input_path)

    # Create output directory if it doesn't exist
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_sfd = os.path.join(target_dir, f"{base_name}-bold.sfd")
    output_ttf = os.path.join(target_dir, f"{base_name}-bold.ttf")

    existing_files = []
    if os.path.exists(output_sfd):
        existing_files.append(output_sfd)
    if os.path.exists(output_ttf):
        existing_files.append(output_ttf)

    if existing_files and not overwrite:
        raise FileExistsError(
            f"The following output files already exist: {', '.join(existing_files)}\n"
            "Use --force to overwrite existing files."
        )

    return output_sfd, output_ttf


def generate_bold_sfd(input_path, bold_weight=defaults.bold_weight, output_dir=None, force=False):
    # Check if the input file exists
    if not os.path.isfile(input_path):
        print(f"Error: File '{input_path}' not found.")
        sys.exit(1)

    # Check output paths before processing
    try:
        output_sfd, output_ttf = check_output_paths(input_path, output_dir, force)
    except FileExistsError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"Error creating output directory: {e}")
        sys.exit(1)

    try:
        # Open the font
        font = fontforge.open(input_path)

        # Update metadata for bold variant
        print("Updating font metadata for bold variant...")
        # removing "regular" from the font name, case insensitive
        font.fontname = font.fontname.replace("-Regular", "").replace("-regular", "")
        font.familyname = font.familyname
        font.fullname = font.fullname + " Bold"
        font.weight = "Bold"

        # Set OS/2 weight class (directly via font.os2_weight)
        font.os2_weight = 700  # 700 is the standard value for "Bold"

        # Update unique identifier
        font.appendSFNTName(
            "English (US)", "UniqueID", f"{font.fullname} {font.version}"
        )

        # Validate and repair the font
        print("Validating and repairing the font...")
        font.validate()

        # Process each glyph individually to avoid infinite loops
        print(f"Applying bold effect (weight: {bold_weight}) glyph by glyph...")
        for glyph in font.glyphs():
            if glyph.isWorthOutputting():
                try:
                    glyph.correctDirection()  # Correct spline directions
                    glyph.changeWeight(bold_weight)  # Apply weight change
                    print(f"Processed glyph: {glyph.glyphname}")
                except Exception as e:
                    print(f"Error processing glyph '{glyph.glyphname}': {e}")

        # Save the modified font as .sfd
        font.save(output_sfd)
        print(f"Bold SFD file generated: {output_sfd}")

        # Optionally generate a TTF for inspection
        # font.generate(output_ttf)
        # print(f"Bold TTF file generated: {output_ttf}")

        font.close()
    except Exception as e:
        print(f"Error processing file '{input_path}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a bold variant of a font file."
    )
    parser.add_argument("input_file", help="Path to the input font file")
    parser.add_argument(
        "--weight", "-w", type=float, default=15, help="Bold weight value (default: 15)"
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

    generate_bold_sfd(args.input_file, args.weight, args.output_dir, args.force)
