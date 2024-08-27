import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import './App.css';
import Dropdown from "./Dropdown";

function Navigation() {

    return (
        <div className="flex bg-[#01161E] text-white p-4">
            <h2 className="m-2"><Link to="/">Home</Link></h2>
            <Dropdown linkNames = {["/About_EEG"]} linkTitles = {["Introduction"]} navName = {"About EEG"}/>
            <Dropdown linkNames = {["/Preprocessing", "/Preprocessing_2", "/Preprocessing_3"]} linkTitles = {["Basic Preprocessing", "Preprocessing 2", "Preprocessing 3"]} navName = {"Preprocessing"}/>
        </div>
    );
}

export default Navigation;
