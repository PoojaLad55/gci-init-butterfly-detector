from rembg import remove
import os
from random import sample

# Define the input and output directories
input_folder = 'cropped_images'  # Specify your input folder path
output_folder = 'rembg_images'  # Specify your output folder path

# Check if output folder exists, if not, create it
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
print("1")

# Loop through all files in the input folder
for filename in sample(os.listdir(input_folder),30):
    # Full path to the current file
    print("in for loop")
    input_path = os.path.join(input_folder, filename)

    # Check if it's a file (not a directory)
    if os.path.isfile(input_path):
        # Create the output file path with the same name
        output_path = os.path.join(output_folder, filename)

        # Read the input file, remove background, and write to the output file
        with open(input_path, 'rb') as i:
            input_data = i.read()
            output_data = remove(input_data)

            with open(output_path, 'wb') as o:
                o.write(output_data)

        print(f"Processed {filename} and saved to {output_path}")
