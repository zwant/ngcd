import React from 'react';
import PipelineStatusAvatar from './PipelineStatusAvatar';
import PropTypes from 'prop-types';
import Icon from 'material-ui/Icon';
import Tooltip from 'material-ui/Tooltip';
import red from 'material-ui/colors/red';

export class FailureAvatar extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  render() {
    return (
      <PipelineStatusAvatar title='Failed' backgroundColor={ red[500] } iconName='error_outline' />
    )
  }
}

export default FailureAvatar;
