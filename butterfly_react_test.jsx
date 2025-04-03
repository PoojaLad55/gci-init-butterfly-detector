// App.jsx
import React, { useEffect } from 'react';
import './App.css';

function App() {
  // Handle overscroll in a React-friendly way
  useEffect(() => {
    // This is a more targeted approach to prevent overscroll on iOS
    const handleTouchMove = (e) => {
      // Only prevent default if at the boundary of scrollable content
      // This allows normal scrolling within content
      if (window.scrollY === 0 && e.touches[0].screenY > e.touches[0].clientY ||
          window.scrollY + window.innerHeight >= document.body.scrollHeight && 
          e.touches[0].screenY < e.touches[0].clientY) {
        e.preventDefault();
      }
    };

    // Add the event listener
    document.addEventListener('touchmove', handleTouchMove, { passive: false });

    // Clean up the event listener when component unmounts
    return () => {
      document.removeEventListener('touchmove', handleTouchMove);
    };
  }, []);

  return (
    <div className="butterfly-garden">
      <div className="top-bar">
        main
      </div>
      <div className="content">
        {/* Your actual content goes here instead of relying on a large body height */}
        {/* For example: */}
        <div className="section">Butterfly Garden Content</div>
        <div className="section">More content...</div>
        {/* Add as many sections as needed */}
      </div>
    </div>
  );
}

export default App;
