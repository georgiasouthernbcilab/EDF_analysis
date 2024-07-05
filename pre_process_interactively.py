import mne
import matplotlib.pyplot as plt

# Define EEG channels and frequencies of interest
eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']

# Read your EDF file
raw = mne.io.read_raw_edf(r'EDF+\Zacker\Zacker.edf', eog=['fp1', 'fp2'], preload=True, infer_types=True)

# Select only EEG channels
raw.pick_channels(eeg_channels)  # Explicitly pick EEG channels to avoid picking other channels

# Set montage
montage = mne.channels.make_standard_montage('standard_1020')
raw.set_montage(montage, on_missing='ignore')

# Apply preprocessing steps
raw.set_eeg_reference('average', projection=True)  # Set EEG average reference
raw.apply_proj()  # Apply projections

# Apply band-pass filter
raw.filter(l_freq=1, h_freq=40)

raw.plot(block=True)
# Interpolate bad channels
raw_interpolated = raw.copy().interpolate_bads(method='spline')
raw.plot(block=False)
raw_interpolated.plot(block=True)
# Compute and plot PSD (Power Spectral Density)
raw_interpolated.plot_psd(fmin=0.5, fmax=40, average=False, spatial_colors=False)

# Plot original and interpolated data for comparison
orig_data = raw.get_data() * 1e6  # Original data in microvolts
interp_data = raw_interpolated.get_data() * 1e6  # Interpolated data in microvolts

times = raw.times * 1e3  # Convert to milliseconds

plt.figure(figsize=(15, 10))
for idx, ch_name in enumerate(eeg_channels):
    plt.plot(times, orig_data[idx] + idx * 100, color='blue', label='Original' if idx == 0 else '')
    plt.plot(times, interp_data[idx] + idx * 100, color='red', linestyle='--', label='Interpolated' if idx == 0 else '')

plt.xlabel('Time (ms)')
plt.ylabel('Amplitude (µV)')
plt.legend(loc='upper right')
plt.title('Original vs Interpolated EEG Data')
plt.yticks([i * 100 for i in range(len(eeg_channels))], eeg_channels)
plt.tight_layout()
plt.show()


# import mne
# from mne.preprocessing import ICA  # Import it explicitly to minimize required code and refer to it more easily


# ## Definitions:

# # Define eeg channels for when we need to pass them explicitly as arguments
# eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']
# eog_channels=['Fp1', 'Fp2']


# ### Syntax: mne.io.read_raw_edf(r'file', eog=[list of eog channels], preload=True, speed things up, infer_types=True, discover channel types) 
# #raw = mne.io.read_raw_edf(r'EDF+\103918\103918.edf', eog=['Fp1', 'Fp2'], preload=True, infer_types=True) ##NOTE: YOU MUST watch the capitalization!
# raw = mne.io.read_raw_edf(
#     r'EDF+\103918\103918.edf',
#     #eog=['Fp1', 'Fp2'], # Define eog channels!  I suggest trying making a copy of these as eog1 and eog2
#     misc=None, # List of channel names to be considered as miscellaneous (MISC) channels.
#     stim_channel=None,  # Set to None if you don't have a stim channel
#     exclude=[],  # Exclude channels you don't want
#     preload=True,  # Preload data into memory to speed things up
#     infer_types=True,  # Infer channel types from names
#     verbose=True  # Set verbosity / output messages
#     )
# montage = mne.channels.make_standard_montage('standard_1020')
# raw.set_montage(montage, on_missing='ignore')
# raw.pick('eeg') # Pick only eeg related data!  However, we still have more data then we need!  We'll plot only the channels we want
# # raw.plot(picks=(eog_channels + eeg_channels), block=True) #Block must be True if working interactively with a .py file.  Also, we are picking only eeg channels

# print('Lets compare with and without dc removed:')
# # raw.pick('eeg').plot(picks=(eog_channels + eeg_channels), title = 'Raw Data',block=True, remove_dc=False) # Pick only eeg related data!  However, we still have more data then we need!  We'll plot only the channels we want
# print('DC removed:')
# print('Notice that removing the DC drifts\n makes more data fit on the graph!\n\n')
# # raw.pick('eeg').plot(picks=(eog_channels + eeg_channels), title = 'Raw Data',block=True) # Pick only eeg related data!  However, we still have more data then we need!  We'll plot only the channels we want
# print("Let's filter the raw so that we can see how much it improves the signal!")
# filtered = raw.copy().filter(l_freq=1, h_freq=40)
# # filtered.pick('eeg') # Pick only eeg related data!  However, we still have more data then we need!  We'll plot only the channels we want
# ica = ICA(n_components=32, random_state=97, max_iter="auto")
# ica.fit(filtered)


# # Find EOG and muscle artifacts
# eog_indices, eog_scores = ica.find_bads_eog(filtered, ch_name=['Fp1','Fp2'])
# muscle_noise_indices, muscle_noise_scores = ica.find_bads_muscle(filtered)

# # Exclude the identified artifact components
# ica.exclude = list(set(eog_indices + muscle_noise_indices))

# # Apply ICA to the raw data
# filtered_clean = ica.apply(filtered.copy())
# # raw #Block must be True if working interactively with a .py file.  Also, we are picking only eeg channels
# filtered_clean.pick('eeg').plot(picks=(eeg_channels), title = 'Filtered Data',block=True)

# # filtered_clean.plot(picks=(eeg_channels), title = 'Interactively Cleaned Data',block=True)

# filtered_clean_interpolated = filtered_clean.copy().interpolate_bads(method='spline')# NOTE: Reset bads = false keeps the bads in the data, just different color!!!
# filtered_clean_interpolated.plot(picks = eeg_channels ,block=True, title='Interpolated bads')