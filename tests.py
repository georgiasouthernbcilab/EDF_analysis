# # import mne
# # from mne.preprocessing import ICA
# # # Read your EDF file

# # eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']
# # raw = mne.io.read_raw_edf(r'my_shared_data_folder/Zacker/Zacker.edf', preload=True, verbose=True, infer_types=True, include=eeg_channels) #raw = mne.io.read_raw_edf(r'EDF+\Zacker\Zacker.edf', preload=True, verbose=True, infer_types=True)
# # #raw = mne.io.read_raw_edf(r'e:\EEG\Archive\DATA2OTHERFORMATS\zachary_edf+.edf', preload=True, verbose=True, infer_types=True)

# # # Select only EEG channels
# # raw.pick_channels(eeg_channels)

# # # Set montage
# # montage = mne.channels.make_standard_montage('standard_1020')
# # raw.set_montage(montage, on_missing='ignore')

# # # Apply preprocessing steps
# # raw.set_eeg_reference('average', projection=True)  # set EEG average reference
# # raw.filter(l_freq=1, h_freq=40)  # Apply band-pass filter

# # # Apply ICA to the raw EEG data to remove artifacts
# # # Set up ICA
# # ica = ICA(n_components=20, random_state=97, max_iter=800)
# # ica.fit(raw)

# # # # Plot ICA components to manually inspect and identify components that capture eye blinks
# # # ica.plot_components()
# # # ica.plot_overlay(raw)

# # # ica.plot_components()
# # # ica.plot_overlay(raw)
# # # ica.plot_properties(raw)
# # ica.plot_scores()
# # ica.plot_sources()

# import mne
# from mne.preprocessing import ICA
# import matplotlib.pyplot as plt

# # Specify EEG channels
# eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']

# # Read your EDF file
# raw = mne.io.read_raw_edf(r'my_shared_data_folder/Zacker/Zacker.edf', preload=True, verbose=True, infer_types=True, include=eeg_channels)

# # Select only EEG channels
# raw.pick_channels(eeg_channels)

# # Set montage
# montage = mne.channels.make_standard_montage('standard_1020')
# raw.set_montage(montage, on_missing='ignore')

# # Apply preprocessing steps
# raw.set_eeg_reference('average', projection=True)  # set EEG average reference
# raw.filter(l_freq=1, h_freq=40)  # Apply band-pass filter

# # Apply ICA to the raw EEG data to remove artifacts
# # Set up ICA
# ica = ICA(n_components=20, random_state=97, max_iter=800)
# ica.fit(raw)

# # Plot ICA components to manually inspect and identify components that capture eye blinks
# ica.plot_components(picks=range(20))

# # Use built-in methods to automatically find EOG-like components
# eog_indices, eog_scores = ica.find_bads_eog(raw, ch_name='Fp1')

# # Exclude the identified EOG-related components
# ica.exclude = eog_indices

# # Apply the ICA solution to the raw data to remove the artifacts
# raw_clean = ica.apply(raw.copy())

# # Plot the raw and cleaned data for comparison using MNE's plotting functions
# # raw.plot(title='Raw EEG Data')
# # raw_clean.plot(title='Cleaned EEG Data')
# # ica.plot_components()
# # ica.plot_overlay(raw)
# # ica.plot_properties(raw)
# # ica.plot_scores(eog_scores)
# # ica.plot_sources(raw_clean,block=True)
# # Score sources using the identified EOG components
# # ica.score_sources(raw, target=eog_indices)
# # ica.score_sources(raw)
# ica.score_sources(raw, target=eog_indices)

import mne
from mne.preprocessing import ICA

# Specify EEG channels
eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']

# Read your EDF file
raw = mne.io.read_raw_edf(r'my_shared_data_folder/Zacker/Zacker.edf', preload=True, verbose=True, infer_types=True, include=eeg_channels)

# Select only EEG channels
raw.pick_channels(eeg_channels)

# Set montage
montage = mne.channels.make_standard_montage('standard_1020')
raw.set_montage(montage, on_missing='ignore')

# Apply preprocessing steps
raw.set_eeg_reference('average', projection=True)  # set EEG average reference
raw.filter(l_freq=1, h_freq=40)  # Apply band-pass filter

# Apply ICA to the raw EEG data to remove artifacts
# Set up ICA
ica = ICA(n_components=20, random_state=97, max_iter=800)
ica.fit(raw)

# Plot ICA components to manually inspect and identify components that capture eye blinks
ica.plot_components(picks=range(20))

# Use built-in methods to automatically find EOG-like components
eog_indices, eog_scores = ica.find_bads_eog(raw, ch_name='Fp1')

# Exclude the identified EOG-related components
ica.exclude = eog_indices

# Apply the ICA solution to the raw data to remove the artifacts
raw_clean = ica.apply(raw.copy())

# Plot the raw and cleaned data for comparison using MNE's plotting functions
raw.plot(title='Raw EEG Data')
raw_clean.plot(title='Cleaned EEG Data')

# Score sources using the identified EOG components
ica.score_sources(raw, target=eog_indices)

# Show all plots and keep them open
import matplotlib.pyplot as plt
plt.show()
