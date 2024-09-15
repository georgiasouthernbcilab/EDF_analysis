import os
import mne
import re
import matplotlib.pyplot as plt
from mne.preprocessing import ICA
import numpy as np

def detect_noisy_channels_by_zscore(raw_data, z_threshold=3):
    data = raw_data.get_data()
    channel_std_dev = np.std(data, axis=1)
    z_scores = (channel_std_dev - np.mean(channel_std_dev)) / np.std(channel_std_dev)
    noisy_chs = [raw_data.ch_names[idx] for idx, z in enumerate(z_scores) if np.abs(z) > z_threshold]
    return noisy_chs

def save_raw_to_folder(raw, save_path):
    raw.save(save_path, overwrite=True)


def read_edf(edf_file_path, initial_dir, cleaned_dir):
    volunteer_id  = edf_file_path[5:11]
    os.makedirs(initial_dir, exist_ok=True)
    os.makedirs(cleaned_dir, exist_ok=True)
    
    # raw = mne.io.read_raw_edf(edf_file_path, preload=True)
    raw = mne.io.read_raw_edf(
    edf_file_path,
    #eog=['Fp1', 'Fp2'], # Define eog channels!  I suggest trying making a copy of these as eog1 and eog2 ##NOTE: YOU MUST watch the capitalization!
    misc=None, # List of channel names to be considered as miscellaneous (MISC) channels.
    stim_channel=None,  # Set to None if you don't have a stim channel
    exclude=['TimestampS', 'TimestampMs', 'OrTimestampS', 'OrTimestampMs', 'Counter', 'Interpolated', 'HighBitFlex', 
             'SaturationFlag', 'RawCq', 'Battery', 'BatteryPercent', 'MarkerHardware', 'CQ.Cz', 'CQ.Fz', 'CQ.Fp1', 
             'CQ.F7', 'CQ.F3', 'CQ.FC1', 'CQ.C3', 'CQ.FC5', 'CQ.FT9', 'CQ.T7', 'CQ.CP5', 'CQ.CP1', 'CQ.P3', 'CQ.P7', 
             'CQ.PO9', 'CQ.O1', 'CQ.Pz', 'CQ.Oz', 'CQ.O2', 'CQ.PO10', 'CQ.P8', 'CQ.P4', 'CQ.CP2', 'CQ.CP6', 'CQ.T8', 
             'CQ.FT10', 'CQ.FC6', 'CQ.C4', 'CQ.FC2', 'CQ.F4', 'CQ.F8', 'CQ.Fp2', 'CQ.Overall', 'EQ.SampleRateQua', 
             'EQ.OVERALL', 'EQ.Cz', 'EQ.Fz', 'EQ.Fp1', 'EQ.F7', 'EQ.F3', 'EQ.FC1', 'EQ.C3', 'EQ.FC5', 'EQ.FT9', 
             'EQ.T7', 'EQ.CP5', 'EQ.CP1', 'EQ.P3', 'EQ.P7', 'EQ.PO9', 'EQ.O1', 'EQ.Pz', 'EQ.Oz', 'EQ.O2', 'EQ.PO10', 
             'EQ.P8', 'EQ.P4', 'EQ.CP2', 'EQ.CP6', 'EQ.T8', 'EQ.FT10', 'EQ.FC6', 'EQ.C4', 'EQ.FC2', 'EQ.F4', 'EQ.F8', 
             'EQ.Fp2', 'MOT.TimestampS', 'MOT.TimestampMs', 'MOT.OrTimestampS', 'MOT.OrTimestampM', 'MOT.CounterMems', 
             'MOT.Interpolated', 'MOT.Q0', 'MOT.Q1', 'MOT.Q2', 'MOT.Q3', 'MOT.AccX', 'MOT.AccY', 'MOT.AccZ', 
             'MOT.MagX', 'MOT.MagY', 'MOT.MagZ'],  # Exclude channels you don't want
    preload=True,  # Preload data into memory to speed things up
    infer_types=True,  # Infer channel types from names
    verbose=False  # Set verbosity / output messages
    )
    eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']
    raw.pick_channels(eeg_channels)
    montage = mne.channels.make_standard_montage('standard_1020')
    raw.set_montage(montage, on_missing='ignore')
    raw.set_eeg_reference('average', projection=True)  
    
    annotations = raw.annotations
    annotations_to_analyze = []
    
    onsets = [annotation['onset'] for annotation in annotations]
    durations = [(onsets[i + 1] - onsets[i]) if i < len(onsets) - 1 else 1.0 for i in range(len(onsets))]
    
    for i, annotation in enumerate(annotations):
        onset = annotation['onset']
        duration = durations[i]
        description = annotation['description']
        match = re.findall(r'\d+ \w+', description)
        if len(match) > 0:
            title_name = match[0]
        end_time = onset + duration
        
        # Extract the annotation to analyze directly
        annotation_parts = description.split()
        if len(annotation_parts) > 1:
            emotion = match[0].split()[1]
            emotion_dir_initial = os.path.join(initial_dir, emotion)
            emotion_dir_cleaned = os.path.join(cleaned_dir, emotion)
            os.makedirs(emotion_dir_initial, exist_ok=True)
            os.makedirs(emotion_dir_cleaned, exist_ok=True)
            raw_segment = raw.copy().crop(tmin=onset, tmax=end_time)
            raw_segment.filter(l_freq = 1, h_freq = 40)
            
            ica = ICA(n_components=20, random_state=97, max_iter=800)
            ica.fit(raw_segment)
            eog_indices, eog_scores = ica.find_bads_eog(raw, ch_name=['Fp1', 'Fp2'])
            ica.exclude = eog_indices
            
            raw_clean_segment = ica.apply(raw_segment.copy())
            noisy_chs = detect_noisy_channels_by_zscore(raw_clean_segment) 
            raw_clean_segment.info['bads'].extend(noisy_chs)
            if raw_clean_segment.info['bads']:
                raw_clean_segment.interpolate_bads()
                
            # Save the initial plot
            initial_plot_filename = os.path.join(emotion_dir_initial, f'{volunteer_id}_{i}_{title_name}_initial.png')
            raw_segment.plot(scalings = "auto", show=False, title=f'Initial: {volunteer_id} {title_name}').savefig(initial_plot_filename)
            plt.close()
            
            # Save the cleaned plot
            cleaned_plot_filename = os.path.join(emotion_dir_cleaned, f'{volunteer_id}_{i}_{title_name}_cleaned.png')
            raw_clean_segment.plot(scalings = "auto", show=False, title=f'Cleaned: {volunteer_id} {title_name}').savefig(cleaned_plot_filename)
            plt.close()
            
            # Save the initial and cleaned raw data
            initial_save_path = os.path.join(emotion_dir_initial, f'{volunteer_id}_{i}_{title_name}_raw.fif')
            cleaned_save_path = os.path.join(emotion_dir_cleaned, f'{volunteer_id}_{i}_{title_name}_raw_clean.fif')
            save_raw_to_folder(raw_segment, initial_save_path)
            save_raw_to_folder(raw_clean_segment, cleaned_save_path)
    return raw, annotations_to_analyze

# Walking through the directory to find EDF files
all_annotations = []
initial_directory = 'raw_plots_initial'
cleaned_directory = 'raw_plots_cleaned'
for root, dirs, files in os.walk('EDF+'):
    for file in files:
        if file.endswith('.edf'):
            edf_file_path = os.path.join(root, file)
            try:
                raw, annotations = read_edf(edf_file_path,  initial_directory, cleaned_directory)
                all_annotations.extend(annotations)
            
                    
            except Exception as e:
                print(f"Failed to read {edf_file_path}: {e}")

