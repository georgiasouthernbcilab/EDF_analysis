import React from 'react';
import ReactDOM from 'react-dom/client';
import {
  createHashRouter,
  RouterProvider,
} from 'react-router-dom';
import Navigation from './Navigation.jsx';
import AboutEEG from './AboutEEG.jsx';
import Preprocessing from './Preprocessing.jsx';
import 'highlight.js/styles/atom-one-dark.css';
import Home from './Home.jsx';
import Preprocessing_2 from './Preprocessing_2.jsx';
import Preprocessing_3 from './Preprocessing_3.jsx';

// Create a hash router
const router = createHashRouter([
  {
    path: "/",
    element: (
      <>
        <Navigation />
        <Home />
      </>
    ),
  },
  {
    path: "/About_EEG",
    element: (
      <>
        <Navigation />
        <AboutEEG />
      </>
    ),
  },
  {
    path: "/Preprocessing",
    element: (
      <>
        <Navigation />
        <Preprocessing />
      </>
    ),
  },
  {
    path: "/Preprocessing_2",
    element: (
      <>
        <Navigation />
        <Preprocessing_2 />
      </>
    ),
  },
  {
    path: "/Preprocessing_3",
    element: (
      <>
        <Navigation />
        <Preprocessing_3 />
      </>
    ),
  },
]);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
