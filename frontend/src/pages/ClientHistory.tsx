import React, { useEffect, useRef, useState } from 'react';
import { Container, Box, Typography, Button, IconButton, AppBar, Toolbar } from '@mui/material';
import { Home, Logout } from '@mui/icons-material';
import Chart from 'chart.js/auto';
import 'chartjs-adapter-date-fns';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchClientChoices, logout, fetchQuestions } from '../api/client';
import { Choice } from '../types';
interface Data {
  choices1: Choice[];
  choices2: Choice[];
}

const GraphComponent: React.FC<{ type: 'pre' | 'post' }> = ({ type }) => {
  const [data, setData] = useState<Choice[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [questions, setQuestions] = useState<{ [key: string]: string }>({});
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const { clientId } = useParams<{ clientId: string }>();

  const fetchQuestionsData = async () => {
    try {
      const questionsData = await fetchQuestions(type === 'pre' ? 'pre' : 'post');
      const questionsMap = questionsData.reduce((acc, item) => {
        acc[item.id] = item.text;
        return acc;
      }, {} as { [key: string]: string });
      setQuestions(questionsMap);
    } catch (error) {
      console.error('Error fetching questions:', error);
      setError('Failed to load questions');
    }
  };

  const fetchData = async () => {
    if (clientId) {
      try {
        const response = await fetchClientChoices(clientId);
        const choices = type === 'pre' ? response.choices1 : response.choices2;
        if (choices.length === 0) {
          setData([]);
          setError(`Нет данных`);
        } else {
          setData(choices.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()));
          setError(null);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('Failed to load data');
      }
    } else {
      setError('Client ID is missing');
    }
  };

  useEffect(() => {
    fetchQuestionsData();
    console.log(questions);
  }, []);

  useEffect(() => {
    fetchData();
  }, [clientId]);

  useEffect(() => {
    if (canvasRef.current && data.length > 0) {
      const datasets: { [key: string]: any } = {};
      const colors = [
        'rgba(255, 99, 132, 0.6)', 'rgba(54, 162, 235, 0.6)', 'rgba(255, 206, 86, 0.6)',
        'rgba(75, 192, 192, 0.6)', 'rgba(153, 102, 255, 0.6)', 'rgba(255, 159, 64, 0.6)'
      ];

      data.forEach((choice, index) => {
        if (!datasets[choice.question_id]) {
          datasets[choice.question_id] = {
            label: questions[choice.question_id] || `Question ${choice.question_id}`,
            data: [],
            backgroundColor: colors[index % colors.length],
            borderColor: colors[index % colors.length],
            borderWidth: 1
          };
        }
        datasets[choice.question_id].data.push({ x: choice.timestamp, y: choice.choice });
      });

      const chartData = { datasets: Object.values(datasets) };

      new Chart(canvasRef.current.getContext('2d')!, {
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
    }
  }, [data, questions]);

  return (
    <Box sx={{ flex: 1, mb: 4 }}>
      <Typography variant="h6">
        {type === 'pre' ? 'До сессии' : 'После сессии'}:
      </Typography>
      <Box sx={{ mb: 2 }}>
        {error ? <Typography color="error">{error}</Typography> : null}
      </Box>
      <Box sx={{ height: '40vh' }}>
        <canvas ref={canvasRef} style={{ width: '100%', height: '100%' }}></canvas>
      </Box>
    </Box>
  );
};

const ClientGraphs: React.FC = () => {
  const navigate = useNavigate();

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
        <GraphComponent type="pre" />
        <GraphComponent type="post" />
      </Box>
    </Container>
  );
};

export default ClientGraphs;
