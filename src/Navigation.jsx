import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import './App.css';

function Navigation() {
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const dropdownRef = useRef(null);

    const toggleDropdown = () => {
        setDropdownOpen(!dropdownOpen);
    };

    const closeDropdown = () => {
        setDropdownOpen(false);
    };

    const handleClickOutside = (event) => {
        if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
            closeDropdown();
        }
    };

    useEffect(() => {
        document.addEventListener('click', handleClickOutside);
        document.addEventListener('scroll', closeDropdown);
        
        return () => {
            document.removeEventListener('click', handleClickOutside);
            document.removeEventListener('scroll', closeDropdown);
        };
    }, []);

    return (
        <div className="flex bg-[#01161E] text-white p-4">
            <h2 className="m-2"><Link to="/">Home</Link></h2>
            <h2 className="m-2"><Link to="/About_EEG">About EEG</Link></h2>
            <ul className="flex space-x-4 relative" ref={dropdownRef}>
                <li className="relative">
                    <button
                        className="text-white px-4 py-2"
                        onClick={toggleDropdown}
                    >
                        Preprocessing
                    </button>
                    {dropdownOpen && (
                        <div
                            className="absolute bg-white text-black mt-1 rounded-md shadow-lg"
                        >
                            <Link to="/Preprocessing" className="block px-4 py-2 hover:bg-gray-200" onClick={closeDropdown}>Basic Preprocessing</Link>
                            <Link to="/Preprocessing_2" className="block px-4 py-2 hover:bg-gray-200" onClick={closeDropdown}>Preprocessing 2</Link>
                            <Link to="/Preprocessing_3" className="block px-4 py-2 hover:bg-gray-200" onClick={closeDropdown}>Preprocessing 3</Link>
                        </div>
                    )}
                </li>
            </ul>
        </div>
    );
}

export default Navigation;
