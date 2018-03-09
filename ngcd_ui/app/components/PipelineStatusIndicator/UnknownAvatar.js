import React from 'react';
import red from 'material-ui/colors/red';
import PipelineStatusAvatar from './PipelineStatusAvatar';

export class UnknownAvatar extends React.PureComponent {
  // eslint-disable-line react/prefer-stateless-function
  render() {
    return (
      <PipelineStatusAvatar
        title="Unknown"
        backgroundColor={red[500]}
        iconName="remove"
      />
    );
  }
}

export default UnknownAvatar;
