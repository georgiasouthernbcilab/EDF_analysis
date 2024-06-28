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


def read_edf(edf_file_path, save_dir):
    volunteer_id  = edf_file_path[5:11]
    os.makedirs(save_dir, exist_ok=True)
    
    raw = mne.io.read_raw_edf(edf_file_path, preload=True)
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
            emotion_dir = os.path.join(save_dir, emotion)
            os.makedirs(emotion_dir, exist_ok=True)
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
                
            fig, axs = plt.subplots(2, 1, figsize= (12,8))
            psd_fig = raw_segment.compute_psd(fmax = 40).plot(axes=axs[0], show=False)
            axs[0].set_title(f'Before: {volunteer_id} {title_name}')
            
            clean_psd_fig = raw_clean_segment.compute_psd(fmax = 40).plot(axes=axs[1], show=False)
            axs[1].set_title(f'After: {volunteer_id} {title_name}')
            # Save the plot as an image file
            plot_filename = os.path.join(emotion_dir, f'{volunteer_id}_{i}_{title_name}.png')
            plt.savefig(plot_filename)
            plt.close(fig) 
    return raw, annotations_to_analyze

# Walking through the directory to find EDF files
all_annotations = []
save_directory = 'psd_plots'
for root, dirs, files in os.walk('EDF+'):
    for file in files:
        if file.endswith('.edf'):
            edf_file_path = os.path.join(root, file)
            try:
                raw, annotations = read_edf(edf_file_path, save_directory)
                all_annotations.extend(annotations)
            
                    
            except Exception as e:
                print(f"Failed to read {edf_file_path}: {e}")

