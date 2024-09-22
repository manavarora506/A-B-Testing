import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import FormA from './components/FormA';
import FormB from './components/FormB';
import AdminPanel from './components/AdminPanel';
import RedirectToSite from './components/RedirectToSite'; // Import the RedirectToSite component

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Use element instead of component */}
          <Route path="/site-a" element={<FormA />} />
          <Route path="/site-b" element={<FormB />} />
          <Route path="/admin" element={<AdminPanel />} />

          {/* Home route redirects based on routing probability */}
          <Route path="/" element={<RedirectToSite />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
