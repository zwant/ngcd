import React from 'react';
import PropTypes from 'prop-types';

import List from 'components/List';
import ListItem from 'components/ListItem';
import LoadingIndicator from 'components/LoadingIndicator';
import PipelineListItem from 'containers/PipelineListItem';

function PipelineList({ loading, error, pipelines }) {
  if (loading) {
    return <List component={LoadingIndicator} />;
  }

  if (error !== false) {
    const ErrorComponent = () => (
      <ListItem item={'Something went wrong, please try again!'} />
    );
    return <List component={ErrorComponent} />;
  }

  if (pipelines !== false) {
    return <List items={pipelines} component={PipelineListItem} />;
  }

  return null;
}

PipelineList.propTypes = {
  loading: PropTypes.bool,
  error: PropTypes.any,
  pipelines: PropTypes.any,
};

export default PipelineList;
