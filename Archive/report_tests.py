import mne
from mne.preprocessing import ICA
import matplotlib.pyplot as plt
from pathlib import Path

# Read your EDF file
raw = mne.io.read_raw_edf(r'my_shared_data_folder\Zacker\Zacker.edf', preload=True, verbose=True, infer_types=True)

# Select only EEG channels
eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']
raw.pick_channels(eeg_channels)

# Set montage
montage = mne.channels.make_standard_montage('standard_1020')
raw.set_montage(montage, on_missing='ignore')

# Apply preprocessing steps
raw.set_eeg_reference('average', projection=True)  # set EEG average reference
raw.filter(l_freq=1, h_freq=40)  # Apply band-pass filter

# Apply ICA to the raw EEG data to remove artifacts
# Set up ICA
ica = ICA(n_components=20, random_state=97, max_iter=800) # doesn't work here: , n_jobs=4

# Fit ICA on the raw EEG data
ica.fit(raw)

# Plot ICA components to manually inspect and identify components that capture eye blinks
ica.plot_components()

# Use built-in methods to automatically find ECG-like components
ecg_indices, ecg_scores = ica.find_bads_ecg(raw, ch_name='Fp1')  # assuming Fp1 is most likely to capture ECG artifacts, doesn't work here: , n_jobs=4
ica.plot_scores(ecg_scores)

# Exclude the identified ECG-related components
ica.exclude = ecg_indices

# Apply the ICA solution to the raw data to remove the artifacts
print('Applying ICA solution(s)')
raw_clean = ica.apply(raw.copy())

# Plot the raw and cleaned data for comparison using MNE's plotting functions
print('Now plotting raw data')
raw.plot(title='Raw EEG Data')
print('Now plotting cleaned data!')
raw_clean.plot(title='Cleaned EEG Data')

# Generate a report for the processed data
print('Now generating report')
report = mne.Report(title="Processed EEG Data")
report.add_raw(raw=raw, title="Raw EEG Data", psd=False)
report.add_raw(raw=raw_clean, title="Cleaned EEG Data", psd=False)
report.save("report_processed_eeg.html", overwrite=True)
