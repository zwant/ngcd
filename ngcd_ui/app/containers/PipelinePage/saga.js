/**
 * Gets the repositories of the user from Github
 */

import { call, put, takeLatest } from 'redux-saga/effects';
import { LOAD_PIPELINES } from 'containers/App/constants';
import { pipelinesLoaded, pipelineLoadingError } from 'containers/App/actions';

import request from 'utils/request';

/**
 * Github repos request/response handler
 */
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

/**
 * Root saga manages watcher lifecycle
 */
export default function* pipelineData() {
  // Watches for LOAD_REPOS actions and calls getRepos when one comes in.
  // By using `takeLatest` only the result of the latest API call is applied.
  // It returns task descriptor (just like fork) so we can continue execution
  // It will be cancelled automatically on component unmount
  yield takeLatest(LOAD_PIPELINES, getPipelines);
}
