import hljs from "highlight.js";
import python from 'highlight.js/lib/languages/python';
import { useEffect } from "react";
import 'highlight.js/styles/default.css'; // Import a highlight.js style

hljs.registerLanguage('python', python);

function Preprocessing_3() {

    useEffect(() => {
        hljs.highlightAll();
    }, []);

    return (
        <>
            <div className="flex flex-col items-center mt-4">
                <h1 className="text-4xl p-4 m-2">Preprocessing 3</h1>
                <div className="p-4 m-2 w-2/3">
                    <p className="mt-10 mb-5">
                        This page details the advanced preprocessing steps for EEG data using MNE-Python. The steps include applying projections, filtering, interpolating bad channels, and visualizing differences.
                    </p>

                    <h2 className="text-3xl p-4 m-2">1. Import Libraries and Define Parameters</h2>
                    <p className="mt-5">
                        In this section, we import essential libraries such as MNE for EEG processing and matplotlib for plotting. We also define basic parameters and EEG channels for our analysis.
                    </p>
                    <pre><code className="language-python">
{`import mne
from mne.preprocessing import ICA
from mne.preprocessing import create_ecg_epochs, create_eog_epochs
import matplotlib.pyplot as plt
from pathlib import Path
from imports.message_user import show_message_plot
import numpy as np

# Define basics and parameters
visualize_difference = True
apply_projection = True

# Define EEG channels
eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']

# Frequencies of interest for EEG analysis
freqs = {
    'delta': (0.5, 4),
    'theta': (4, 8),
    'alpha': (8, 13),
    'beta': (13, 30),
    'gamma': (30, 40)
}

# Create array of frequencies
freqs_array = []
for band in freqs.values():
    freqs_array += list(range(int(band[0]), int(band[1]) + 1))
`}
                    </code></pre>

                    <h2 className="text-3xl p-4 m-2">2. Load and Prepare EEG Data</h2>
                    <p className="mt-5">
                        This section loads the EEG data from an EDF file and selects only the specified EEG channels. The montage is then set according to the 10-20 system.
                    </p>
                    <pre><code className="language-python">
{`# Read your EDF file
raw = mne.io.read_raw_edf(r'EDF+\Zacker\Zacker.edf', preload=True, infer_types=True)

# Select only EEG channels
raw.pick(eeg_channels)  # Explicitly pick EEG channels to avoid picking other channels
print(raw.info)

# Set montage
montage = mne.channels.make_standard_montage('standard_1020')
raw.set_montage(montage, on_missing='ignore')
`}
                    </code></pre>

                    <h2 className="text-3xl p-4 m-2">3. Initial Visualization and Annotation</h2>
                    <p className="mt-5">
                        We provide initial instructions to the user to review the data and annotate any anomalies. This step helps in identifying bad channels that need further preprocessing.
                    </p>
                    <pre><code className="language-python">
{`# Define your message and instructions
message = "Pick bads"
instructions = """
1. Please review the data.
2. Make note of any anomalies.
3. Use the toolbar to zoom and pan.
4. Press A on your keyboard to annotate.
5. Close this window to proceed.
NOTE: The home, end, page up, page down,
and arrow keys all do special functions too
"""
# Display the message plot
show_message_plot(message, instructions)

# Apply preprocessing steps
raw.set_eeg_reference('average', ch_type='eeg', projection=apply_projection)  # Set EEG average reference
if apply_projection:
    raw.apply_proj()  # MUST be applied or it doesn't work!
raw.filter(l_freq=1, h_freq=40)  # Apply band-pass filter
raw.plot(picks=eeg_channels, block=True)
`}
                    </code></pre>

                    <h2 className="text-3xl p-4 m-2">4. Interpolation of Bad Channels</h2>
                    <p className="mt-5">
                        Interpolation is applied to bad channels identified in the previous step. This process estimates the values of bad channels based on the surrounding good channels.
                    </p>
                    <pre><code className="language-python">
{`# Define your message and instructions
message = "Now Interpolating!"
instructions = """
1. Please wait while I interpolate!
2. You may wish to view a before and after
NOTE: The home, end, page up, page down,
and arrow keys all do special functions too
"""
# Display the message plot
show_message_plot(message, instructions)

# Interpolate bads
print(f'bads: {raw.info["bads"]}')
raw_interpolated = raw.copy().interpolate_bads(method='spline')  # Interpolate bad channels

raw_interpolated.plot(picks=eeg_channels, block=True, title='Interpolated bads')
`}
                    </code></pre>

                    <h2 className="text-3xl p-4 m-2">5. Power Spectral Density (PSD) Analysis</h2>
                    <p className="mt-5">
                        After interpolation, we compute and plot the Power Spectral Density (PSD) of the EEG data. This helps in visualizing the power distribution across different frequency bands.
                    </p>
                    <pre><code className="language-python">
{`# Compute and plot PSD
raw_interpolated.compute_psd().plot()
plt.show(block=True)
print('Showed interpolated plot')

# Extract data for plotting
times = raw.times * 1e3  # Convert to milliseconds
data_orig = raw.get_data() * 1e6  # Convert to microvolts
data_interp = raw_interpolated.get_data() * 1e6  # Convert to microvolts
`}
                    </code></pre>

                    <h2 className="text-3xl p-4 m-2">6. Visualization of Differences</h2>
                    <p className="mt-5">
                        If the `visualize_difference` flag is set to True, this section plots the original and interpolated EEG data for comparison. It highlights the differences between the original and processed signals.
                    </p>
                    <pre><code className="language-python">
{`if visualize_difference:
    # Plot original and interpolated data
    fig, ax = plt.subplots(figsize=(15, 10))
    for ch_idx, ch_name in enumerate(eeg_channels):
        ax.plot(times, data_orig[ch_idx] + ch_idx * 100, color='blue', label='Original' if ch_idx == 0 else "")
        ax.plot(times, data_interp[ch_idx] + ch_idx * 100, color='red', linestyle='--', label='Interpolated' if ch_idx == 0 else "")

    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Amplitude (µV)')
    ax.legend(loc='upper right')
    ax.set_title('Original vs Interpolated EEG Data')
    ax.set_yticks([i * 100 for i in range(len(eeg_channels))])
    ax.set_yticklabels(eeg_channels)
    plt.tight_layout()
    plt.show(block=True)
print('Visualized difference')
`}
                    </code></pre>

                    <h2 className="text-3xl p-4 m-2">7. Detection and Annotation of EOG Artifacts</h2>
                    <p className="mt-5">
                        This section detects EOG (Electrooculography) artifacts such as blinks and annotates them in the EEG data. These annotations help in identifying and handling these artifacts during further analysis.
                    </p>
                    <pre><code className="language-python">
{`eog_events = mne.preprocessing.find_eog_events(raw, ch_name=['Fp1', 'Fp2'])
n_blinks = len(eog_events)
onset = eog_events[:, 0] / raw.info['sfreq'] - 0.25
duration = np.repeat(0.5, n_blinks)
annotations = mne.Annotations(onset, duration, ['bad blink'] * n_blinks, orig_time=raw.info['meas_date'])
raw.set_annotations(annotations)
raw.plot(events=eog_events, block=True)  # To see the annotated segments.
print('Plotted events difference')
`}
                    </code></pre>

                    <h2 className="text-3xl p-4 m-2">8. Time-Frequency Representation (TFR)</h2>
                    <p className="mt-5">
                        Although commented out in the code, this section outlines the steps for computing Time-Frequency Representation (TFR) using the multitaper method. TFR provides a detailed view of how power varies with both time and frequency.
                    </p>
                    <pre><code className="language-python">
{`# Compute TFR (commented out)
# tfr = mne.time_frequency.tfr_multitaper(raw_interpolated, freqs=freqs_array, n_cycles=freqs_array, time_bandwidth=2.0, return_itc=False)
# tfr.plot(picks=eeg_channels, baseline=(-0.5, 0), mode='logratio', title='TFR')
# plt.show(block=True)
`}
                    </code></pre>
                </div>
            </div>
        </>
    );
}

export default Preprocessing_3;
