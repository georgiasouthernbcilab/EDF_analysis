import os  # Handy OS functions, explore file directory, etc.
import glob  # Useful to grab the EDF files easily
import mne  # The main eeg package / library
import matplotlib.pyplot as plt  # Use as backend when needed
from datetime import datetime  # To time & date stamp output files as needed
import re  # To sanitize filename
from mne.preprocessing import ICA  # Import it explicitly to minimize required code and refer to it more easily

description = 'All_Plots'  # Put a nice description here as it gets saved in the output directory name and code output file
eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']
eog_channels = ['Fp1', 'Fp2']
time_window = 60  # Time window in seconds
apply_proj = True
plot_psd = True
plot_ica_overlay = True
plot_topomap = True

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|,]', '_', filename)

def save_script_copy(script_path, output_directory):
    sanitized_description = sanitize_filename(description)
    script_name = os.path.basename(script_path).replace('.py', f'_{sanitized_description}.py')
    output_path = os.path.join(output_directory, script_name)
    with open(script_path, 'r') as original_script:
        with open(output_path, 'w') as copy_script:
            copy_script.write(original_script.read())
    print(f"Saved a copy of the script to {output_path}")

def process_and_plot(edf_file, output_directory):
    try:
        raw = mne.io.read_raw_edf(edf_file, preload=True, infer_types=True, verbose=True)
        raw.pick(eeg_channels)
        montage = mne.channels.make_standard_montage('standard_1020')
        raw.set_montage(montage, on_missing='ignore')
        raw.set_eeg_reference('average', projection=True)
        if apply_proj:
            raw.apply_proj()
        raw.filter(l_freq=1, h_freq=40)

        ica = ICA(n_components=32, random_state=97, max_iter="auto")
        ica.fit(raw)
        eog_indices, eog_scores = ica.find_bads_eog(raw, ch_name=eog_channels)
        muscle_noise_indices, muscle_noise_scores = ica.find_bads_muscle(raw)
        ica.exclude = list(set(eog_indices + muscle_noise_indices))
        raw_clean = ica.apply(raw.copy())

        events, event_dict = mne.events_from_annotations(raw, regexp='^(?=.*videos)(?!.*neutralVideo)')

        for i, event in enumerate(events):
            event_id = event[-1]
            event_name = list(event_dict.keys())[list(event_dict.values()).index(event_id)]

            start, stop = event[0] / raw.info['sfreq'], min((event[0] + raw.n_times) / raw.info['sfreq'], raw.times[-1])
            start = start + 15
            stop = start + 45
            cropped_raw = raw_clean.copy().crop(tmin=start, tmax=stop)

            if plot_psd:
                fig = cropped_raw.compute_psd(picks=eeg_channels, fmin=1, fmax=40).plot(dB=False, show=False)
                plt.title(f"PSD Plot - Emotion: {event_name}")
                save_figure(fig, edf_file, i, event_name, "psd", output_directory)

            if plot_ica_overlay:
                fig = ica.plot_overlay(cropped_raw, exclude=ica.exclude, picks=eeg_channels, start=0, stop=1500, show=False)
                save_figure(fig, edf_file, i, event_name, "ica_overlay", output_directory)

            if plot_topomap:
                fig = cropped_raw.compute_psd(picks=eeg_channels, fmin=1, fmax=40).plot_topomap(
                    ch_type="eeg", normalize=False, sensors=True, contours=8, outlines='head', cmap='Spectral_r', show=False)
                plt.title(f"PSD TOPOMAP - {event_name}")
                save_figure(fig, edf_file, i, event_name, "psd_topomap", output_directory)
    except Exception as e:
        print(f"Error processing {edf_file}: {e}")

def save_figure(fig, edf_file, epoch_index, event_name, plot_type, output_directory):
    sanitized_event_name = sanitize_filename(event_name)
    subfolder_name = os.path.basename(edf_file)[:6]
    subfolder_path = os.path.join(output_directory, subfolder_name)
    os.makedirs(subfolder_path, exist_ok=True)

    output_filename = f"{os.path.basename(edf_file).replace('.edf', '').replace('.bdf', '')}_epoch_{epoch_index + 1}_{sanitized_event_name}_{plot_type}.png"
    output_path = os.path.join(subfolder_path, output_filename)
    fig.savefig(output_path)
    plt.close(fig)
    print(f"Saved {plot_type} plot for epoch {epoch_index + 1} ({sanitized_event_name}) of {edf_file} to {output_path}")

def find_edf_files(parent_directory):
    extensions = ['*.bdf', '*.edf', '*.edf+']
    edf_files = []
    for ext in extensions:
        edf_files.extend(glob.glob(os.path.join(parent_directory, '**', ext), recursive=True))
    return edf_files

def main(parent_directory, output_directory):
    edf_files = find_edf_files(parent_directory)
    for edf_file in edf_files:
        print(f"Processing file: {edf_file}")
        process_and_plot(edf_file, output_directory)

if __name__ == '__main__':
    parent_directory = 'EDF+'
    output_directory = 'ICA_PSD_TOPO'

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    timestamped_output_directory = os.path.join(output_directory, sanitize_filename(timestamp + description))
    os.makedirs(timestamped_output_directory, exist_ok=True)

    save_script_copy(__file__, timestamped_output_directory)
    main(parent_directory, timestamped_output_directory)