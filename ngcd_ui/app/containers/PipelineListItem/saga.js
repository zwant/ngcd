import { call, put, takeLatest } from 'redux-saga/effects';
import { LOAD_PIPELINE_DETAILS } from './constants';
import { pipelineDetailsLoaded, pipelineDetailsLoadingError } from './actions';

import request from 'utils/request';

/**
 * Github repos request/response handler
 */
export function* getPipelineDetails(action) {
  const pipelineId = action.pipelineId;
  const requestURL = `http://localhost:5001/pipeline/${pipelineId}`;
  try {
    // Call our request helper (see 'utils/request')
    const pipelineDetails = yield call(request, requestURL);
    yield put(pipelineDetailsLoaded(pipelineId, pipelineDetails));
  } catch (err) {
    yield put(pipelineDetailsLoadingError(pipelineId, err));
  }
}

/**
 * Root saga manages watcher lifecycle
 */
export default function* pipelineDetailsData() {
  yield takeLatest(LOAD_PIPELINE_DETAILS, getPipelineDetails);
}
