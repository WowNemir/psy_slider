import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Box, Typography, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Avatar } from '@mui/material';
import { LockOutlined } from "@mui/icons-material";
import '../components/AdminDashboard.css'; // Ensure you have corresponding CSS

interface Client {
  id: string;
  name: string;
  activeSession: boolean;
}

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate(); // Get the navigate function from react-router-dom
  const [clients, setClients] = useState<Client[]>([]);
  const [username, setUsername] = useState<string>('Admin');

  useEffect(() => {
    // Fetch clients and user info here
    // setClients(data.clients);
    // setUsername(data.username);
  }, []);

  const handleLogout = () => {
    // Handle logout logic
    navigate('/login');
  };

  const handleAddClient = () => {
    navigate("/add-client"); // Navigate to the add-client route
  };

  const copyToClipboard = (clientPageUrl: string, clientId: string, button: HTMLButtonElement) => {
    // Copy to clipboard logic
  };

  const startSession = (clientId: string, button: HTMLButtonElement) => {
    // Start session logic
  };

  const finishSession = (clientId: string, button: HTMLButtonElement) => {
    // Finish session logic
  };

  return (
    <Container>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Avatar sx={{ bgcolor: 'primary.main' }}>
            <LockOutlined />
          </Avatar>
          <Typography variant="h6" sx={{ ml: 2 }}>{username}</Typography>
        </Box>
        <Button variant="contained" onClick={handleLogout}>
          Logout
        </Button>
      </Box>
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" gutterBottom>Клиенты:</Typography>
        <Button variant="contained" onClick={handleAddClient} sx={{ mb: 2 }}>
          Добавить клиента
        </Button>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Имя</TableCell>
                <TableCell>Графики</TableCell>
                <TableCell>Ссылка с ползунком</TableCell>
                <TableCell>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {clients.map(client => (
                <TableRow key={client.id}>
                  <TableCell>{client.name}</TableCell>
                  <TableCell>
                    <Button href={`/client-history/${client.id}`} variant="outlined">
                      Посмотреть
                    </Button>
                  </TableCell>
                  <TableCell>
                    {client.activeSession ? (
                      <>
                        <Button
                          onClick={(e) => copyToClipboard(`/client-page/${client.id}?type=pre`, client.id, e.currentTarget as HTMLButtonElement)}
                          variant="outlined"
                        >
                          До сессии
                        </Button>
                        <Button
                          onClick={(e) => copyToClipboard(`/client-page/${client.id}?type=post`, client.id, e.currentTarget as HTMLButtonElement)}
                          variant="outlined"
                        >
                          После сессии
                        </Button>
                      </>
                    ) : (
                      <>
                        <Button disabled variant="outlined">До сессии</Button>
                        <Button disabled variant="outlined">После сессии</Button>
                      </>
                    )}
                  </TableCell>
                  <TableCell>
                    {client.activeSession ? (
                      <Button
                        onClick={(e) => finishSession(client.id, e.currentTarget as HTMLButtonElement)}
                        variant="outlined"
                      >
                        Завершить сессию
                      </Button>
                    ) : (
                      <Button
                        onClick={(e) => startSession(client.id, e.currentTarget as HTMLButtonElement)}
                        variant="outlined"
                      >
                        Начать сессию
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Container>
  );
};

export default AdminDashboard;
