import { createSelector } from 'reselect';
import { Map } from 'immutable';

const selectPipelineDetails = (state) =>
  state.get('pipelineDetails');

const selectPipelineId = (_, props) =>
  props.item.external_id;

const makeSelectPipelineDetailsFor = createSelector(
    [ selectPipelineId, selectPipelineDetails ],
    (pipelineId, pipelineState) => {
      return pipelineState.get(pipelineId, Map())
    }
  );

const makeSelectPipelineDetailsData = () => {
  return createSelector(
    [ makeSelectPipelineDetailsFor ],
    (pipelineState) => pipelineState.get('data')
  )
};

const makeSelectPipelineDetailsLoading = () => {
  return createSelector(
    [ makeSelectPipelineDetailsFor ],
    (pipelineState) => pipelineState.get('loading')
  )
};

const makeSelectPipelineDetailsLoadingError = () => {
  return createSelector(
    [ makeSelectPipelineDetailsFor ],
    (pipelineState) => pipelineState.get('error')
  )
};


export {
  makeSelectPipelineDetailsData,
  makeSelectPipelineDetailsLoading,
  makeSelectPipelineDetailsLoadingError
};
