import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const ThankYouPage: React.FC = () => {
    return (
        <Container
            maxWidth="xs"
            style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}
        >
            <Box textAlign="center">
                <Typography variant="h4" component="h1" gutterBottom>
                    Спасибо
                </Typography>
            </Box>
        </Container>
    );
};

export default ThankYouPage;
