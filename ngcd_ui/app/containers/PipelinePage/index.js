/**
 *
 * PipelinePage
 *
 */

import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { createStructuredSelector } from 'reselect';
import { compose } from 'redux';

import PageTitle from 'components/PageTitle';
import PipelineList from 'components/PipelineList';
import {
  makeSelectPipelines,
  makeSelectLoading,
  makeSelectError,
} from 'containers/App/selectors';
import injectSaga from 'utils/injectSaga';
import { loadPipelines } from '../App/actions';
import saga from './saga';

class PipelinePage extends React.PureComponent {
  // eslint-disable-line react/prefer-stateless-function
  componentWillMount() {
    this.props.loadPipelines();
  }

  render() {
    const { loading, error, pipelines } = this.props;
    const pipelinesListProps = {
      loading,
      error,
      pipelines,
    };
    return (
      <div>
        <PipelineList {...pipelinesListProps} />
      </div>
    );
  }
}

PipelinePage.propTypes = {
  loading: PropTypes.bool,
  error: PropTypes.oneOfType([PropTypes.object, PropTypes.bool]),
  pipelines: PropTypes.oneOfType([PropTypes.array, PropTypes.bool]),
  loadPipelines: PropTypes.func,
};

export function mapDispatchToProps(dispatch) {
  return {
    loadPipelines: () => dispatch(loadPipelines()),
  };
}

const mapStateToProps = createStructuredSelector({
  pipelines: makeSelectPipelines(),
  loading: makeSelectLoading(),
  error: makeSelectError(),
});

const withConnect = connect(mapStateToProps, mapDispatchToProps);
const withSaga = injectSaga({ key: 'pipelinePage', saga });

export default compose(withSaga, withConnect)(PipelinePage);
