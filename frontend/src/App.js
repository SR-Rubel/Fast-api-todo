import { Provider } from 'react-redux';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Home from 'pages/Home';
import SignIn from 'pages/SignIn';
import store from 'redux/store';
import AppLayout from 'pages/AppLayout';
import 'styles/style.scss';
import SignUp from 'pages/SignUp';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Home />
  },
  {
    path: 'sign-up',
    element: <SignUp />
  },
  {
    path: 'sign-in',
    element: <SignIn />
  }
]);

function App() {
  return (
    <Provider store={store}>
      <AppLayout>
        <RouterProvider router={router} />
      </AppLayout>
    </Provider>
  );
}

export default App;
