import os
from PIL import Image

def combine_plots_vertically(output_directory):
    # Iterate through each subfolder in the output directory
    for root, dirs, files in os.walk(output_directory):
        for dir_name in dirs:
            subfolder_path = os.path.join(root, dir_name)
            
            # Gather all PSD topomap plot files in the subfolder
            psd_topomap_files = sorted([f for f in os.listdir(subfolder_path) if f.endswith('_psd_topomap.png')])
            
            if not psd_topomap_files:
                continue
            
            # Open each image and collect them into a list
            images = [Image.open(os.path.join(subfolder_path, img)) for img in psd_topomap_files]
            
            # Determine the width and total height of the combined image
            width, height = images[0].size
            total_height = sum(img.size[1] for img in images)
            
            # Create a new blank image with the same width and total height
            combined_image = Image.new('RGB', (width, total_height))
            
            # Paste each image into the combined image vertically
            y_offset = 0
            for img in images:
                combined_image.paste(img, (0, y_offset))
                y_offset += img.size[1]
            
            # Save the combined image with a descriptive filename
            combined_filename = f"{dir_name}_combined_psd_topomaps.png"
            combined_filepath = os.path.join(subfolder_path, combined_filename)
            combined_image.save(combined_filepath)
            
            print(f"Saved combined PSD topomap for {dir_name} to {combined_filepath}")

# Example usage:
combine_plots_vertically('all_plots')  # Replace 'all_plots' with your output directory path
