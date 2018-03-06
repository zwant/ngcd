import React from 'react';
import PipelineStatusAvatar from './PipelineStatusAvatar';
import PropTypes from 'prop-types';
import Icon from 'material-ui/Icon';
import Tooltip from 'material-ui/Tooltip';
import blue from 'material-ui/colors/blue';

export class RunningAvatar extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  render() {
    return (
      <PipelineStatusAvatar title='Running' backgroundColor={ blue[500] } iconName='directions_run' />
    )
  }
}

export default RunningAvatar;
