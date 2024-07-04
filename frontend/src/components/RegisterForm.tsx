import React, { useState } from 'react';
import './AuthForms.css';

const RegisterForm: React.FC = () => {
  const [newUsername, setNewUsername] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleRegisterSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (newPassword !== confirmPassword) {
      alert('Passwords do not match');
      return;
    }

    // Add your registration logic here
    console.log('New Username:', newUsername);
    console.log('New Password:', newPassword);

    // For example, send a POST request to your Flask backend
    fetch('/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ new_username: newUsername, new_password: newPassword }),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Success:', data);
        // Handle success (e.g., redirect, show a message)
      })
      .catch((error) => {
        console.error('Error:', error);
        // Handle error (e.g., show an error message)
      });
  };

  return (
    <div className="container">
      <h2>Зарегистрироваться</h2>
      <form onSubmit={handleRegisterSubmit}>
        <label htmlFor="new_username">New Username:</label>
        <input 
          type="text" 
          id="new_username" 
          name="new_username" 
          value={newUsername}
          onChange={(e) => setNewUsername(e.target.value)}
          required 
        />
        
        <label htmlFor="new_password">New Password:</label>
        <input 
          type="password" 
          id="new_password" 
          name="new_password" 
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required 
        />
        
        <label htmlFor="confirm_password">Confirm Password:</label>
        <input 
          type="password" 
          id="confirm_password" 
          name="confirm_password" 
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required 
        />
        
        <input type="submit" value="Register" className="fancy-button" />
      </form>
    </div>
  );
};

export default RegisterForm;