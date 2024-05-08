import { useEffect, useState } from 'react';
import axios from 'axios';
import { useDispatch, useSelector } from 'react-redux';
import BottomNav from 'components/BottomNav';
import TaskContainer from 'components/TaskContainer';
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

  useEffect(() => {
    axios
      .get('/')
      .then((response) => {
        console.log(response);
      })
      .catch((error) => {
        console.log(error);
      });
  }, []);

  return (
    <div className="home">
      {isLoading ? (
        <div>loading....</div>
      ) : (
        <>
          {isSearching && <Loader />}
          <BottomNav />
          <TaskContainer />
        </>
      )}
    </div>
  );
}

export default Home;
