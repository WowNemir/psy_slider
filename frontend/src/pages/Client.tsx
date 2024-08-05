import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { Container, Typography, Slider, Button, Box, FormControl, FormLabel } from '@mui/material';
import { fetchQuestions } from '../api/client';
interface Question {
    id: string;
    text: string;
}

const ClientPage: React.FC = () => {
    const { share_uid } = useParams<{ share_uid: string }>();
    const location = useLocation();
    const navigate = useNavigate();
    const [questions, setQuestions] = useState<Question[]>([]);
    const [formValues, setFormValues] = useState<Record<string, number>>({});
    const [loading, setLoading] = useState(true);
    const [showSliders, setShowSliders] = useState(false);
    const [isSubmitEnabled, setIsSubmitEnabled] = useState(false);

    const queryParams = new URLSearchParams(location.search);
    const queryType = queryParams.get('type') || 'default';

    useEffect(() => {
        const checkSubmissionStatus = async () => {
            try {
                const response = await fetch(`/client-page/${share_uid}?type=${queryType}`);
                if (response.ok) {
                    const data = await response.json();
                    if (data.completed) {
                        navigate('/thank-you');
                    } else {
                        setShowSliders(true);
                    }
                } else {
                    console.error('Error checking submission status:', response.statusText);
                }
            } catch (error) {
                console.error('Error checking submission status:', error);
            } finally {
                setLoading(false);
            }
        };

        checkSubmissionStatus();
    }, [share_uid, queryType, navigate]);
    useEffect(() => {
        if (showSliders) {
            const fetchAndSetQuestions = async () => {
                try {
                    // Ensure queryType is a string and does not contain unexpected values
                    const data = await fetchQuestions(queryType.trim());

                    if (Array.isArray(data)) {
                        setQuestions(data);
                    } else {
                        console.error('Unexpected data format:', data);
                        setQuestions([]);
                    }
                } catch (error) {
                    console.error('Error fetching questions:', error);
                    setQuestions([]);
                }
            };

            fetchAndSetQuestions();
        }
    }, [queryType, showSliders]);

    useEffect(() => {
        if (showSliders) {
            const areAllQuestionsAnswered = () => {
                return questions.every(({ id }) => formValues.hasOwnProperty(id));
            };
            setIsSubmitEnabled(areAllQuestionsAnswered());
        }
    }, [formValues, questions, showSliders]);

    const handleChange = (event: Event, newValue: number | number[], id: string) => {
        if (Array.isArray(newValue)) return;

        setFormValues(prev => ({ ...prev, [id]: newValue }));
    };

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        try {
            const formData = new FormData();
            for (const [question_id, value] of Object.entries(formValues)) {
                formData.append(question_id, value.toString());
            }

            const response = await fetch(window.location.href, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                console.log('Form submitted successfully');
                navigate('/thank-you');
            } else {
                console.error('Error submitting form:', response.statusText);
            }
        } catch (error) {
            console.error('Error submitting form:', error);
        }
    };

    if (loading) return <Typography>Loading...</Typography>;

    if (!showSliders) return null;

    return (
        <Container>
            <Typography variant="h4" gutterBottom>
                Здравствуйте!
            </Typography>
            <form id="questionForm" onSubmit={handleSubmit}>
                <Box mb={2}>
                    {questions.length > 0 ? (
                        questions.map(({ id, text }) => (
                            <FormControl fullWidth margin="normal" key={id}>
                                <FormLabel>{text}</FormLabel>
                                <Slider
                                    id={id}
                                    min={0}
                                    max={100}
                                    value={formValues[id] || 50}
                                    step={1}
                                    onChange={(event, newValue) => handleChange(event, newValue, id)}
                                    aria-labelledby={id}
                                />
                            </FormControl>
                        ))
                    ) : (
                        <Typography>No questions available</Typography>
                    )}
                </Box>
                <Button variant="contained" color="primary" type="submit" disabled={!isSubmitEnabled}>
                    Отправить
                </Button>
            </form>
        </Container>
    );
};

export default ClientPage;
