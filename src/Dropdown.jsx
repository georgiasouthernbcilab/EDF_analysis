import { useState, useEffect, useRef} from "react";
import { Link } from "react-router-dom";

useState

function Dropdown({linkNames, linkTitles, navName}) {
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const dropdownRef = useRef(null);

    function toggleDropdown() {
        setDropdownOpen(!dropdownOpen);
    }

    function closeDropdown() {
        setDropdownOpen(false);
    }

    function handleClickOutside(event) {
        if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
            closeDropdown();
        }
    }

    useEffect(() => {
        document.addEventListener('click', handleClickOutside);
        document.addEventListener('scroll', closeDropdown);
        
        return () => {
            document.removeEventListener('click', handleClickOutside);
            document.removeEventListener('scroll', closeDropdown);
        };
    }, []);

    return (
        <ul className="flex space-x-4 relative" ref={dropdownRef}>
        <li className="relative">
            <button className="text-white px-4 py-2" onClick={toggleDropdown}>
                {navName}
            </button>
            {dropdownOpen && (
                <div className="absolute bg-white text-black mt-1 rounded-md shadow-lg">
                    {linkNames.map((link, index) => (
                        <Link to={link} key = {index} className="block px-4 py-2 hover:bg-gray-200" onClick={closeDropdown}>{linkTitles[index]}</Link>
                    ))}
                </div>
            )}
        </li>
        </ul>
    )
}

export default Dropdown;