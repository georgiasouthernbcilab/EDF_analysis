import React, { useState, useEffect } from 'react';
import './App.css';

function AboutEEG() {
    const [imagesLoaded, setImagesLoaded] = useState(false);

    useEffect(() => {
        const imageSources = [
            './example_eeg.png',
            './bad_electrode_contact.png',
            './the-10-10-system-new.png'
        ];

        const loadImages = imageSources.map(src => {
            return new Promise((resolve, reject) => {
                const img = new Image();
                img.src = src;
                img.onload = resolve;
                img.onerror = reject;
            });
        });

        Promise.all(loadImages)
            .then(() => setImagesLoaded(true))
            .catch(err => console.error('Failed to load images:', err));
    }, []);

    if (!imagesLoaded) {
        return <div className="text-white p-4">Loading...</div>;
    }

    return (
        <div className="flex flex-col items-center mt-4">
            <h1 className="text-4xl p-4 m-2">About EEG</h1>
            <div className="p-4 m-2 w-2/3">
                <p className="bg-[#FFF6F6] rounded p-2 break-words">
                    Electroencephalogram (EEG) is a method of measuring electrical activity in the brain by using small metal electrodes that attach to the scalp. It has been used extensively for the purpose of diagnosing medical conditions and for research purposes. Below is one example of a recorded EEG. This raw graph shows each channels voltage with respect to the point in time and the corresponding electrode.
                </p>
                <img src="/example_eeg.png" alt="Example EEG" className="w-full" />
                <p className="bg-[#FFF6F6] rounded p-2 break-words">
                    It&apos;s vital to ensure good contact quality with the scalp of the subject before recording begins. No amount of preprocessing or alterations made after the fact can reconstruct an initially bad signal into a good one. The first step is ensuring good contact quality and that the experimental setup eliminates any kind of motion artifacts. Within EEG, there are many kind of artifacts. These include: heartbeart, lateral eye movement, eye blinks, muscle movement, head movement, electrical interference, clenched jaw, touching the face, among many others. During any experimental setup these are critical to keep in perspective until data collection is complete. The more work done here to prevent these artifacts, the less work will be needed during the preprocessing stage. Below is an example of bad electrode contact with the scalp.
                </p>
                <img src="/bad_electrode_contact.png" alt="Bad Electrode Contact" className="w-full" />
                <p className="bg-[#FFF6F6] rounded p-2 break-words">
                    There are a lot of powerful tools out there made for analyzing EEG recordings such as MNE-Python and EEGLAB within MATLAB. There are also several different considerations that have to be made when considering the EEG headset being employed. In our case, we will be utilizing the <a href="https://emotiv.gitbook.io/epoc-flex-user-manual/epoc-flex/readme" target="_blank" className="text-[#598392]">Emotiv Flex 32-electrode system with saline sensors.</a> Please review the technical specifications and ensure that when you are working within your development environment that you match the sampling rate to the correct number. With this model, you can either record data at 128 samples per second or 256 if using the cable.
                </p>
                <br />
                <p className="bg-[#FFF6F6] rounded p-2 break-words">
                    To properly start the preprocessing stage, you&apos;ll need to understand electrode position conventions. Please review the <a href="https://en.wikipedia.org/wiki/10%E2%80%9320_system_(EEG)" target='_blank' className="text-[#598392]">10-20 system.</a> We will be working under the assumption of this principle and our analysis in MNE-Python will also adhere to the 10-20 system.
                </p>
                <img src="/the-10-10-system-new.png" alt="The 10-20 System" className="w-full mt-2" />
            </div>
        </div>
    );
}

export default AboutEEG;
