muscle_threshold = 0.6 #0.5
eog_threshold = 4 #3
apply_proj = False
plot_psd = True
plot_ica_overlay = False 
plot_topomap = True
dB=True
normalize = True

output_directory = 'all_plots'
description = f'mt_{muscle_threshold}eogt_{eog_threshold}db_{dB}_nrmlizd_{normalize}'  # Put a nice description here as it gets saved in the output directory name and code output file

import os  # Handy OS functions, explore file directory, etc.
import glob  # Useful to grab the EDF files easily
import mne  # The main eeg package / library
import matplotlib.pyplot as plt  # Use as backend when needed
from datetime import datetime  # To time & date stamp output files as needed
import re  # To sanitize filename
from mne.preprocessing import ICA  # Import it explicitly to minimize required code and refer to it more easily

eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']
eog_channels=['Fp1', 'Fp2']

## NOTES:
# Try and edit required z scores for the data, as it will affect filtering a lot!
# the EOG indicies and such
# may be nice to iterate through variations and plot them!


def sanitize_filename(filename):
    
    print(f'filename:{filename}')
    ### Sanitize the filename to remove or replace invalid characters
    return re.sub(r'[\\/*?:"<>|,]', '_', filename)

def save_script_copy(script_path, output_directory):
    ## Save a copy of the script in the output directory
    sanitized_description = sanitize_filename(description)
    script_name = os.path.basename(script_path).replace('.py', f'_{sanitized_description}.py')
    output_path = os.path.join(output_directory, script_name)
    with open(script_path, 'r') as original_script:
        with open(output_path, 'w') as copy_script:
            copy_script.write(original_script.read())
    print(f"Saved a copy of the script to {output_path}")

def generate_plots(edf_file, output_directory):
    try:
        raw = mne.io.read_raw_edf(
            edf_file, 
            preload=True, 
            infer_types=True, 
            verbose=True
            )# Load the EDF/BDF file
        raw.pick(eeg_channels)# Pick only EEG channels
        montage = mne.channels.make_standard_montage('standard_1020') # Define the locations
        raw.set_montage(montage, on_missing='ignore') # Set locations and handle error
        # raw.set_montage(montage, on_missing='raise') # Set locations and handle error
        raw.set_eeg_reference(
            ref_channels = "average",
            projection = apply_proj,
            #projection=True,  
            ch_type = "eeg",
            # ch_type = "auto",
            # forward = None,
            # joint = False,
            verbose = False
            )# Set EEG average reference and apply band-pass filter
        
        if apply_proj:
            raw.apply_proj()
        raw.filter(
            l_freq=0.1, 
            h_freq=40,
            picks=eeg_channels,
            n_jobs = 4,            
            ) # Apply bandpass filter
        
        #         l_freq: Any,
        #     h_freq: Any,
        #     picks: Any | None = None,
        #     filter_length: str = "auto",
        #     l_trans_bandwidth: str = "auto",
        #     h_trans_bandwidth: str = "auto",
        #     n_jobs: Any | None = None,
        #     method: str = "fir",
        #     iir_params: Any | None = None,
        #     phase: str = "zero",
        #     fir_window: str = "hamming",
        #     fir_design: str = "firwin",
        #     skip_by_annotation: Any = ("edge", "bad_acq_skip"),
        #     pad: str = "reflect_limited",
        #     verbose: Any | None = None
        # ) -> (BaseRaw | FilterMixin | _BaseSourceEstimate)

        # Set up ICA
        ica = ICA(
            # n_components=30,
            n_components=32,
            #noise_cov = 
            #method =
            # fit_params = 
            random_state=97,
            max_iter=800,
            # max_iter="auto",
            )
         
        ica.fit(
            inst = raw,
            picks = eeg_channels,
            # start =,
            # stop =,
            # decim =,
            # reject =,
            # flat =,
            tstep = 2,
            # reject_by_annotation = True,
            verbose = False,
            )

        # Find EOG and muscle artifacts
        eog_indices, eog_scores = ica.find_bads_eog(
            raw, 
            ch_name=eog_channels,
            threshold = eog_threshold,
            measure = "zscore",
            verbose = False
            )  # Define EOG indicies and scores
        
        muscle_noise_indices, muscle_noise_scores = ica.find_bads_muscle(
            inst= raw,
            threshold = muscle_threshold,
            # start: Any | None = None,
            # stop: Any | None = None,
            # l_freq: int = 7,
            # h_freq: int = 45,
            # sphere: Any | None = None,
            verbose= False
            )
        
        # Exclude the identified artifact components
        ica.exclude = list(set(eog_indices + muscle_noise_indices)) # NOTE: This excludes a lot!  Can set this to be more or less
        
        # Apply ICA to the raw data
        raw_clean = ica.apply(raw.copy())
        events, event_dict = mne.events_from_annotations(raw_clean, regexp='^(?=.*videos)(?!.*neutralVideo)') # Extract events and create epochs
        #events, event_dict = mne.events_from_annotations(raw, regexp='^(?=.*videos)(?!.*neutralVideo)') # Extract events and create epochs
        
        # Loop through each event and plot PSD
        for i, event in enumerate(events):
            event_id = event[-1]
            event_name = list(event_dict.keys())[list(event_dict.values()).index(event_id)]
            event_name = re.search(r'\\([^\\]+)\.(mp4|mkv)', event_name)
            event_name = event_name.group(1)
            # Define the time span for the event
            start = event[0] / raw.info['sfreq'] #start, stop = event[0] / raw.info['sfreq'], min((event[0] + raw.n_times) / raw.info['sfreq'], raw.times[-1])
            start = start + 15
            stop = start + 44
            
            try:
                cropped_raw = raw_clean.copy().crop(tmin=start, tmax=stop)# Crop the raw data to the event span
            except:
                # try:
                #     cropped_raw = raw_clean.copy().crop(tmin=start, tmax=stop-5)
                # except:
                cropped_raw = raw_clean.picks(eeg_channels).copy().crop(tmin=start)
                event_name = event_name + str(start) + 'shortened'
                test = input('Press enter to coninue')

            sanitized_event_name = sanitize_filename(event_name)
            # Determine subfolder based on the first 6 characters of the filename
            subfolder_name = os.path.basename(edf_file)[:6]
            subfolder_path = os.path.join(output_directory, subfolder_name)
            os.makedirs(subfolder_path, exist_ok=True)
            # Add title to the plot
            plt.title(f"{event_name}")
            
            # Save the plot to a PNG file
            psd_output_filename = f"{os.path.basename(edf_file).replace('.edf', '').replace('.bdf', '')}_epoch_{i + 1}_{sanitized_event_name}_psd.png"
            psd_output_path = os.path.join(subfolder_path, psd_output_filename)
            psd_fig = cropped_raw.compute_psd(picks=eeg_channels, fmin=1, fmax=40).plot(
                dB=dB, 
                show=False)  # Set dB=False here
            psd_fig.savefig(psd_output_path)
            plt.close(psd_fig)  # Close the figure to free up memory
            print(f"Saved PSD plot for epoch {i + 1} ({sanitized_event_name}) of {edf_file} to {psd_output_path}")
            
            # Save the plot to a PNG file
            ica_output_filename = f"{os.path.basename(edf_file).replace('.edf', '').replace('.bdf', '')}_epoch_{i + 1}_{sanitized_event_name}_ica_overlay.png"
            ica_output_path = os.path.join(subfolder_path, ica_output_filename)
            # Plot ICA overlay for the cropped raw data
            plt.title(f"{event_name}")
            if plot_ica_overlay:
                try: # NOTE: Failure causes raised exception!!
                    ica_fig = ica.plot_overlay(
                        cropped_raw, 
                        # exclude=ica.exclude, 
                        picks=eeg_channels, 
                        start = start, 
                        stop = stop,
                        title = event_name,
                        show=False,
                        # n_pca_components = 32,
                        )# on_baseline = None
                    
                    ica_fig.savefig(ica_output_path)
                    plt.close(ica_fig)  # Close the figure to free up memory
                    # print(f"Saved ICA overlay plot for epoch {i + 1} ({sanitized_event_name}) of {edf_file} to {ica_output_path}")
                except Exception as e:
                    print(e)
            # Plot the PSD for the cropped raw data
            # try:
            topo_fig = cropped_raw.compute_psd(picks=eeg_channels, fmin=1, fmax=40).plot_topomap(
                ch_type="eeg",
                normalize=normalize,  #NOTE: KEY!!!
                sensors=True, 
                # names=None, 
                mask=None, 
                mask_params=None, 
                contours=6, 
                outlines='head', 
                sphere=None, 
                image_interp='cubic', #'nearest' 'linear'
                extrapolate='auto', 
                border='mean', 
                res=64, 
                size=1, 
                # cmap='RdBu_r', 
                # cmap='viridis', 
                # cmap='plasma', 
                # cmap='inferno', 
                # cmap='magma', 
                # cmap='cividis', 
                cmap='Spectral_r', 
                vlim=(None, None), 
                cnorm=None, 
                axes=None, 
                show=False, 
                )
                

            # # Add title to the plot
            # plt.title(f"{event_name}")
            plt.title(f"{event_name}")
            # Save the plot to a PNG file
            topo_output_filename = f"{os.path.basename(edf_file).replace('.edf', '').replace('.bdf', '')}_epoch_{i + 1}_{sanitized_event_name}_psd_topomap.png"
            topo_output_path = os.path.join(subfolder_path, topo_output_filename)
            topo_fig.savefig(topo_output_path)
            plt.close(topo_fig)  # Close the topo_figure to free up memory
            print(f"Saved PSD plot for epoch {i + 1} ({sanitized_event_name}) of {edf_file} to {topo_output_path}")
            # except:
            #     pass

    except Exception as e:
        print(f"Error processing {edf_file}: {e}")


def find_edf_files(parent_directory):  # Self explanatory, let's grab every EDF file and process it
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
        # if plot_ica_overlay:
        #     # plot_ica_overlay(edf_file, output_directory)
        # if plot_psd:
        #     generate_plots(edf_file, output_directory)
        # if plot_topomap:
        #     plot_topomap(edf_file, output_directory)
if __name__ == '__main__':
    parent_directory = 'EDF+'
    
    
    # Create a timestamped subfolder in the output directory
    timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
    timestamped_output_directory = os.path.join(output_directory, sanitize_filename(timestamp + description))
    os.makedirs(timestamped_output_directory, exist_ok=True)
    
    # Save a copy of the script in the output directory for a verbatim record of code that produced the relevant graphs
    save_script_copy(__file__, timestamped_output_directory)
    
    main(parent_directory, timestamped_output_directory)
