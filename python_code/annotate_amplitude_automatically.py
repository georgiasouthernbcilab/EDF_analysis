import mne
from mne.preprocessing import ICA, create_eog_epochs

# Read your EDF file
raw = mne.io.read_raw_edf(r'EDF+\Zacker\Zacker.edf', preload=True, verbose=True, infer_types=True)
eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']

# Parameters for annotation
peak = 0.00005
peak_max = 10
flat = None
bad_percent = 1
bad_percent_max = 10
min_duration = 0.01
min_duration_max = 2
picks = eeg_channels
verbose = True

# Select only EEG channels
raw.pick_channels(eeg_channels)

# Set montage
montage = mne.channels.make_standard_montage('standard_1020')
raw.set_montage(montage, on_missing='ignore')

# Apply preprocessing steps
raw.set_eeg_reference('average', projection=True)  # set EEG average reference
raw.filter(l_freq=1, h_freq=40)  # Apply band-pass filter

# Apply ICA to the raw EEG data to remove artifacts
ica = ICA(n_components=5, random_state=97, max_iter=800)
ica.fit(raw)

# Use built-in methods to automatically find EOG-like components
eog_indices, eog_scores = ica.find_bads_eog(raw, ch_name='Fp1')  # Use an appropriate EEG channel for EOG detection

# Exclude the identified EOG-related components
ica.exclude = eog_indices

# Apply the ICA solution to the raw data to remove the artifacts
raw_clean = ica.apply(raw.copy())

# Define the annotation function with iterative parameter adjustments
def annotate_amplitude_iterative():
    global peak, flat, bad_percent, min_duration
    annotations_found = False
    
    while peak <= peak_max:
        print(f"Trying peak: {peak}")
        annotations, bad_segments = mne.preprocessing.annotate_amplitude(
            raw, 
            peak=peak, 
            flat=flat, 
            bad_percent=bad_percent, 
            min_duration=min_duration, 
            picks=eeg_channels, 
            verbose=verbose
        )
        
        if len(annotations) > 2:
            annotations_found = True
            break
        
        peak += 0.05
    
    if not annotations_found:
        print("No annotations found with peak. Adjusting bad_percent.")
        peak = 0.00005  # Reset peak for the next iteration
        
        while bad_percent <= bad_percent_max:
            print(f"Trying bad_percent: {bad_percent}")
            annotations, bad_segments = mne.preprocessing.annotate_amplitude(
                raw, 
                peak=peak, 
                flat=flat, 
                bad_percent=bad_percent, 
                min_duration=min_duration, 
                picks=eeg_channels, 
                verbose=verbose
            )
            
            if len(annotations) > 2:
                annotations_found = True
                break
            
            bad_percent += 1
    
    if annotations_found:
        print(f"Annotations found with peak: {peak}, bad_percent: {bad_percent}")
        bad_annotations = mne.Annotations(onset=annotations.onset, duration=annotations.duration, description=annotations.description, orig_time=raw.info['meas_date'])
        raw.set_annotations(bad_annotations)
        return annotations, len(annotations)
    else:
        print("No annotations found after iterating through all parameters.")
        return None, 0

# Run the annotation function
annotations, num_annotations = annotate_amplitude_iterative()

raw.plot(title='Raw EEG Data', block=True)
print('Peak:', peak)
print('Number of annotations:', num_annotations)