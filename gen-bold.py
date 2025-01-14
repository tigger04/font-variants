#!/Applications/FontForge.app/Contents/MacOS/FFPython
import fontforge
import os
import sys

def generate_bold_sfd(input_path):
    # Check if the input file exists
    if not os.path.isfile(input_path):
        print(f"Error: File '{input_path}' not found.")
        sys.exit(1)

    # Generate the output path
    input_dir, file_name = os.path.split(input_path)
    base_name, _ = os.path.splitext(file_name)
    output_sfd = os.path.join(input_dir, f"bold_{base_name}.sfd")
    output_ttf = os.path.join(input_dir, f"bold_{base_name}.ttf")

    try:
        # Open the font
        font = fontforge.open(input_path)

        # Validate and repair the font
        print("Validating and repairing the font...")
        font.validate()

        # Convert to cubic splines for reliable operations
        print("Converting to cubic splines...")
        font.selection.all()
        font.changeToCubic()

        # Apply bold effect
        print("Applying bold effect...")
        font.changeWeight(100, "auto", False)  # Adjust weight as needed

        # Save the modified font as .sfd
        font.save(output_sfd)
        print(f"Bold SFD file generated: {output_sfd}")

        # Optionally generate TTF for inspection
        font.generate(output_ttf)
        print(f"Bold TTF file generated: {output_ttf}")

        font.close()
    except Exception as e:
        print(f"Error processing file '{input_path}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv)
