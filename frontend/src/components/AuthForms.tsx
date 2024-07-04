// AuthForms.tsx
import React from 'react';
import { useHistory } from 'react-router-dom';
import './AuthForms.css';

const AuthForms: React.FC = () => {
  const history = useHistory();

  const handleLoginClick = () => {
    history.push('/login');
  };

  const handleRegisterClick = () => {
    history.push('/register');
  };

  return (
    <div className="container">
      <button onClick={handleLoginClick} className="fancy-button">
        Войти
      </button>

      <button onClick={handleRegisterClick} className="fancy-button">
        Зарегистрироваться
      </button>
    </div>
  );
};

export default AuthForms;
