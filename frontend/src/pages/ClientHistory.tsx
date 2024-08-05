import React, { useEffect, useRef, useState } from 'react';
import { Container, Box, Typography, Button, IconButton, AppBar, Toolbar } from '@mui/material';
import { Home, Logout } from '@mui/icons-material';
import Chart from 'chart.js/auto';
import 'chartjs-adapter-date-fns';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchClientChoices, logout } from '../api/client';
import { Choice } from '../types'; // Import Choice type

interface Data {
  choices1: Choice[];
  choices2: Choice[];
}

const ClientGraphs: React.FC = () => {
  const { clientId } = useParams<{ clientId: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<Data | null>(null);
  const [error, setError] = useState<string | null>(null);

  const chartRef1 = useRef<HTMLCanvasElement | null>(null);
  const chartRef2 = useRef<HTMLCanvasElement | null>(null);

  const fetchData = async () => {
    if (clientId) {
      try {
        console.log(`Fetching data for clientId: ${clientId}`);
        const response = await fetchClientChoices(clientId);
        console.log('API Response:', response); // Log the API response
  
        const choices1 = response.choices1 || []; // First array in the response
        const choices2 = response.choices2 || []; // Second array in the response
  
        if (choices1.length === 0 && choices2.length === 0) {
          setData(null);
          setError('No data available for this client.');
        } else {
          choices1.sort((a: Choice, b: Choice) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
          choices2.sort((a: Choice, b: Choice) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
          setData({ choices1, choices2 });
          setError(null);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('Failed to load data');
      }
    } else {
      console.error('clientId is not available');
      setError('Client ID is missing');
    }
  };

  useEffect(() => {
    if (clientId) {
      fetchData();
    }
  }, [clientId]);

  useEffect(() => {
    if (data) {
      if (data.choices1) {
        processData(data.choices1, chartRef1.current);
      }
      if (data.choices2) {
        processData(data.choices2, chartRef2.current);
      }
    }
  }, [data]);

  const processData = (data: Choice[], canvasElement: HTMLCanvasElement | null) => {
    if (!canvasElement) return;
  
    const datasets: { [key: string]: any } = {};
    const colors = [
      'rgba(255, 99, 132, 0.6)', 'rgba(54, 162, 235, 0.6)', 'rgba(255, 206, 86, 0.6)',
      'rgba(75, 192, 192, 0.6)', 'rgba(153, 102, 255, 0.6)', 'rgba(255, 159, 64, 0.6)'
    ];
  
    data.forEach((choice, index) => {
      if (!datasets[choice.question_id]) {
        datasets[choice.question_id] = {
          label: `Question ${choice.question_id}`,
          data: [],
          backgroundColor: colors[index % colors.length],
          borderColor: colors[index % colors.length],
          borderWidth: 1
        };
      }
      datasets[choice.question_id].data.push({ x: choice.timestamp, y: choice.choice });
    });
  
    const chartData = { datasets: Object.values(datasets) };
  
    new Chart(canvasElement.getContext('2d')!, {
      type: 'line',
      data: chartData,
      options: {
        maintainAspectRatio: false,
        responsive: true,
        scales: {
          x: { type: 'time', time: { unit: 'day' }, ticks: { maxRotation: 0 } },
          y: { suggestedMin: 0, suggestedMax: 100, beginAtZero: true }
        }
      }
    });
  };

  const handleHome = () => navigate('/admin-dashboard');
  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  return (
    <Container>
      <AppBar position="static">
        <Toolbar>
          <IconButton edge="start" color="inherit" onClick={handleHome}>
            <Home />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Client Graphs
          </Typography>
          <Button color="inherit" onClick={handleLogout}>
            <Logout /> Logout
          </Button>
        </Toolbar>
      </AppBar>
      <Box sx={{ mt: 4, display: 'flex', flexDirection: 'column', height: '80vh' }}>
        <Typography variant="h4" gutterBottom>
          Graphs for {/* Client name */}
        </Typography>
        {error && <Typography color="error">{error}</Typography>}
        {data ? (
          <>
            <Box sx={{ flex: 1, mb: 4 }}>
              <Typography variant="h6">Before Session:</Typography>
              <Box sx={{ mb: 2 }}>
                <ul>
                  {data.choices1.length > 0 ? (
                    data.choices1.map((choice, index) => (
                      <li key={index}>{`Question ${choice.question_id}: ${choice.timestamp} - ${choice.choice}`}</li>
                    ))
                  ) : (
                    <Typography>No data available for before the session.</Typography>
                  )}
                </ul>
              </Box>
              <Box sx={{ height: '40vh' }}>
                <canvas ref={chartRef1} style={{ width: '100%', height: '100%' }}></canvas>
              </Box>
            </Box>
            <Box sx={{ flex: 1, mb: 4 }}>
              <Typography variant="h6">After Session:</Typography>
              <Box sx={{ mb: 2 }}>
                <ul>
                  {data.choices2.length > 0 ? (
                    data.choices2.map((choice, index) => (
                      <li key={index}>{`Question ${choice.question_id}: ${choice.timestamp} - ${choice.choice}`}</li>
                    ))
                  ) : (
                    <Typography>No data available for after the session.</Typography>
                  )}
                </ul>
              </Box>
              <Box sx={{ height: '40vh' }}>
                <canvas ref={chartRef2} style={{ width: '100%', height: '100%' }}></canvas>
              </Box>
            </Box>
          </>
        ) : (
          <Typography>No data available for this client.</Typography>
        )}
      </Box>
    </Container>
  );
};

export default ClientGraphs;
