// src/App.tsx
import React from 'react';
import AuthForms from './components/AuthForms';
import './App.css'; // Add your global styles if necessary

const App: React.FC = () => {
  return (
    <div className="App">
      <AuthForms />
    </div>
  );
};

export default App;
