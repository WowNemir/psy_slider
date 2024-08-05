import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Route, Routes} from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import AdminDashboard from './pages/AdminDashboard';
import AddClient from './pages/AddClient';
import ClientPage from './pages/Client';
import ThankYouPage from './pages/ThankYou';
import ClientGraphs from './pages/ClientHistory'; // Import the new component

function App() {
  return ( 
    <>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/admin-dashboard" element={<AdminDashboard />} />
        <Route path="/add-client" element={<AddClient />} />
        <Route path="/client-page/:share_uid" element={<ClientPage />} />
        <Route path="/client-history/:clientId" element={<ClientGraphs />} />
        <Route path="/thank-you/" element={<ThankYouPage />} />
      </Routes>
    </>
  );
}

export default App;
