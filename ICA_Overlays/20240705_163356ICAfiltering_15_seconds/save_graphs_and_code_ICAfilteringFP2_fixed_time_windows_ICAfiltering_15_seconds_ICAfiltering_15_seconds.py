import os  # Handy OS functions, explore file directory, etc.
import glob  # Useful to grab the EDF files easily
import mne  # The main eeg package / library
import matplotlib.pyplot as plt  # Use as backend when needed
from datetime import datetime  # To time & date stamp output files as needed
import re  # To sanitize filename
from mne.preprocessing import ICA  # Import it explicitly to minimize required code and refer to it more easily

description = 'ICAfiltering_15_seconds'  # Put a nice description here as it gets saved in the output directory name and code output file
eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']
time_window = 60  # Time window in seconds

def sanitize_filename(filename):
    ### Sanitize the filename to remove or replace invalid characters
    return re.sub(r'[\\/*?:"<>|,]', '_', filename)

def save_script_copy(script_path, output_directory):
    ## Save a copy of the script in the output directory
    sanitized_description = sanitize_filename(description)
    script_name = os.path.basename(script_path).replace('.py', f'_{sanitized_description}.py')
    output_path = os.path.join(output_directory, script_name)
    with open(script_path, 'r') as original_script:
        with open(output_path, 'w') as copy_script:
            copy_script.write(original_script.read())
    print(f"Saved a copy of the script to {output_path}")

def plot_psd(edf_file, output_directory):
    try:
        # Load the EDF/BDF file
        raw = mne.io.read_raw_edf(edf_file, preload=True, infer_types=True, verbose=True)

        # Pick only EEG channels
        raw.pick_types(eeg=True)

        montage = mne.channels.make_standard_montage('standard_1020')
        raw.set_montage(montage, on_missing='ignore')
        
        # Set EEG average reference and apply band-pass filter
        raw.set_eeg_reference('average', projection=True)
        raw.filter(l_freq=1, h_freq=40)

        # Set up ICA
        ica = ICA(n_components=32, random_state=97, max_iter="auto")
        ica.fit(raw)

        # Find EOG and muscle artifacts
        eog_indices, eog_scores = ica.find_bads_eog(raw, ch_name='Fp2')
        muscle_noise_indices, muscle_noise_scores = ica.find_bads_muscle(raw)
        
        # Exclude the identified artifact components
        ica.exclude = list(set(eog_indices + muscle_noise_indices))
        
        # Apply ICA to the raw data
        raw_clean = ica.apply(raw.copy())
        
        # Extract events and create epochs
        events, event_dict = mne.events_from_annotations(raw, regexp='^(?=.*videos)(?!.*neutralVideo)')
        
        # Loop through each event and plot PSD
        for i, event in enumerate(events):
            event_id = event[-1]
            event_name = list(event_dict.keys())[list(event_dict.values()).index(event_id)]
            
            # Define the time span for the event
            start, stop = event[0] / raw.info['sfreq'], min((event[0] + raw.n_times) / raw.info['sfreq'], raw.times[-1])
            start = start + 15
            stop = start + 45
            
            # Crop the raw data to the event span
            cropped_raw = raw_clean.copy().crop(tmin=start, tmax=stop)
            
            # Plot the PSD for the cropped raw data
            fig = cropped_raw.compute_psd(picks=eeg_channels, fmin=1, fmax=40).plot(dB=False, show=False)  # Set dB=False here
            
            # Sanitize event name for the filename and title
            sanitized_event_name = sanitize_filename(event_name)
            
            # Determine subfolder based on the first 6 characters of the filename
            subfolder_name = os.path.basename(edf_file)[:6]
            subfolder_path = os.path.join(output_directory, subfolder_name)
            os.makedirs(subfolder_path, exist_ok=True)
            
            # Add title to the plot
            plt.title(f"PSD Plot - Emotion: {event_name}")
            
            # Save the plot to a PNG file
            output_filename = f"{os.path.basename(edf_file).replace('.edf', '').replace('.bdf', '')}_epoch_{i + 1}_{sanitized_event_name}_psd.png"
            output_path = os.path.join(subfolder_path, output_filename)
            fig.savefig(output_path)
            plt.close(fig)  # Close the figure to free up memory
            print(f"Saved PSD plot for epoch {i + 1} ({sanitized_event_name}) of {edf_file} to {output_path}")
        
    except Exception as e:
        print(f"Error processing {edf_file}: {e}")



def plot_ica_overlay(edf_file, output_directory):
    try:
        # Load the EDF/BDF file
        raw = mne.io.read_raw_edf(edf_file, preload=True, infer_types=True, verbose=True)

        # Pick only specified EEG channels
        raw.pick_channels(eeg_channels)

        montage = mne.channels.make_standard_montage('standard_1020')
        raw.set_montage(montage, on_missing='ignore')
        
        # Set EEG average reference and apply band-pass filter
        raw.set_eeg_reference('average', projection=True)
        raw.filter(l_freq=1, h_freq=40)

        # Set up ICA
        ica = ICA(n_components=32, random_state=97, max_iter="auto")
        ica.fit(raw)

        # Find EOG and muscle artifacts
        eog_indices, eog_scores = ica.find_bads_eog(raw, ch_name=['Fp1','Fp2'])  # NOTE: Can also be Fp1, it all depends
        # fp2_indices, fp2_scores = ica.find_bads_eog(raw, ch_name='Fp2')  # NOTE: Can also be Fp1, it all depends
        muscle_noise_indices, muscle_noise_scores = ica.find_bads_muscle(raw)
        
        # Exclude the identified artifact components
        ica.exclude = list(set(eog_indices + muscle_noise_indices))
        
        # Plot ICA overlay for the whole recording
        fig = ica.plot_overlay(raw, exclude=ica.exclude, picks=eeg_channels, start = 0, stop = 150000, show=False)
        
        # Save the plot to a PNG file
        output_filename = f"{os.path.basename(edf_file).replace('.edf', '').replace('.bdf', '')}_ica_overlay.png"
        output_path = os.path.join(output_directory, output_filename)
        fig.savefig(output_path)
        plt.close(fig)  # Close the figure to free up memory
        print(f"Saved ICA overlay plot of {edf_file} to {output_path}")

        # Extract events and create epochs
        events, event_dict = mne.events_from_annotations(raw, regexp='^(?=.*videos)(?!.*neutralVideo)')
        
        # Loop through each event and plot ICA overlay
        for i, event in enumerate(events):
            event_id = event[-1]
            event_name = list(event_dict.keys())[list(event_dict.values()).index(event_id)]
            
            # Define the time span for the event
            start = event[0] / raw.info['sfreq']
            stop = start + time_window  # Use the time window variable
            
            # Crop the raw data to the event span
            cropped_raw = raw.copy().crop(tmin=start, tmax=stop)
            
            
            # Plot ICA overlay for the cropped raw data
            fig = ica.plot_overlay(cropped_raw, exclude=ica.exclude, picks=eeg_channels, start = 0, stop = 1500, show=False)
            
            # Sanitize event name for the filename
            sanitized_event_name = sanitize_filename(event_name)
            
            # Determine subfolder based on the first 6 characters of the filename
            subfolder_name = os.path.basename(edf_file)[:6]
            subfolder_path = os.path.join(output_directory, subfolder_name)
            os.makedirs(subfolder_path, exist_ok=True)
            
            # Save the plot to a PNG file
            output_filename = f"{os.path.basename(edf_file).replace('.edf', '').replace('.bdf', '')}_epoch_{i + 1}_{sanitized_event_name}_ica_overlay.png"
            output_path = os.path.join(subfolder_path, output_filename)
            fig.savefig(output_path)
            plt.close(fig)  # Close the figure to free up memory
            print(f"Saved ICA overlay plot for epoch {i + 1} ({sanitized_event_name}) of {edf_file} to {output_path}")
        
    except Exception as e:  # Print out any relevant error codes!
        print(f"Error processing {edf_file}: {e}")

def find_edf_files(parent_directory):  # Self explanatory, let's grab every EDF file and process it
    extensions = ['*.bdf', '*.edf', '*.edf+']
    edf_files = []
    for ext in extensions:
        edf_files.extend(glob.glob(os.path.join(parent_directory, '**', ext), recursive=True))
    return edf_files

def main(parent_directory, output_directory):
    edf_files = find_edf_files(parent_directory)  # Grab EDF files

    for edf_file in edf_files:  # Process EDF files one at a time
        print(f"Processing file: {edf_file}")
        plot_ica_overlay(edf_file, output_directory)
        plot_psd(edf_file, output_directory)

if __name__ == '__main__':
    parent_directory = 'EDF+'
    output_directory = 'ICA_Overlays'
    
    # Create a timestamped subfolder in the output directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    timestamped_output_directory = os.path.join(output_directory, sanitize_filename(timestamp + description))
    os.makedirs(timestamped_output_directory, exist_ok=True)
    
    # Save a copy of the script in the output directory for a verbatim record of code that produced the relevant graphs
    save_script_copy(__file__, timestamped_output_directory)
    
    main(parent_directory, timestamped_output_directory)
