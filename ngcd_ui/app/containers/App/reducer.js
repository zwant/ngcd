/*
 * AppReducer
 *
 * The reducer takes care of our data. Using actions, we can change our
 * application state.
 * To add a new action, add it to the switch statement in the reducer function
 *
 * Example:
 * case YOUR_ACTION_CONSTANT:
 *   return state.set('yourStateVariable', true);
 */

import { fromJS } from 'immutable';

import {
  LOAD_PIPELINES_SUCCESS,
  LOAD_PIPELINES,
  LOAD_PIPELINES_ERROR,
} from './constants';

// The initial state of the App
const initialState = fromJS({
  loading: false,
  error: false,
  pipelines: false,
});

function appReducer(state = initialState, action) {
  switch (action.type) {
    case LOAD_PIPELINES:
      return state
        .set('loading', true)
        .set('error', false)
        .set('pipelines', false);
    case LOAD_PIPELINES_SUCCESS:
      return state
        .set('pipelines', action.pipelines)
        .set('loading', false);
    case LOAD_PIPELINES_ERROR:
      return state
        .set('error', action.error)
        .set('loading', false);
    default:
      return state;
  }
}

export default appReducer;
