import hljs from "highlight.js";
import python from 'highlight.js/lib/languages/python';
import { useEffect } from "react";
import { Link } from "react-router-dom";




hljs.registerLanguage('python', python);


function Preprocessing() {

    useEffect(() => {
        hljs.highlightAll();
    }, [])

    return (
        <>
         <div className = "flex flex-col items-center mt-4">
            <h1 className = "text-4xl p-4 m-2">Preprocessing</h1>
            <div className = "p-4 m-2 w-2/3">
            <p className = "mt-10 mb-5">Preprocessing steps can vary depending on your needs, but for general EEG cleanup there are some steps that should always be taken. First, we should import all the essentials for data preprocessing. For the sake of simplicity you can search for how to install these libraries.</p> 
            <pre><code className="language-python">
{`import mne
from mne.preprocessing import ICA
import matplotlib.pyplot as plt
import numpy as np`}
            </code></pre>
            <p className = "mt-10 mb-5">After installing the libraries, we create a list of all the EEG channels and the specific EOG channels. In this case, we are familiar with sites Fp1 and Fp2 being most closely associated with ocular information.</p>
            <pre><code className="language-python">
{`eeg_channels = ['Cz', 'Fz', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5', 'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1', 'Pz', 'Oz', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6', 'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2']
eog_channels=['Fp1', 'Fp2']`}
            </code></pre>
            <p className = "mt-10 mb-5">After establishing the sites we&apos;re going to analyze, we can start utilizing MNE-Python. They have a powerful function to read the EDF format which is much more versatile than the CSV alternative.</p>
            <pre><code className="language-python">
            {
                `# Read your EDF file
raw = mne.io.read_raw_edf(r'EDF+\Zacker\Zacker.edf', preload=True, infer_types=True)

# Select only EEG channels
raw.pick(eeg_channels)  # Explicitly pick EEG channels to avoid picking other channels
print(raw.info)`
            }
            </code></pre>
            <p className = "mt-10 mb-5">
                Afterwards, let&apos;s set the 10-20 montage so that MNE knows what kind of setup we&apos;re working with.
            </p>
            <pre><code>
                {`# Set montage
montage = mne.channels.make_standard_montage('standard_1020')
raw.set_montage(montage, on_missing='ignore')`}
            </code></pre>
            <p className = "mt-10 mb-5">Now we will set the average reference. If this does not make sense, look more into EEG referencing and its purpose. We also apply a band-pass filter which in this case cuts off frequencies below 1 Hz and above 40 Hz. Afterwards, we call the method on the raw object: <span className = "text-red-50 bg-[#282c34] p-1 rounded">raw.plot</span> to plot the raw EEG recording.</p>
            <pre><code>{`raw.set_eeg_reference('average', ch_type = 'eeg')  # Setting EEG average reference, NOTE: must be applied later!
raw.filter(l_freq=1, h_freq=40)  # Apply band-pass filtering
raw.plot(picks=eeg_channels,block=True)`}</code></pre>
                <p className = "mt-10 mb-5">The next step is to initialize (ICA) Independent Component Analysis and then fit it to our data. The number of components can make the computation time go up. MNE recommends a cutoff frequency of 1 Hz for <a href="https://mne.tools/stable/generated/mne.preprocessing.ICA.html#mne.preprocessing.ICA" target="_blank" className = "text-[#598392]">this.</a></p>
                <pre><code>{`ica = ICA(n_components=n_components, random_state=97, max_iter=800)
ica.fit(inst = raw, picks = eeg_channels, tstep = 2, verbose = False)
eog_indices, scores = ica.find_bads_eog(raw, ch_name=['Fp1', 'Fp2'])
ica.exclude = eog_indices
raw_clean = ica.apply(raw.copy())`}</code></pre>
                <p className = "mt-10 mb-5">Next, we will perform interpolation. A method of restoring noisy channels by averaging the other channels around them. This generally works well and when it can be applied its advised to use it. We make a copy of the raw object of the EEG data in order to show before and afters later on when we do more detailed analysis.</p>
                <pre><code>{`raw_interpolated = raw.copy().interpolate_bads(method='spline')# NOTE: Reset bads = false keeps the bads within the data, just a different color.`}</code></pre>
                
                <p className = "mt-10 mb-5">Now we will perform power spectral density analysis on our data. Use <span className = "text-red-50 bg-[#282c34] p-1 rounded">plt.show()</span> to ensure the plot does not disappear.</p>
                <pre><code>{`raw.compute_psd().plot(picks="data", exclude="bads", amplitude=False)
plt.show()`}</code></pre>
                <p className = "mt-10 mb-5">That is the basics of preprocessing and using some of MNE-Python&apos;s suite of tools. They are powerful and versatile if you get familiar with them. Of course, this analyzes the entire recording. In most cases, we want to look at a more specific piece of time. We will explore this in Preprocessing 2.</p>

                <Link to ="/Preprocessing_2" className="text-[#598392] mb-10">Next Preprocessing Page</Link>
            </div>
         </div>
        </>
    )
}


export default Preprocessing;