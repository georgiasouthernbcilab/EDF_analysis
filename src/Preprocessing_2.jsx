import hljs from "highlight.js";
import python from 'highlight.js/lib/languages/python';
import { useEffect } from "react";
import 'highlight.js/styles/default.css'; // Import a highlight.js style
import { Link } from "react-router-dom";

hljs.registerLanguage('python', python);

function Preprocessing_2() {

    useEffect(() => {
        hljs.highlightAll();
    }, []);

    return (
        <>
            <div className="flex flex-col items-center mt-4">
                <h1 className="text-4xl p-4 m-2">Preprocessing 2</h1>
                <div className="p-4 m-2 w-2/3">
                    <p className="mt-10 mb-5">
                        Here, we will walk through the preprocessing and analysis steps using MNE-Python for EEG data. The code includes loading EDF files, applying filters, performing ICA, and generating various plots.
                    </p>

                    <h2 className="text-3xl p-4 m-2">1. Import Libraries and Define Parameters</h2>
                    <p className="mt-5">
                        In this section, we import essential libraries such as MNE for EEG processing and matplotlib for plotting. We also define key parameters like thresholds for artifact detection, flags for plotting options, and the number of ICA components to use.
                    </p>
                    <pre><code className="language-python">
{`import os  # Handy OS functions, explore file directory, etc.
import glob  # Useful to grab the EDF files easily
import mne  # The main EEG package/library
import matplotlib.pyplot as plt  # Use as backend when needed
from datetime import datetime  # To time & date stamp output files as needed
import re  # To sanitize filename
from mne.preprocessing import ICA  # Import it explicitly to minimize required code and refer to it more easily

muscle_threshold = 0.6  # Threshold for muscle artifacts
eog_threshold = 4  # Threshold for EOG artifacts
apply_proj = False  # Whether to apply projection
plot_psd = True  # Generate and save PSD plots?
plot_ica_overlay = False  # Plot before and after effects of ICA cleaning
plot_topomap = True  # Plot topomap of PSD
dB = True  # Display PSD in dB
normalize = True  # Normalize topomap
n_components = 30  # Number of ICA components
output_directory = 'all_plots'
description = f'mt_{muscle_threshold}eogt_{eog_threshold}db_{dB}_nrmlizd_{normalize}_cmp_{n_components}'  # Description for output directory and files
`}
                    </code></pre>

                    <h2 className="text-3xl p-4 m-2">2. Define EEG and EOG Channels</h2>
                    <p className="mt-5">
                        We specify the EEG and EOG channels that will be used for our analysis. These channels are essential for correctly identifying and processing the EEG and EOG data.
                    </p>
                    <pre><code className="language-python">
{`eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']
eog_channels = ['Fp1', 'Fp2']
`}
                    </code></pre>

                    <h2 className="text-3xl p-4 m-2">3. Define Helper Functions</h2>
                    <h3 className="text-2xl p-2 m-2">Sanitize Filename</h3>
                    <p className="mt-5">
                        This helper function sanitizes filenames by replacing invalid characters, ensuring that filenames are safe to use within the file system.
                    </p>
                    <pre><code className="language-python">
{`def sanitize_filename(filename):
    """Sanitize the filename to remove or replace invalid characters"""
    print(f'filename:{filename}')
    return re.sub(r'[\\/*?:"<>|,]', '_', filename)
`}
                    </code></pre>

                    <h3 className="text-2xl p-2 m-2">Save Script Copy</h3>
                    <p className="mt-5">
                        This function saves a copy of the current script in the output directory. This is useful for keeping a record of the exact code that was used to generate the analysis results.
                    </p>
                    <pre><code className="language-python">
{`def save_script_copy(script_path, output_directory):
    """Save a copy of the script in the output directory"""
    sanitized_description = sanitize_filename(description)
    script_name = os.path.basename(script_path).replace('.py', f'_{sanitized_description}.py')
    output_path = os.path.join(output_directory, script_name)
    with open(script_path, 'r') as original_script:
        with open(output_path, 'w') as copy_script:
            copy_script.write(original_script.read())
    print(f"Saved a copy of the script to {output_path}")
`}
                    </code></pre>

                    <h2 className="text-3xl p-4 m-2">4. Load and Preprocess EDF Files</h2>
                    <p className="mt-5">
                        This function handles the loading of EEG data from an EDF file, applying necessary filters, performing Independent Component Analysis (ICA) to identify and remove artifacts, and generating Power Spectral Density (PSD) and topomap plots. It ensures the EEG data is clean and ready for further analysis.
                    </p>
                    <pre><code className="language-python">
{`def generate_plots(edf_file, output_directory):
    try:
        raw = mne.io.read_raw_edf(
            edf_file,
            preload=True,
            verbose=True
        )  # Load the EDF/BDF file

        raw.pick(eeg_channels)  # Pick only EEG channels
        montage = mne.channels.make_standard_montage('standard_1020')  # Define the locations
        raw.set_montage(montage, on_missing='ignore')  # Set locations and handle error
        raw.set_eeg_reference(
            ref_channels="average",
            projection=apply_proj,
            ch_type="eeg",
            verbose=False
        )  # Set EEG average reference

        if apply_proj:
            raw.apply_proj()
        raw.filter(
            l_freq=1.0,
            h_freq=40,
            picks=eeg_channels,
            n_jobs=4,
        )  # Apply bandpass filter

        # Set up ICA
        ica = ICA(
            n_components=n_components,
            random_state=97,
            max_iter=800,
        )

        ica.fit(
            inst=raw,
            picks=eeg_channels,
            tstep=2,
            verbose=False,
        )

        # Find EOG and muscle artifacts
        eog_indices, eog_scores = ica.find_bads_eog(
            raw,
            ch_name=eog_channels,
            threshold=eog_threshold,
            measure="zscore",
            verbose=False
        )  # Define EOG indices and scores

        muscle_noise_indices, muscle_noise_scores = ica.find_bads_muscle(
            inst=raw,
            threshold=muscle_threshold,
            verbose=False
        )

        # Exclude the identified artifact components
        ica.exclude = list(set(eog_indices + muscle_noise_indices))  # NOTE: This excludes a lot!

        # Apply ICA to the raw data
        raw_clean = ica.apply(raw.copy())
        events, event_dict = mne.events_from_annotations(raw_clean, regexp='^(?=.*videos)(?!.*neutralVideo)')  # Extract events and create epochs

        # Loop through each event and plot PSD
        for i, event in enumerate(events):
            event_id = event[-1]
            event_name = list(event_dict.keys())[list(event_dict.values()).index(event_id)]
            event_name = re.search(r'\\\\([^\\\\]+)\\\\.(mp4|mkv)', event_name)
            event_name = event_name.group(1)
            start = event[0] / raw.info['sfreq']
            start = start + 15
            stop = start + 44

            try:
                cropped_raw = raw_clean.copy().crop(tmin=start, tmax=stop)  # Crop the raw data to the event span
            except:
                cropped_raw = raw_clean.picks(eeg_channels).copy().crop(tmin=start)
                event_name = event_name + str(start) + 'shortened'

            sanitized_event_name = sanitize_filename(event_name)
            subfolder_name = os.path.basename(edf_file)[:6]
            subfolder_path = os.path.join(output_directory, subfolder_name)
            os.makedirs(subfolder_path, exist_ok=True)
            plt.title(f"{event_name}")

            # Save the plot to a PNG file
            psd_output_filename = f"{os.path.basename(edf_file).replace('.edf', '').replace('.bdf', '')}_epoch_{i + 1}_{sanitized_event_name}_psd.png"
            psd_output_path = os.path.join(subfolder_path, psd_output_filename)
            psd_fig = cropped_raw.compute_psd(picks=eeg_channels, fmin=1, fmax=40).plot(
                dB=dB,
                show=False
            )
            psd_fig.savefig(psd_output_path)
            plt.close(psd_fig)  # Close the figure to free up memory
            print(f"Saved PSD plot for epoch {i + 1} ({sanitized_event_name}) of {edf_file} to {psd_output_path}")

            ica_output_filename = f"{os.path.basename(edf_file).replace('.edf', '').replace('.bdf', '')}_epoch_{i + 1}_{sanitized_event_name}_ica_overlay.png"
            ica_output_path = os.path.join(subfolder_path, ica_output_filename)
            plt.title(f"{event_name}")

            if plot_ica_overlay:
                try:
                    ica_fig = ica.plot_overlay(
                        cropped_raw,
                        picks=eeg_channels,
                        start=start,
                        stop=stop,
                        title=event_name,
                        show=False,
                    )
                    ica_fig.savefig(ica_output_path)
                    plt.close(ica_fig)  # Close the figure to free up memory
                except Exception as e:
                    print(e)

            topo_fig = cropped_raw.compute_psd(picks=eeg_channels, fmin=1, fmax=40).plot_topomap(
                ch_type="eeg",
                normalize=normalize,
                sensors=True,
                contours=6,
                outlines='head',
                image_interp='cubic',
                cmap='Spectral_r',
                show=False,
            )

            plt.title(f"{event_name}")
            topo_output_filename = f"{os.path.basename(edf_file).replace('.edf', '').replace('.bdf', '')}_epoch_{i + 1}_{sanitized_event_name}_psd_topomap.png"
            topo_output_path = os.path.join(subfolder_path, topo_output_filename)
            topo_fig.savefig(topo_output_path)
            plt.close(topo_fig)  # Close the figure to free up memory
            print(f"Saved PSD plot for epoch {i + 1} ({sanitized_event_name}) of {edf_file} to {topo_output_path}")

    except Exception as e:
        print(f"Error processing {edf_file}: {e}")
`}
                    </code></pre>

                    <h2 className="text-3xl p-4 m-2">5. Find and Process EDF Files</h2>
                    <p className="mt-5">
                        This section includes functions to find all EDF files in the specified directory and process each one by one, ensuring each file is analyzed and the results are saved appropriately.
                    </p>
                    <pre><code className="language-python">
{`def find_edf_files(parent_directory):
    """Grab every EDF file and process it"""
    extensions = ['*.bdf', '*.edf', '*.edf+']
    edf_files = []
    for ext in extensions:
        edf_files.extend(glob.glob(os.path.join(parent_directory, '**', ext), recursive=True))
    return edf_files

def main(parent_directory, output_directory):
    edf_files = find_edf_files(parent_directory)  # Grab EDF files

    for edf_file in edf_files:  # Process EDF files one at a time
        print(f"Processing file: {edf_file}")
        generate_plots(edf_file, output_directory)

if __name__ == '__main__':
    parent_directory = 'EDF+'

    # Create a timestamped subfolder in the output directory
    timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
    timestamped_output_directory = os.path.join(output_directory, sanitize_filename(timestamp + description))
    os.makedirs(timestamped_output_directory, exist_ok=True)

    # Save a copy of the script in the output directory for a verbatim record of code that produced the relevant graphs
    save_script_copy(__file__, timestamped_output_directory)

    main(parent_directory, timestamped_output_directory)
`}
                    </code></pre>
                </div>
                <Link to ="/Preprocessing_3" className="text-[#598392] mb-10">Next Preprocessing Page</Link>
            </div>
        </>
    );
}

export default Preprocessing_2;
