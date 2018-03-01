import {
  LOAD_PIPELINES,
  LOAD_PIPELINES_SUCCESS,
  LOAD_PIPELINES_ERROR,
} from './constants';

/**
 * Load the repositories, this action starts the request saga
 *
 * @return {object} An action object with a type of LOAD_REPOS
 */
export function loadPipelines() {
  return {
    type: LOAD_PIPELINES,
  };
}

/**
 * Dispatched when the repositories are loaded by the request saga
 *
 * @param  {array} pipelines The pipeline data
 *
 * @return {object}      An action object with a type of LOAD_PIPELINES_SUCCESS passing the repos
 */
export function pipelinesLoaded(pipelines) {
  return {
    type: LOAD_PIPELINES_SUCCESS,
    pipelines,
  };
}

/**
 * Dispatched when loading the repositories fails
 *
 * @param  {object} error The error
 *
 * @return {object}       An action object with a type of LOAD_PIPELINES_ERROR passing the error
 */
export function pipelineLoadingError(error) {
  return {
    type: LOAD_PIPELINES_ERROR,
    error,
  };
}
