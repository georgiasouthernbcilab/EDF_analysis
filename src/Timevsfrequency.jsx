import hljs from "highlight.js";
import python from 'highlight.js/lib/languages/python';
import { useEffect } from "react";
import * as data from "./json_content/Timevsfrequency.json";

//DO NOT USE. Template for setting up new pages.

hljs.registerLanguage('python', python);

function Timevsfrequency() {

    
    useEffect(() => {
        hljs.highlightAll();
    }, [])

    return(
        <>
        <div className = "flex flex-col items-center mt-4">
            <h1 className = "text-4xl p-4 m-2">Time vs Frequency Domain</h1>
            <div className = "p-4 m-2 w-2/3">
            <p className = "bg-[#FFF6F6] rounded p-2 break-words mt-10 mb-5">{data.pOne}</p> 
            <img src="./Spectrogram.png" alt="Spectrogram" className="w-full"/>
            <p className = "bg-[#FFF6F6] rounded p-2 break-words mt-10 mb-5">{data.pTwo}</p> 
            <img src="./psd.png" alt="PSD" className="w-full"/>
            <p className = "bg-[#FFF6F6] rounded p-2 break-words mt-10 mb-5">{data.pThree}</p> 
            <img src="./Bands.png" alt="bands" className="w-full"/>
            <pre><code className="language-python">{`frequency_bands = {\n"Delta":(0, 4), \n"Theta":(4, 8), \n"Alpha":(8, 12), \n"Beta":(12, 30), \n"Gamma":(30, 40)\n}`}</code></pre>
            </div>
        </div>
        </>
    )
}

export default Timevsfrequency;