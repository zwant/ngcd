import { createSelector } from 'reselect';
import { Map } from 'immutable';

const selectPipelineDetails = (state) => state.get('pipelineDetails');

const selectPipelineId = (_, props) => props.item.external_id;

const makeSelectPipelineDetailsFor = createSelector(
  [selectPipelineId, selectPipelineDetails],
  (pipelineId, pipelineState) => pipelineState.get(pipelineId, Map())
);

const makeSelectPipelineDetailsData = () => createSelector([makeSelectPipelineDetailsFor], (pipelineState) =>
    pipelineState.get('data')
  );

const makeSelectPipelineDetailsLoading = () => createSelector([makeSelectPipelineDetailsFor], (pipelineState) =>
    pipelineState.get('loading')
  );

const makeSelectPipelineDetailsLoadingError = () => createSelector([makeSelectPipelineDetailsFor], (pipelineState) =>
    pipelineState.get('error')
  );

export {
  makeSelectPipelineDetailsData,
  makeSelectPipelineDetailsLoading,
  makeSelectPipelineDetailsLoadingError,
};
