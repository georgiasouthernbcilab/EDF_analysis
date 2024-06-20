import mne
import numpy as np
import matplotlib.pyplot as plt

# Read your EDF file
raw = mne.io.read_raw_edf(r'EDF+\Zacker\Zacker.edf', preload=True, verbose=True, infer_types=True)
print(f"Raw data loaded. Number of channels: {len(raw.ch_names)}, Sampling frequency: {raw.info['sfreq']} Hz")

# Select EEG channels
eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']
raw.pick_channels(eeg_channels)
print(f"Selected EEG channels: {eeg_channels}")

# Set montage
montage = mne.channels.make_standard_montage('standard_1020')
raw.set_montage(montage, on_missing='ignore')
print("Standard 10-20 montage applied.")

# Apply preprocessing steps
raw.set_eeg_reference('average', projection=True)
raw.filter(l_freq=1, h_freq=40)
print("Applied average reference and band-pass filter (1 - 40 Hz).")

# Apply ICA to remove artifacts
ica = mne.preprocessing.ICA(n_components=5, random_state=97, max_iter=800)
ica.fit(raw)
ica.plot_components()
print("ICA applied to remove artifacts.")

# EOG regression
eogRegression = mne.preprocessing.EOGRegression(picks_artifact='Fp1')
eogRegression.fit(raw)
eogCorrected = eogRegression.apply(raw.copy())
print("EOG regression applied.")

# Apply ICA solution to clean data
raw_clean = ica.apply(raw.copy())
print("ICA solution applied to obtain cleaned data.")

# Annotate muscle artifacts using z-score
threshold_muscle = 5  # z-score
annot_muscle, scores_muscle = mne.preprocessing.annotate_muscle_zscore(
    raw,
    ch_type="eeg",
    threshold=threshold_muscle,
    min_length_good=0.2,
    filter_freq=[1, 63],
)

fig, ax = plt.subplots()
ax.plot(raw.times, scores_muscle)
ax.axhline(y=threshold_muscle, color="r")
ax.set(xlabel="time, (s)", ylabel="zscore", title="Muscle activity")

# Convert segments to Annotations format
if annot_muscle is not None:
    raw.set_annotations(annot_muscle)
    raw_clean.set_annotations(annot_muscle)  # Apply the same annotations to cleaned data

    print(f"Muscle artifacts annotated with z-score threshold={threshold_muscle}.")

# Extract events from annotations (if available)


# events_from_annot = mne.events_from_annotations(raw, event_id=None, use_rounding=False)[0]

# Plot raw and cleaned data with annotations and events
order = np.arange(0, len(raw.ch_names))  # Replace with your valid channel indices

# Plot raw data with events and annotations
raw.plot(start=5, duration=20, order=order, title='Raw EEG Data with Annotations and Events', scalings='auto', events=events_from_annot)

# Plot cleaned data with events and annotations
raw_clean.plot(start=5, duration=20, order=order, title='Cleaned EEG Data with Annotations and Events', scalings='auto', events=events_from_annot)

plt.show()

print("Plotted raw and cleaned EEG data with annotations and events.")
print(dir(raw))
raw.merge_events(annot_muscle)