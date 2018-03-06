import React from 'react';
import PipelineStatusAvatar from './PipelineStatusAvatar';
import PropTypes from 'prop-types';
import Icon from 'material-ui/Icon';
import Tooltip from 'material-ui/Tooltip';
import green from 'material-ui/colors/green';

export class SuccessAvatar extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  render() {
    return (
      <PipelineStatusAvatar title='Success' backgroundColor={ green[500] } iconName='done' />
    )
  }
}

export default SuccessAvatar;
