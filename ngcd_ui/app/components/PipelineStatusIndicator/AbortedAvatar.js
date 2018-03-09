import React from 'react';
import orange from 'material-ui/colors/orange';
import PipelineStatusAvatar from './PipelineStatusAvatar';

export class AbortedAvatar extends React.PureComponent {
  // eslint-disable-line react/prefer-stateless-function
  render() {
    return (
      <PipelineStatusAvatar
        title="Aborted"
        backgroundColor={orange[500]}
        iconName="highlight_off"
      />
    );
  }
}

export default AbortedAvatar;
