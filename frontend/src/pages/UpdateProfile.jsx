import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import { ReactComponent as Logo } from 'assets/logo.svg';
import ToastContainer from 'components/ToastContainer';
import Heading from 'components/Heading';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import axios from 'axios';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { toast } from 'redux/actions/TodoAction';
import { TOAST_TYPE_ERROR, TOAST_TYPE_SUCCESS } from 'utils/constants';
import { setProfile } from 'redux/actions/AppAction';

export default function UpdateProfile() {
  const [email, setEmail] = useState(null);
  const [fullName, setFullName] = useState('');
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const submitHandler = (e) => {
    e.preventDefault();
    axios
      .post('/auth/update-profile', { email: email, full_name: fullName })
      .then((response) => {
        if (response.status == 200) {
          dispatch(toast({ type: TOAST_TYPE_SUCCESS, message: 'Profile updated!' }));
          dispatch(setProfile(response.data));
          navigate('/profile');
        }
      })
      .catch((error) => {
        dispatch(toast({ type: TOAST_TYPE_ERROR, message: 'Invalid credentials!' }));
        console.log(error);
      });
  };
  return (
    <div className="sign-up">
      <ToastContainer />
      <Heading />
      <Box
        sx={{
          width: '100vw',
          height: '100vh',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          marginTop: '-10rem'
        }}
      >
        <Card
          sx={{
            display: 'flex',
            flexDirection: 'column',
            textAlign: 'center',
            alignItems: 'center',
            gap: '4rem',
            padding: '2rem'
          }}
        >
          <Box sx={{ display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flex: '1 0 auto' }}>
              <div className="logo">
                <Logo />
                <div className="label">Todo</div>
              </div>
              <div className="sign-in__container">
                <TextField
                  onChange={(e) => {
                    setFullName(e.target.value);
                  }}
                  variant="outlined"
                  size="small"
                  fullWidth="true"
                  label="Full Name"
                />
                <TextField
                  onChange={(e) => {
                    setEmail(e.target.value);
                  }}
                  variant="outlined"
                  size="small"
                  fullWidth="true"
                  label="Email"
                />
                <Button
                  onClick={(e) => {
                    submitHandler(e);
                  }}
                  variant="outlined"
                >
                  Update
                </Button>
              </div>
            </CardContent>
          </Box>
        </Card>
      </Box>
    </div>
  );
}
