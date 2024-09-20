import os
import glob
import mne
import matplotlib.pyplot as plt
import re

# Parameters
apply_proj = False

eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7',
                'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10',
                'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2',
                'F4', 'F8', 'Fp2']
eog_channels = ['Fp1', 'Fp2']

def get_emotion_from_video_name(video_name):
    """Function to get the emotion associated with a video name."""
    emotion_mapping = {
        "excited": ["kenMiles", "motorsports", "NBA", "sport", "ratatChaseScene"],
        "happy": ["scooby"],
        "motivated": ["motivationalAuthor"],
        "relaxed": ["meditation", "waterfall", "asmr"],
        "sad": ["saddogs", "sadBaby1", "ChampDeath"],
        "horror": ["conjuring"],
        "disgusted": ["trainspotting"],
        "angry": ["angrydogs", "thepiano"]
    }
    for emotion, videos in emotion_mapping.items():
        if video_name in videos:
            return emotion
    return "unknown"  # Default if no emotion is found

def sanitize_filename(filename):
    """Sanitize the filename to remove or replace invalid characters."""
    return re.sub(r'[\\/*?:"<>|,]', '_', filename)

def generate_basic_psd_plots(fif_file):
    """Generate basic PSD plots from preprocessed FIF files and display them."""
    try:
        # Load the preprocessed .fif file
        raw_clean = mne.io.read_raw_fif(fif_file, preload=True, verbose=False)

        # Get events from annotations
        events, event_dict = mne.events_from_annotations(raw_clean, regexp='^(?=.*videos)(?!.*neutralVideo)')

        for i, event in enumerate(events):
            event_id = event[-1]
            event_name = list(event_dict.keys())[list(event_dict.values()).index(event_id)]
            event_name_match = re.search(r'\\([^\\]+)\.(mp4|mkv)', event_name)
            if event_name_match:
                event_name = event_name_match.group(1)
            else:
                event_name = event_name  # Use the original name if no match

            # Define the time window for cropping
            start = event[0] / raw_clean.info['sfreq'] + 15
            stop = start + 44

            emotion = get_emotion_from_video_name(event_name)
            sanitized_event_name = sanitize_filename(event_name)

            try:
                cropped_raw = raw_clean.copy().crop(tmin=start, tmax=stop)
            except Exception as e:
                print(f"Error cropping data for {event_name}: {e}")
                continue

            # Compute the PSD
            psd = cropped_raw.compute_psd(fmin=1, fmax=40, picks='eeg').plot(dB=True)
            
            # Plot the PSD
            psd.suptitle(f"PSD Plot ({sanitized_event_name}) - Emotion: {emotion}", fontsize=10)
            plt.show()
            plt.close(psd)

    except Exception as e:
        print(f"Error processing {fif_file}: {e}")

def find_fif_files(parent_directory):
    """Find all preprocessed FIF files in the given directory."""
    return glob.glob(os.path.join(parent_directory, '**', '*_preprocessed.fif'), recursive=True)

def main(parent_directory):
    fif_files = find_fif_files(parent_directory)
    for fif_file in fif_files:
        print(f"Processing file: {fif_file}")
        generate_basic_psd_plots(fif_file)

if __name__ == '__main__':
    parent_directory = 'Preprocessed Files'  # Directory containing preprocessed .fif files
    main(parent_directory)
