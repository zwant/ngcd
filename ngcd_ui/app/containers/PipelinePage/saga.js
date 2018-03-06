/**
 * Gets the repositories of the user from Github
 */

import { call, put, takeLatest, all} from 'redux-saga/effects';
import { LOAD_PIPELINES } from 'containers/App/constants';
import { LOAD_PIPELINE_DETAILS } from 'containers/PipelineListItem/constants';
import { pipelinesLoaded, pipelineLoadingError } from 'containers/App/actions';
import { pipelineDetailsLoaded, pipelineDetailsLoadingError } from 'containers/PipelineListItem/actions';


import request from 'utils/request';

export function* getPipelines() {
  const requestURL = 'http://localhost:5001/pipeline/';
  try {
    // Call our request helper (see 'utils/request')
    const pipelines = yield call(request, requestURL);
    yield put(pipelinesLoaded(pipelines.pipelines));
  } catch (err) {
    yield put(pipelineLoadingError(err));
  }
}

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
export default function* root() {
  yield all([
    takeLatest(LOAD_PIPELINES, getPipelines),
    takeLatest(LOAD_PIPELINE_DETAILS, getPipelineDetails)
  ]);
}
