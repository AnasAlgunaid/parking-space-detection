import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css"; // Import the CSS file

function App() {
  const [parkingData, setParkingData] = useState({
    total: 0,
    free: 0,
    occupied: 0,
    spaces: [],
  });

  useEffect(() => {
    // Fetch parking data every 5 seconds
    const fetchData = async () => {
      try {
        const response = await axios.get("http://localhost:8000/status");
        setParkingData(response.data);
      } catch (error) {
        console.error("Error fetching parking data:", error);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      <header className="header">
        <h1>Parking Dashboard</h1>
      </header>
      <main className="main-content">
        <div className="stats">
          <div className="stat">
            <h2>Total Spaces</h2>
            <p>{parkingData.total}</p>
          </div>
          <div className="stat">
            <h2>Free Spaces</h2>
            <p className="free">{parkingData.free}</p>
          </div>
          <div className="stat">
            <h2>Occupied Spaces</h2>
            <p className="occupied">{parkingData.occupied}</p>
          </div>
        </div>
      </main>
      <footer className="footer">
        <p>&copy; 2024 Parking Management System</p>
      </footer>
    </div>
  );
}

export default App;
