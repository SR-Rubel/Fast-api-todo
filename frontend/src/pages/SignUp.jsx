import * as React from 'react';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import { ReactComponent as Logo } from 'assets/logo.svg';
import ToastContainer from 'components/ToastContainer';
import Heading from 'components/Heading';

export default function SignUp() {
  return (
    <div className="sign-up">
      <ToastContainer />
      <Heading />
      <div className="logo">
        <Logo />
        <div className="label">Todo</div>
      </div>
      <div className="sign-in__container">
        <TextField variant="outlined" size="small" fullWidth="true" label="Full Name" />
        <TextField variant="outlined" size="small" fullWidth="true" label="Email" />
        <TextField
          variant="outlined"
          size="small"
          fullWidth="true"
          label="Password"
          type="password"
        />
        <Button variant="outlined">Sign Up</Button>
      </div>
    </div>
  );
}
