import React from 'react';
import blue from 'material-ui/colors/blue';
import PipelineStatusAvatar from './PipelineStatusAvatar';

export class RunningAvatar extends React.PureComponent {
  // eslint-disable-line react/prefer-stateless-function
  render() {
    return (
      <PipelineStatusAvatar
        title="Running"
        backgroundColor={blue[500]}
        iconName="directions_run"
      />
    );
  }
}

export default RunningAvatar;
