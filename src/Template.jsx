import hljs from "highlight.js";
import python from 'highlight.js/lib/languages/python';
import { useEffect } from "react";


//DO NOT USE. Template for setting up new pages.

hljs.registerLanguage('python', python);

function Template() {

    
    useEffect(() => {
        hljs.highlightAll();
    }, [])

    return(
        <>
        <div className = "flex flex-col items-center mt-4">
            <h1 className = "text-4xl p-4 m-2">Template</h1>
            <div className = "p-4 m-2 w-2/3">
            <p className = "bg-[#FFF6F6] rounded p-2 break-words mt-10 mb-5"></p> 
            <pre><code className="language-python">{`print("hello")`}</code></pre>
            </div>
        </div>
        </>
    )
}

export default Template;