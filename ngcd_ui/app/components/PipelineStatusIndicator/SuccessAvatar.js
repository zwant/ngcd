import React from 'react';
import green from 'material-ui/colors/green';
import PipelineStatusAvatar from './PipelineStatusAvatar';

export class SuccessAvatar extends React.PureComponent {
  // eslint-disable-line react/prefer-stateless-function
  render() {
    return (
      <PipelineStatusAvatar
        title="Success"
        backgroundColor={green[500]}
        iconName="done"
      />
    );
  }
}

export default SuccessAvatar;
