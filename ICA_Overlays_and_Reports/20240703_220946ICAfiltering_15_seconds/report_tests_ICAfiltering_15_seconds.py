import os
import glob
import mne
from mne.preprocessing import ICA
from datetime import datetime
import re

# Constants
description = 'ICAfiltering_15_seconds'
eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']
time_window = 60  # Time window in seconds

def sanitize_filename(filename):
    """Sanitize the filename to remove or replace invalid characters."""
    return re.sub(r'[\\/*?:"<>|,]', '_', filename)

def save_script_copy(script_path, output_directory):
    """Save a copy of the script in the output directory."""
    sanitized_description = sanitize_filename(description)
    script_name = os.path.basename(script_path).replace('.py', f'_{sanitized_description}.py')
    output_path = os.path.join(output_directory, script_name)
    with open(script_path, 'r') as original_script:
        with open(output_path, 'w') as copy_script:
            copy_script.write(original_script.read())
    print(f"Saved a copy of the script to {output_path}")

def plot_ica_overlay(edf_file, output_directory):
    """Plot ICA overlay for the specified EDF file and save plots."""
    try:
        # Load the EDF/BDF file
        raw = mne.io.read_raw_edf(edf_file, preload=True, infer_types=True, verbose=True)

        # Pick only specified EEG channels
        raw.pick_channels(eeg_channels)

        # Set montage
        montage = mne.channels.make_standard_montage('standard_1020')
        raw.set_montage(montage, on_missing='ignore')

        # Set EEG average reference and apply band-pass filter
        raw.set_eeg_reference('average', projection=True)
        raw.filter(l_freq=1, h_freq=40)

        # Set up ICA
        ica = ICA(n_components=32, random_state=97, max_iter="auto")
        ica.fit(raw)

        # Find EOG and muscle artifacts
        fp1_indices, fp1_scores = ica.find_bads_eog(raw, ch_name='Fp1')
        fp2_indices, fp2_scores = ica.find_bads_eog(raw, ch_name='Fp2')
        muscle_noise_indices, muscle_noise_scores = ica.find_bads_muscle(raw)

        # Exclude the identified artifact components
        ica.exclude = list(set(fp1_indices + fp2_indices + muscle_noise_indices))

        # Plot ICA overlay for the whole recording
        fig = ica.plot_overlay(raw, exclude=ica.exclude, picks=eeg_channels, start=0, stop=None, show=False)

        # Save the plot to a PNG file
        output_filename = f"{os.path.basename(edf_file).replace('.edf', '').replace('.bdf', '')}_ica_overlay.png"
        output_path = os.path.join(output_directory, output_filename)
        fig.savefig(output_path)
        plt.close(fig)  # Close the figure to free up memory
        print(f"Saved ICA overlay plot of {edf_file} to {output_path}")

        # Extract events and create epochs
        events, event_dict = mne.events_from_annotations(raw, regexp='^(?=.*videos)(?!.*neutralVideo)')
        
        # Initialize MNE Report for this file
        report = mne.Report()

        # Add raw EEG data to the report
        report.add_raw(raw=raw, title="Raw EEG Data", psd=False)

        # Apply ICA solution to the raw data to remove artifacts
        raw_clean = ica.apply(raw.copy())

        # Add cleaned EEG data to the report
        report.add_raw(raw=raw_clean, title="Cleaned EEG Data", psd=False)

        # Save the report
        report_filename = f"{os.path.basename(edf_file).replace('.edf', '').replace('.bdf', '')}_ica_report.html"
        report_path = os.path.join(output_directory, report_filename)
        report.save(report_path, overwrite=True)
        print(f"Saved MNE Report for {edf_file} to {report_path}")

    except Exception as e:
        print(f"Error processing {edf_file}: {e}")

def find_edf_files(parent_directory):
    """Find all EDF files in the specified parent directory."""
    extensions = ['*.bdf', '*.edf', '*.edf+']
    edf_files = []
    for ext in extensions:
        edf_files.extend(glob.glob(os.path.join(parent_directory, '**', ext), recursive=True))
    return edf_files

def main(parent_directory, output_directory):
    """Main function to process all EDF files in the specified directory."""
    edf_files = find_edf_files(parent_directory)
    
    for edf_file in edf_files:
        print(f"Processing file: {edf_file}")
        plot_ica_overlay(edf_file, output_directory)

if __name__ == '__main__':
    parent_directory = 'EDF+'
    output_directory = 'ICA_Overlays_and_Reports'

    # Create a timestamped subfolder in the output directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    timestamped_output_directory = os.path.join(output_directory, sanitize_filename(timestamp + description))
    os.makedirs(timestamped_output_directory, exist_ok=True)

    # Save a copy of the script in the output directory
    save_script_copy(__file__, timestamped_output_directory)

    # Process EDF files and generate reports
    main(parent_directory, timestamped_output_directory)
