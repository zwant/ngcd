import React from 'react';
import red from 'material-ui/colors/red';
import PipelineStatusAvatar from './PipelineStatusAvatar';

export class FailureAvatar extends React.PureComponent {
  // eslint-disable-line react/prefer-stateless-function
  render() {
    return (
      <PipelineStatusAvatar
        title="Failed"
        backgroundColor={red[500]}
        iconName="error_outline"
      />
    );
  }
}

export default FailureAvatar;
