import AdminRoute from 'components/AdminRoute';
import ProtectedRoute from 'components/AuthRequired';
import FullProfile from 'components/FullProfile';
import DashboardLayout from 'layouts/dashboard';
import ChangePassword from 'pages/ChangePassword';
import Home from 'pages/Home';
import ResetPassword from 'pages/ResetPassword';
import SendResetLink from 'pages/SendResetLink';
import SignIn from 'pages/SignIn';
import SignUp from 'pages/SignUp';
import UpdateProfile from 'pages/UpdateProfile';
import { lazy, Suspense } from 'react';
import { Navigate, Outlet, useRoutes } from 'react-router-dom';

export const IndexPage = lazy(() => import('pages/app'));
export const UserPage = lazy(() => import('pages/user'));
export const Page404 = lazy(() => import('pages/page-not-found'));

// ----------------------------------------------------------------------

export default function Router() {
  const routes = useRoutes([
    {
      element: (
        <DashboardLayout>
          <Suspense>
            <Outlet />
          </Suspense>
        </DashboardLayout>
      ),
      children: [
        {
          path: 'dashboard',
          element: (
            <AdminRoute>
              {' '}
              <IndexPage />{' '}
            </AdminRoute>
          )
        },
        {
          path: 'user',
          element: (
            <AdminRoute>
              {' '}
              <UserPage />{' '}
            </AdminRoute>
          )
        }
      ]
    },
    {
      path: '/',
      element: (
        <ProtectedRoute>
          <Home />
        </ProtectedRoute>
      )
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
      element: <ProtectedRoute><ResetPassword /></ProtectedRoute>
    },
    {
      path: 'change-password',
      element: <ProtectedRoute><ChangePassword /></ProtectedRoute>
    },
    {
      path: 'profile',
      element: <ProtectedRoute><FullProfile /></ProtectedRoute>
    },
    {
      path: 'update-profile',
      element: <ProtectedRoute><UpdateProfile /></ProtectedRoute>
    },
    {
      path: 'send-reset-link',
      element: <ProtectedRoute><SendResetLink /></ProtectedRoute>
    },
    {
      path: '404',
      element: <Page404 />
    },
    {
      path: '*',
      element: <Navigate to="/404" replace />
    }
  ]);

  return routes;
}
