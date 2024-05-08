import propTypes from 'prop-types';
import axios from 'axios';
import Heading from 'components/Heading';
import ToastContainer from 'components/ToastContainer';

axios.defaults.baseURL = 'http://127.0.0.1:8000/api/v1';

function AppLayout({ children = null }) {
  return (
    <div className="app">
      <ToastContainer />
      <Heading />
      {children}
    </div>
  );
}

export default AppLayout;

AppLayout.propTypes = {
  children: propTypes.node
};
