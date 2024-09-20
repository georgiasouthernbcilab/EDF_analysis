import os
import glob
import mne
from mne.preprocessing import ICA

parent_directory = "EDF+"
output_directory = "Preprocessed Files"
eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']
eog_channels=['Fp1', 'Fp2']

def grab_files(parent_directory):
    extensions = ['*.edf', '.edf+']
    edf_files = []
    for extension in extensions:
        edf_files.extend(glob.glob(os.path.join(parent_directory, '**', extension), recursive=True))
    return edf_files

def preprocessing(parent_directory, output_directory):
    edf_files = grab_files(parent_directory)
    for every_edf in edf_files:
        print(f"Preprocessing {every_edf}")
        raw = mne.io.read_raw_edf(every_edf, preload=True, infer_types=True, verbose=True)
        raw.pick(eeg_channels)
        montage = mne.channels.make_standard_montage('standard_1020')
        raw.set_montage(montage, on_missing='ignore')
        raw.set_eeg_reference(ref_channels = "average", projection=False, ch_type='eeg', verbose=False)
        raw.filter(l_freq=1, h_freq=40, picks=eeg_channels, n_jobs=4)
        ica = ICA(n_components=32, random_state=97, max_iter=800)
        ica.fit(inst=raw, picks=eeg_channels, tstep=2, verbose=False)
        eog_indices, eog_scores = ica.find_bads_eog(raw, ch_name = eog_channels, threshold=4, measure= 'zscore', verbose = False)
        muscle_noise_indices, muscle_noise_scores = ica.find_bads_muscle(inst =raw, threshold = 4, verbose =False)
        ica.exclude = list(set(eog_indices + muscle_noise_indices))
        raw_clean = ica.apply(raw.copy())
        
        
        relative_path = os.path.relpath(os.path.dirname(every_edf), parent_directory)
        output_path = os.path.join(output_directory, relative_path)
        os.makedirs(output_path, exist_ok=True)        
        output_fname = os.path.join(output_path, os.path.basename(every_edf).replace('.edf', '_preprocessed.fif'))
        raw_clean.save(output_fname, overwrite=True)
        print(f"Saved preprocessed file to {output_fname}")
        
        
preprocessing(parent_directory, output_directory)