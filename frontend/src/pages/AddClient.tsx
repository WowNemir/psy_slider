import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Avatar,
  CssBaseline,
  AppBar,
  Toolbar,
  IconButton,
} from '@mui/material';
import { Home, LockOutlined } from '@mui/icons-material';
import axios from "axios";

const AddClient: React.FC = () => {
  const navigate = useNavigate();
  const [name, setName] = useState<string>('');

  const handleAddClient = async (event: React.FormEvent) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append('name', name);
    
    const response = await axios.post(
      'api/v1/clients',
      formData,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    navigate('/admin-dashboard');
  };
  const handleHome = () => {
    navigate('/admin-dashboard');
  };

  const handleLogout = () => {
    navigate('/login');
  };

  return (
    <Container component="main" maxWidth="xs">
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <IconButton edge="start" color="inherit" onClick={handleHome}>
            <Home />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Add Client
          </Typography>
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Avatar sx={{ m: 1, bgcolor: 'primary.main' }}>
          <LockOutlined />
        </Avatar>
        <Typography component="h1" variant="h5">
          Add Client
        </Typography>
        <Box component="form" onSubmit={handleAddClient} sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="name"
            label="Имя"
            name="name"
            autoFocus
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Введите имя клиента"
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
          >
            Добавить Клиента
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default AddClient;
