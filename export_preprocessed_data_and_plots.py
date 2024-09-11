muscle_threshold = 0.6 #0.5
eog_threshold = 4 #3
apply_proj = False #Use same settings globally
plot_psd = True # Generate and save PSD plots?
plot_ica_overlay = False # Plot before and after effects of ica cleaning
plot_topomap = True
dB=True
normalize = True
n_components = 30
output_directory = 'all_plots'
description = f'mt_{muscle_threshold}eogt_{eog_threshold}db_{dB}_nrmlizd_{normalize}_cmp_{n_components}'  # Put a nice description here as it gets saved in the output directory name and code output file

import os
import glob
import mne
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import re
from mne.preprocessing import ICA

eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']
eog_channels=['Fp1', 'Fp2']

def sanitize_filename(filename):
    print(f'filename:{filename}')
    return re.sub(r'[\\/*?:"<>|,]', '_', filename)

def save_script_copy(script_path, output_directory):
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
        )
        raw.pick(eeg_channels)
        montage = mne.channels.make_standard_montage('standard_1020')
        raw.set_montage(montage, on_missing='ignore')
        raw.set_eeg_reference(
            ref_channels = "average",
            projection = apply_proj,
            ch_type = "eeg",
            verbose = False
        )
        
        if apply_proj:
            raw.apply_proj() 
        raw.filter(
            l_freq=1.0, 
            h_freq=40,
            picks=eeg_channels,
            n_jobs = 4,            
        )
        
        ica = ICA(
            n_components=n_components,
            random_state=97,
            max_iter=800,
        )
         
        ica.fit(
            inst = raw,
            picks = eeg_channels,
            tstep = 2,
            verbose = False,
        )

        eog_indices, eog_scores = ica.find_bads_eog(
            raw, 
            ch_name=eog_channels,
            threshold = eog_threshold,
            measure = "zscore",
            verbose = False
        )
        
        muscle_noise_indices, muscle_noise_scores = ica.find_bads_muscle(
            inst= raw,
            threshold = muscle_threshold,
            verbose= False
        )
        subfolder_name = os.path.basename(edf_file)[:6]
        subfolder_path = os.path.join(output_directory, subfolder_name)
        os.makedirs(subfolder_path, exist_ok=True)
        ica.exclude = list(set(eog_indices + muscle_noise_indices))
        
        raw_clean = ica.apply(raw.copy())
        events, event_dict = mne.events_from_annotations(raw_clean, regexp='^(?=.*videos)(?!.*neutralVideo)')
        
        # Save complete raw data as .npy
        npy_output_filename = f"{os.path.basename(edf_file).replace('.edf', '').replace('.bdf', '')}raw.npy"
        npy_output_path = os.path.join(subfolder_path, npy_output_filename)
        np.save(npy_output_path, raw_clean.get_data())
        print(f"Saved complete raw data to {npy_output_path}")
        
        for i, event in enumerate(events):
            event_id = event[-1]
            event_name = list(event_dict.keys())[list(event_dict.values()).index(event_id)]
            event_name = re.search(r'\\([^\\]+)\.(mp4|mkv)', event_name)
            event_name = event_name.group(1)
            start = event[0] / raw.info['sfreq']
            start = start + 15
            stop = start + 44
            
            try:
                cropped_raw = raw_clean.copy().crop(tmin=start, tmax=stop)
            except:
                cropped_raw = raw_clean.picks(eeg_channels).copy().crop(tmin=start)
                event_name = event_name + str(start) + 'shortened'
                test = input('Press enter to continue')
           
            sanitized_event_name = sanitize_filename(event_name)
            subfolder_name = os.path.basename(edf_file)[:6]
            subfolder_path = os.path.join(output_directory, subfolder_name)
            os.makedirs(subfolder_path, exist_ok=True)
            
            plt.title(f"{event_name}")
            
            psd_output_filename = f"{os.path.basename(edf_file).replace('.edf', '').replace('.bdf', '')}_epoch_{i + 1}_{sanitized_event_name}_psd.png"
            psd_output_path = os.path.join(subfolder_path, psd_output_filename)
            psd_fig = cropped_raw.compute_psd(picks=eeg_channels, fmin=1, fmax=40).plot(
                dB=dB, 
                show=False
            )
            psd_fig.savefig(psd_output_path)
            plt.close(psd_fig)
            print(f"Saved PSD plot for epoch {i + 1} ({sanitized_event_name}) of {edf_file} to {psd_output_path}")
            
            ica_output_filename = f"{os.path.basename(edf_file).replace('.edf', '').replace('.bdf', '')}_epoch_{i + 1}_{sanitized_event_name}_ica_overlay.png"
            ica_output_path = os.path.join(subfolder_path, ica_output_filename)
            plt.title(f"{event_name}")
            if plot_ica_overlay:
                try:
                    ica_fig = ica.plot_overlay(
                        cropped_raw, 
                        picks=eeg_channels, 
                        start = start, 
                        stop = stop,
                        title = event_name,
                        show=False,
                    )
                    ica_fig.savefig(ica_output_path)
                    plt.close(ica_fig)
                except Exception as e:
                    print(e)
            
            # Save cropped raw data as .npy
            npy_output_filename = f"{os.path.basename(edf_file).replace('.edf', '').replace('.bdf', '')}_epoch_{i + 1}_{sanitized_event_name}_cropped_raw.npy"
            npy_output_path = os.path.join(subfolder_path, npy_output_filename)
            np.save(npy_output_path, cropped_raw.get_data())
            print(f"Saved cropped raw data for epoch {i + 1} ({sanitized_event_name}) to {npy_output_path}")
            
            topo_fig = cropped_raw.compute_psd(picks=eeg_channels, fmin=1, fmax=40).plot_topomap(
                ch_type="eeg",
                normalize=normalize,
                sensors=True, 
                mask=None, 
                mask_params=None, 
                contours=6, 
                outlines='head', 
                sphere=None, 
                image_interp='cubic',
                extrapolate='auto', 
                border='mean', 
                res=64, 
                size=1, 
                cmap='Spectral_r', 
                vlim=(None, None), 
                cnorm=None, 
                axes=None, 
                show=False, 
            )

            plt.title(f"{event_name}")
            topo_output_filename = f"{os.path.basename(edf_file).replace('.edf', '').replace('.bdf', '')}_epoch_{i + 1}_{sanitized_event_name}_psd_topomap.png"
            topo_output_path = os.path.join(subfolder_path, topo_output_filename)
            topo_fig.savefig(topo_output_path)
            plt.close(topo_fig)
            print(f"Saved PSD plot for epoch {i + 1} ({sanitized_event_name}) of {edf_file} to {topo_output_path}")

    except Exception as e:
        print(f"Error processing {edf_file}: {e}")

def find_edf_files(parent_directory):
    extensions = ['*.bdf', '*.edf', '*.edf+']
    edf_files = []
    for ext in extensions:
        edf_files.extend(glob.glob(os.path.join(parent_directory, '**', ext), recursive=True))
    return edf_files

def main(parent_directory, output_directory):
    edf_files = find_edf_files(parent_directory)

    for edf_file in edf_files:
        print(f"Processing file: {edf_file}")
        generate_plots(edf_file, output_directory)

if __name__ == '__main__':
    parent_directory = 'EDF+'
    
    timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
    timestamped_output_directory = os.path.join(output_directory, sanitize_filename(timestamp + description))
    os.makedirs(timestamped_output_directory, exist_ok=True)
    
    save_script_copy(__file__, timestamped_output_directory)
    
    main(parent_directory, timestamped_output_directory)
