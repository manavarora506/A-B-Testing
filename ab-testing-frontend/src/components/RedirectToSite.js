// components/RedirectToSite.js
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function RedirectToSite() {
  const navigate = useNavigate();

  useEffect(() => {
    const fetchRouting = async () => {
      try {
        const response = await fetch('http://localhost:8000/route');
        const data = await response.json();
        if (data.site === 'A') {
          navigate('/site-a');
        } else {
          navigate('/site-b');
        }
      } catch (error) {
        console.error('Error fetching routing:', error);
        // Handle error (e.g., redirect to a default page or show an error message)
      }
    };

    fetchRouting();
  }, [navigate]);

  return <div>Loading...</div>; // Show a loading message or spinner
}

export default RedirectToSite;
