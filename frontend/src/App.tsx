import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import AuthForms from '.components/AuthForms';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

ReactDOM.render(
  <Router>
    <Switch>
      <Route exact path="/" component={AuthForms} />
      <Route path="/login" component={LoginForm} />
      <Route path="/register" component={RegisterForm} />
    </Switch>
  </Router>,
  document.getElementById('root')
);
