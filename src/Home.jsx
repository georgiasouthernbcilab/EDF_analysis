

function Home() {
    return (
        <>
        <div className = "flex flex-col items-center mt-6">
            <h1 className = "text-4xl">Welcome to the Georgia Southern BCI Lab Homepage!</h1>
            <p className = "mt-10">To get started, please visit the MNE introductory <a href="https://mne.tools/stable/auto_tutorials/intro/index.html" target="_blank" className="text-[#598392] ">tutorial</a> and familiarize yourself with the content.</p>
            <p className = "">If you need to install MNE-Python, please refer to their <a href="https://mne.tools/stable/install/index.html" target="_blank" className="text-[#598392] ">installation page.</a></p>
            <h2 className = "text-2xl mt-10">At the time of these tutorials, we were using Python 3.12.8 and version 1.7.1 of MNE-Python.</h2>
            <img src="./georgia-southern-eagles3289.jpg" alt="Georgia Southern Logo"  className="w-1/3"/>
            <h2 className = "text-3xl">Roadmap for BCI Lab Documentation future:</h2>
            <ul className = "list-disc mt-2"><li>Finish the About EEG content section</li><li>Overhaul the preprocessing tab to include better instructions and more explanations.</li><li>Create an EEG Pipeline for different analysis goals.</li><li>Discuss more complex topics such as ICA in depth and how they work to produce cleaner recordings.</li><li>More code examples for specific cases.</li></ul>

        </div>
        </>
    )
}

export default Home;