import { useNavigate } from "react-router-dom";
import { Button, Box } from "@mui/material";

const Home = () => {
    const navigate = useNavigate();

    return (
        <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            minHeight="100vh"
        >
            <Button
                variant="contained"
                onClick={() => navigate('/login')}
                sx={{ mb: 2 }}
            >
                Login
            </Button>
            <Button
                variant="contained"
                onClick={() => navigate('/register')}
            >
                Register
            </Button>
        </Box>
    );
};

export default Home;
