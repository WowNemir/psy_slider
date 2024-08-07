import React, { useEffect, useRef, useState } from 'react';
import { Box, Typography } from '@mui/material';
import Chart from 'chart.js/auto';
import 'chartjs-adapter-date-fns';
import { fetchClientChoices, fetchQuestions } from '../api/client';
import { Choice } from '../types';
import { useParams } from 'react-router-dom';

interface GraphComponentProps {
  type: 'pre' | 'post';
}

const GraphComponent: React.FC<GraphComponentProps> = ({ type }) => {
  const [data, setData] = useState<Choice[]>([]);
  const [questions, setQuestions] = useState<{ [key: string]: string }>({});
  const [error, setError] = useState<string | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const { clientId } = useParams<{ clientId: string }>();

  const fetchQuestionsData = async () => {
    try {
      const questionType = type === 'pre' ? 'before' : 'after';
      const questionsData = await fetchQuestions(questionType);
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
          setError(`No data available for ${type === 'pre' ? 'before' : 'after'} the session.`);
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
  }, [type]);

  useEffect(() => {
    fetchData();
  }, [clientId, type]);

  useEffect(() => {
    if (canvasRef.current && data.length > 0 && Object.keys(questions).length > 0) {
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
        {type === 'pre' ? 'Before Session' : 'After Session'}:
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

export default GraphComponent;
