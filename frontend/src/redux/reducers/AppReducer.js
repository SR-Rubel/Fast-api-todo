import { appActionTypes } from '../constants/ActionTypes';

const { SET_LOGGED_IN } = appActionTypes
const initialState = {
  isLoggedIn: false
};

export const appReducer = (state = initialState, action) => {
  switch (action.type) {
    case SET_LOGGED_IN:
      return {
        ...state,
        isLoggedIn: action.payload
      };
    default:
      return state;
  }
};
