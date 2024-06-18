import mne
import numpy as np
# Apply ICA to the raw EEG data to remove artifacts
from mne.preprocessing import ICA
# Read your EDF file
eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']

# Read your EDF file
raw = mne.io.read_raw_edf(r'my_shared_data_folder/Zacker/Zacker.edf', preload=True, verbose=True, infer_types=True, include=eeg_channels)
events, event_dict = mne.events_from_annotations(raw)
montage = mne.channels.make_standard_montage('standard_1020')
raw.set_montage(montage, on_missing='ignore')

# Apply preprocessing steps
raw.set_eeg_reference('average', projection=True)  # set EEG average reference
raw.filter(l_freq=1, h_freq=40)  # Apply band-pass filter, set low to 1 per suggestion in documentation
# Define baseline period (0 to 30 seconds)
baseline_start = 0
baseline_end = 30

# Get time periods for events with "videos\" in their descriptions, skipping the first 30 seconds
sfreq = raw.info['sfreq']  # Get the sampling frequency
time_periods = []
video_events = []
for event_idx, event in enumerate(events):
    onset_sample = event[0]
    duration_seconds = event[2] / sfreq
    event_description = list(event_dict.keys())[list(event_dict.values()).index(event[2])]
    if "videos\\" in event_description:
        start_time = raw.times[onset_sample] + 30  # Skip the first 30 seconds
        end_time = start_time + 30  # Grab the subsequent 30 seconds
        time_period = (start_time, end_time)
        time_periods.append(time_period)
        video_events.append((event_description, time_period))

# Extract baseline period
baseline_data, _ = raw[:, int(baseline_start * sfreq):int(baseline_end * sfreq)]

# Print video events with their corresponding time periods
for event_idx, (event_description, time_period) in enumerate(video_events):
    print(f"Event {event_idx + 1}: {event_description}, Time Period: {time_period[0]} - {time_period[1]} seconds")


# Set up ICA
ica = ICA(n_components=10, random_state=97, max_iter=800)

# Fit ICA on the raw EEG data
ica.fit(raw)

# Plot ICA components to manually inspect and identify components that capture eye blinks
ica.plot_components()

# Use built-in methods to automatically find EOG-like components (since we don't have EOG data, we use EEG channels)
eog_indices, eog_scores = ica.find_bads_eog(raw, ch_name='Fp1')  # assuming Fp1 is most likely to capture eye blinks
ica.plot_scores(eog_scores)

# Exclude the identified EOG-related components
ica.exclude = eog_indices

# Apply the ICA solution to the raw data to remove the artifacts
raw_clean = ica.apply(raw.copy())
print('Now printing raw graph')
raw.plot()
# Plot the cleaned data to verify the result
print('Now printing cleaned graph')
raw_clean.plot()
print('Now plotting overlay')
ica.plot_overlay(raw)