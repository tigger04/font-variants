#!/Applications/FontForge.app/Contents/MacOS/FFPython
import fontforge
import os
import sys

bold_weight = 30

def generate_bold_sfd(input_path):
    # Check if the input file exists
    if not os.path.isfile(input_path):
        print(f"Error: File '{input_path}' not found.")
        sys.exit(1)

    # Generate the output paths
    input_dir, file_name = os.path.split(input_path)
    base_name, _ = os.path.splitext(file_name)
    output_sfd = os.path.join(input_dir, f"{base_name}-bold.sfd")
    output_ttf = os.path.join(input_dir, f"{base_name}-bold.ttf")

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
        print("Applying bold effect glyph by glyph...")
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
        font.generate(output_ttf)
        print(f"Bold TTF file generated: {output_ttf}")

        font.close()
    except Exception as e:
        print(f"Error processing file '{input_path}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_bold_sfd.py <font_file_path>")
        sys.exit(1)

    input_file = sys.argv[1]
    generate_bold_sfd(input_file)
