import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Box } from "@mui/material";
import { LoginButton } from "@telegram-auth/react";
import axios, { AxiosResponse } from "axios";


const API_URL = '/api/v1';


const Home = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Dynamically load the Telegram WebApp script
    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-web-app.js?56";
    script.async = true;
    script.onload = () => {
      const telegramWebApp = (window as any).Telegram?.WebApp;

      if (telegramWebApp) {
        const data = telegramWebApp.initData;

        // Only call the backend if initData is not empty
        if (data) {
          console.log("Telegram initData:", data);
          sendDataToBackend(data).then((success) => {
            if (success) {
              navigate("/admin-dashboard");
            }
          });
        } else {
          console.warn("Telegram initData is empty, skipping backend call.");
        }
      }
    };
    script.onerror = () => {
      console.error("Failed to load Telegram WebApp script.");
    };
    document.body.appendChild(script);

    // Cleanup script on unmount
    return () => {
      document.body.removeChild(script);
    };
  }, [navigate]);

  const sendDataToBackend = async (data: any): Promise<Boolean> => {
    const response = await axios.post(`${API_URL}/auth/telegram`, {
      headers: {
        "skip_zrok_interstitial": "true",
      },
      body: data,
    });
    const token = response.data.access_token;

    localStorage.setItem("token", token);
    return true;
      
  };

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="100vh"
    >
      {/* Navigation Buttons */}
      <Button variant="contained" onClick={() => navigate("/login")} sx={{ mb: 2 }}>
        Login
      </Button>
      <Button variant="contained" onClick={() => navigate("/register")} sx={{ mb: 2 }}>
        Register
      </Button>

      {/* Telegram Login Button */}
      <LoginButton
        botUsername="PsySliderBot"
        onAuthCallback={(data) => {
          if (data) {
            sendDataToBackend(data).then((res) => {
              if (res) {
                navigate("/admin-dashboard");
              }
            });
          } else {
            console.warn("Telegram User Data is empty, skipping backend call.");
          }
        }}
      />
    </Box>
  );
};

export default Home;
