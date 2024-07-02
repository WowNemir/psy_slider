import React from 'react';
import './AuthForms.css';

const AuthForms: React.FC = () => {
  return (
    <div className="container">
      <form action="/login" method="get">
        <input type="submit" value="Войти" className="fancy-button" />
      </form>

      <form action="/register" method="get">
        <input type="submit" value="Зарегистрироваться" className="fancy-button" />
      </form>
    </div>
  );
};

export default AuthForms;
