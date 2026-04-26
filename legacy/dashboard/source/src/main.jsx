import React from "react"; // Import React
import { createRoot } from "react-dom/client"; // Création du DOM React
import "./index.css"; // Import des styles globaux
import App from "./App"; // Import du composant principal

// Obtenir l'élément root
const rootElement = document.getElementById("root");
if (rootElement) {
  createRoot(rootElement).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}
