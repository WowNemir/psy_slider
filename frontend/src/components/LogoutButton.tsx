import React from 'react';
import { Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { logout } from '../api/client';

const LogoutButton: React.FC = () => {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      localStorage.removeItem('token');
    } catch (error) {
      console.error('Failed to logout', error);
    }
    navigate('/login');
  };

  return (
    <Button variant="contained" onClick={handleLogout}>Logout</Button>
  );
};

export default LogoutButton;
