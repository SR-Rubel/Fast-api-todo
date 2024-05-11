import { useEffect, useState } from 'react';
import axios from 'axios';
import Button from '@mui/material/Button';
import Popover from '@mui/material/Popover';
import PopupState, { bindTrigger, bindPopover } from 'material-ui-popup-state';
import { ReactComponent as UserIcon } from 'assets/user.svg';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { setLoggedIn } from 'redux/actions/AppAction'


export default function Profile() {
  const [profile, setProfile] = useState({});
  const isLoggedIn = useSelector((state) => state.appStates.isLoggedIn)
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const location = useLocation()

  const logout = (e) => {
    e.preventDefault();
    axios
      .get('/auth/logout')
      .then((res) => {
        console.log(res)
        if (res.status == 200) {
          console.log(res.status)
          dispatch(setLoggedIn(false))
        }
      })
      .catch((err) => {
        console.log(err);
      });
  };

  useEffect(() => {
    axios
      .get('/auth/profile')
      .then((response) => {
        if (response.status === 200) {
          setProfile(response.data)
          dispatch(setLoggedIn(true))
        };
      })
      .catch((error) => {
        console.log(error);
      });
  }, []);

  return (
    <PopupState variant="popover" popupId="demo-popup-popover">
      {(popupState) => (
        <div className="profile">
          <Button variant="contained" {...bindTrigger(popupState)}>
            <UserIcon />
          </Button>
          <Popover
            {...bindPopover(popupState)}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'left'
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'left'
            }}
          >
            {
              isLoggedIn ? 
            (<div className="profile__container">
              {profile.username}
              <Button onClick={(e) => logout(e)} color="error">
                Logout
              </Button>
                </div>) :
                <Button onClick={() => navigate('/sign-in', { replace: true, state: { from: location } })}>SignIn</Button>
            }
          </Popover>
        </div>
      )}
    </PopupState>
  );
}
