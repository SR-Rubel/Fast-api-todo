import { Provider } from 'react-redux';
import axios from 'axios';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Home from 'pages/Home';
import SignIn from 'pages/SignIn';
import store from 'redux/store';
import 'styles/style.scss';
import SignUp from 'pages/SignUp';
import { useNavigate } from 'react-router-dom'
import { useDispatch } from 'react-redux'
import { setLoggedIn } from 'redux/actions/AppAction'
import { useEffect } from 'react';
import ProtectedRoute from 'components/AuthRequired';
import ResetPassword from 'pages/ResetPassword';

axios.defaults.baseURL = 'http://127.0.0.1:8000/api/v1';
axios.defaults.withCredentials = true;

const router = createBrowserRouter([
  {
    path: '/',
    element: <ProtectedRoute><Home/></ProtectedRoute>
  },
  {
    path: 'sign-up',
    element: <SignUp />
  },
  {
    path: 'sign-in',
    element: <SignIn />
  },
  {
    path: 'reset-password',
    element: <ResetPassword />
  },
]);

function App() {
  const dispatch = useDispatch()

  useEffect(() => {
    axios
      .get('/auth/profile')
      .then((response) => {
        if (response.status === 200) {
          setProfile(response.data)
          dispatch(setLoggedIn(true))
        }
      })
      .catch((error) => {
        console.log(error);
      });
  })

  return (
    <RouterProvider router={router} /> // RouterProvider should be wrapped inside the Provider
  );
}

const WrappedApp = () => (
  <Provider store={store}>
    <App />
  </Provider>
);

export default WrappedApp;