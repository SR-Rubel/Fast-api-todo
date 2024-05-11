export const actionTypes = {
  ADD_TODO: 'ADD_TODO',
  EDIT_TODO: 'EDIT_TOD',
  DELETE_TODO: 'DELETE_TODO',
  SET_ADD_TASK: 'SET_ADD_TASK',
  COMPLETE_TASK: 'COMPLETE_TASK',
  SET_EDIT: 'SET_EDIT',
  NEXT_PAGE: 'NEXT_PAGE',
  TOAST_MESSAGE: 'TOAST_MESSAGE',
  LOAD_TASKS_FROM_DB: 'LOAD_TASKS_FROM_DB'
};

export const paginationActionTypes = {
  LOAD_MORE: 'LOAD_MORE'
};

export const filterActionTypes = {
  SET_FILTER: 'SET_FILTER',
  ALL: 'All',
  INCOMPLETE: 'Incomplete',
  COMPLETE: 'Complete'
};

export const searchActionTypes = {
  SET_SEARCH: 'SET_SEARCH',
  SET_SEARCHING: 'SET_SEARCHING'
};

export const appActionTypes = {
  SET_LOGGED_IN: 'SE_LOGGED_IN'
};
