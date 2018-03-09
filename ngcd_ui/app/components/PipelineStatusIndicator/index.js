import React from 'react';
import PropTypes from 'prop-types';
import SuccessAvatar from './SuccessAvatar';
import FailureAvatar from './FailureAvatar';
import AbortedAvatar from './AbortedAvatar';
import UnknownAvatar from './UnknownAvatar';
import RunningAvatar from './RunningAvatar';

export class PipelineStatusIndicator extends React.PureComponent {
  // eslint-disable-line react/prefer-stateless-function
  getAvatar(running, result) {
    if (running === true) {
      return <RunningAvatar />;
    }
    switch (result) {
      case 'SUCCESS':
        return <SuccessAvatar />;
      case 'FAILURE':
        return <FailureAvatar />;
      case 'ABORTED':
        return <AbortedAvatar />;
      default:
        return <UnknownAvatar />;
    }
  }

  render() {
    const { running, result } = this.props;

    return this.getAvatar(running, result);
  }
}
// this.getAvatar(running, result)

PipelineStatusIndicator.propTypes = {
  running: PropTypes.bool,
  result: PropTypes.string,
};

export default PipelineStatusIndicator;
