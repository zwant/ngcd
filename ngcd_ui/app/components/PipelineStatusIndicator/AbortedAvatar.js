import React from 'react';
import PipelineStatusAvatar from './PipelineStatusAvatar';
import PropTypes from 'prop-types';
import Icon from 'material-ui/Icon';
import Tooltip from 'material-ui/Tooltip';
import orange from 'material-ui/colors/orange';

export class AbortedAvatar extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  render() {
    return (
      <PipelineStatusAvatar title='Aborted' backgroundColor={ orange[500] } iconName='highlight_off' />
    )
  }
}

export default AbortedAvatar;
