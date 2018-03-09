import {
  LOAD_PIPELINE_DETAILS,
  LOAD_PIPELINE_DETAILS_SUCCESS,
  LOAD_PIPELINE_DETAILS_ERROR,
} from './constants';

export function loadPipelineDetails(pipelineId) {
  return {
    type: LOAD_PIPELINE_DETAILS,
    pipelineId,
  };
}

export function pipelineDetailsLoaded(pipelineId, details) {
  return {
    type: LOAD_PIPELINE_DETAILS_SUCCESS,
    pipelineId,
    details,
  };
}

export function pipelineDetailsLoadingError(pipelineId, error) {
  return {
    type: LOAD_PIPELINE_DETAILS_ERROR,
    pipelineId,
    error,
  };
}
