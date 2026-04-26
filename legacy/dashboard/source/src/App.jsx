import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import "./App.css";
import Dashboard from "./components/Dashboard"; // Import direct du composant Dashboard

const WelcomePage = () => {
  return (
    <div className="welcome-container">
      <h1>Neural Stock Exchange</h1>
      <p>Local workspace for the Neural Stock Exchange dashboard.</p>
      {/* Bouton stylisé avec un lien vers le dashboard */}
      <Link to="/dashboard">
        <button className="admin-access-button">Admin Access</button>
      </Link>
    </div>
  );
};

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<WelcomePage />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  );
};

export default App;
