import { createSelector } from 'reselect';

const selectPipelineDetails = (state, props) => {
  state.getIn(['pipelineDetails', props.item.external_id, 'data']);
}

export {
  selectPipelineDetails,
};
