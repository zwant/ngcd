
import { Map } from 'immutable';

import {
  LOAD_PIPELINE_DETAILS_SUCCESS,
  LOAD_PIPELINE_DETAILS,
  LOAD_PIPELINE_DETAILS_ERROR,
} from './constants';


const initialState = Map();

function pipelineListItemReducer(state = initialState, action) {
  const pipelineState = state.get(action.pipelineId, Map());

  switch (action.type) {
    case LOAD_PIPELINE_DETAILS:
      return state
        .set(action.pipelineId,
             pipelineState
               .set('loading', true)
               .set('error', false)
            );
    case LOAD_PIPELINE_DETAILS_SUCCESS:
      return state
        .set(action.pipelineId,
             pipelineState
               .set('data', action.details)
               .set('loading', false)
            );
    case LOAD_PIPELINE_DETAILS_ERROR:
      return state
        .set(action.pipelineId,
             pipelineState
               .set('loading', false)
               .set('error', true)
            );
    default:
      return state;
  }
}

export default pipelineListItemReducer;
