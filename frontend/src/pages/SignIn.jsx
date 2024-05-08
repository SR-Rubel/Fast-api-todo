import { useState } from 'react';
import axios from 'axios';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import { ReactComponent as Logo } from 'assets/logo.svg';

export default function SignIn() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const submitHandler = (e) => {
    e.preventDefault();
    let formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    axios
      .post('/auth/login', formData)
      .then((response) => {
        console.log(response);
      })
      .catch((error) => {
        console.log(error);
      });
  };
  return (
    <div className="sign-in">
      <div className="logo">
        <Logo />
        <div className="label">Todo</div>
      </div>
      <div className="sign-in__container">
        <TextField
          onChange={(e) => {
            setEmail(e.target.value);
          }}
          variant="outlined"
          size="small"
          fullWidth="true"
          label="Username"
        />
        <TextField
          onChange={(e) => {
            setPassword(e.target.value);
          }}
          variant="outlined"
          size="small"
          fullWidth="true"
          label="Password"
          type="password"
        />
        <Button
          onClick={(e) => {
            submitHandler(e);
          }}
          variant="outlined"
        >
          Sign In
        </Button>
      </div>
    </div>
  );
}
