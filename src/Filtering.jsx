import hljs from "highlight.js";
import python from 'highlight.js/lib/languages/python';
import { useEffect } from "react";
import * as data from "./json_content/Filtering.json";




hljs.registerLanguage('python', python);

function Filtering() {

    
    useEffect(() => {
        hljs.highlightAll();
    }, [])

    return(
        <>
        <div className = "flex flex-col items-center mt-4">
            <h1 className = "text-4xl p-4 m-2">Filtering</h1>
            <div className = "p-4 m-2 w-2/3">
            <p className = "bg-[#FFF6F6] rounded p-2 break-words mt-10 mb-5">{data.pOne}</p> 
            <pre><code className="language-python">{`raw.filter(l_freq=1.0, h_freq=40)`}</code></pre>
            </div>
        </div>
        </>
    )
}

export default Filtering;