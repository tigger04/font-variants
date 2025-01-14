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
    output_path = os.path.join(input_dir, f"bold_{base_name}.sfd")

    try:
        # Open the font and apply bold effect
        font = fontforge.open(input_path)
        font.embolden(20)  # Adjust the value for boldness
        font.save(output_path)
        font.close()
        print(f"Bold SFD file generated: {output_path}")
    except Exception as e:
        print(f"Error processing file '{input_path}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_bold_sfd.py <font_file_path>")
        sys.exit(1)

    input_file = sys.argv[1]
    generate_bold_sfd(input_file)
