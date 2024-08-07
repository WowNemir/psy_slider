import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, Box, Typography, Button, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Avatar, Dialog, DialogTitle, DialogContent, DialogActions, Snackbar
} from '@mui/material';
import { LockOutlined } from "@mui/icons-material";
import { fetchClients, handleSession, deleteClient } from '../api/client';
import { Client } from '../types/index';
import LogoutButton from '../components/LogoutButton'; // Import from components

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [clients, setClients] = useState<Client[]>([]);
  const [deleteClientId, setDeleteClientId] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [openSnackbar, setOpenSnackbar] = useState<boolean>(false);

  const getClients = async () => {
    setLoading(true);
    setError(null);
    try {
      const clients = await fetchClients();
      setClients(clients);
    } catch (error) {
      console.error('Failed to fetch clients', error);
      setError('Failed to fetch clients.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    getClients();
  }, []);

  const handleSessionButtonClick = async (client: Client, sessionId: string | null) => {
    console.log('loggin client info')
    console.log(client)
    try {
      await handleSession(client.id, sessionId);
      await getClients();
    } catch (error) {
      console.error(`Failed to ${sessionId ? 'finish' : 'start'} session`, error);
    }
  };

  const deleteSelectedClient = async () => {
    if (!deleteClientId) return;
    try {
      await deleteClient(deleteClientId);
      setClients(clients.filter(client => client.id !== deleteClientId));
      setDeleteClientId(null);
    } catch (error) {
      console.error(`Failed to delete client with ID ${deleteClientId}`, error);
      alert('Failed to delete client. Please try again.');
    }
  };

  const handleCopyClientPage = (client: Client, type: string) => {
    const url = `${window.location.origin}/client-page/${client.activeSession?.share_uid}?type=${type}`;
    navigator.clipboard.writeText(url);
    setOpenSnackbar(true);
  };

  return (
    <Container>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Avatar sx={{ bgcolor: 'primary.main' }}>
            <LockOutlined />
          </Avatar>
          <Typography variant="h6" sx={{ ml: 2 }}>Admin</Typography>
        </Box>
        <LogoutButton />
      </Box>
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" gutterBottom>Клиенты:</Typography>
        <Button variant="contained" onClick={() => navigate("/add-client")} sx={{ mb: 2 }}>Добавить клиента</Button>
        {loading && <Typography>Loading...</Typography>}
        {error && <Typography color="error">{error}</Typography>}
        {!loading && !error && (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Имя</TableCell>
                  <TableCell>Графики</TableCell>
                  <TableCell>Ссылка для клиента</TableCell>
                  <TableCell>Действия</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {clients.length > 0 ? clients.map(client => (
                  <TableRow key={client.id}>
                    <TableCell>{client.name}</TableCell>
                    <TableCell><Button href={`/client-history/${client.id}`} variant="outlined">Посмотреть</Button></TableCell>
                    <TableCell>
                      {['pre', 'post'].map(type => (
                        <Button
                          key={type}
                          onClick={() => handleCopyClientPage(client, type)}
                          variant="outlined"
                          disabled={!client.activeSession}
                        >
                          {type === 'pre' ? 'До сессии' : 'После сессии'}
                        </Button>
                      ))}
                    </TableCell>
                    <TableCell>
                      <Button
                        onClick={() => handleSessionButtonClick(client, client.activeSession?.id || null)}
                        variant="outlined"
                      >
                        {client.activeSession ? 'Завершить сессию' : 'Начать сессию'}
                      </Button>
                      <Button
                        onClick={() => setDeleteClientId(client.id)}
                        variant="outlined"
                        sx={{ ml: 1, color: 'error.main', borderColor: 'error.main' }}
                      >
                        Удалить клиента
                      </Button>
                    </TableCell>
                  </TableRow>
                )) : (
                  <TableRow>
                    <TableCell colSpan={4} align="center">Нет клиентов</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>
      <Dialog open={!!deleteClientId} onClose={() => setDeleteClientId(null)}>
        <DialogTitle>Подтверждение удаления</DialogTitle>
        <DialogContent>
          <Typography variant="body1">Вы уверены, что хотите удалить этого клиента?</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteClientId(null)} color="primary">Отмена</Button>
          <Button onClick={deleteSelectedClient} color="error" variant="contained">Удалить</Button>
        </DialogActions>
      </Dialog>
      <Snackbar
        message="Copied to clipboard"
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        autoHideDuration={2000}
        onClose={() => setOpenSnackbar(false)}
        open={openSnackbar}
      />
    </Container>
  );
};

export default AdminDashboard;
