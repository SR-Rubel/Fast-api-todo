import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import BottomNav from 'components/BottomNav';
import ToastContainer  from 'components/ToastContainer';
import TaskContainer  from 'components/TaskContainer';
import Heading from 'components/Heading';
import Loader from 'components/ui/Loader';
import { loadTasksFromDB, toast } from 'redux/actions/TodoAction';
import supabase from 'supabase';

function Home() {
  const isSearching = useSelector((state) => state.searchStates.searching);
  const dispatch = useDispatch();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchTasks() {
      let { data, error } = await supabase
        .from('todos')
        .select()
        .order('createdAt', { ascending: false });

      if (!error) {
        dispatch(loadTasksFromDB(data));
        setIsLoading(false);
      } else {
        dispatch(toast({ type: 'danger', message: 'something wrong. Try again later' }));
      }
    }

    fetchTasks();
  }, []);

  return (
    <div className="home">
      {isLoading ? (
        <div>loading....</div>
      ) : (
        <>
          {isSearching && <Loader />}
          <ToastContainer />
          <Heading />
          <BottomNav />
          <TaskContainer />
        </>
      )}
    </div>
  );
}

export default Home;
