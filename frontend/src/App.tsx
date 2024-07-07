import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Route, Routes} from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import AdminDashboard from './pages/AdminDashboard';
import AddClient from './pages/AddClient';


function App() {
  return ( 
  <>
  <Routes>
    <Route path="/" element={<Home />} />
    <Route path="/login" element={<Login />} />
    <Route path="/register" element={<Register />} />
    <Route path="/admin-dashboard" element={<AdminDashboard />} />
    <Route path="/add-client" element={<AddClient />} />
  </Routes>
  </>
  );
}

export default App;