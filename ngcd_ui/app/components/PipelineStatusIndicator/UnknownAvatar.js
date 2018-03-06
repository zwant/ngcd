import React from 'react';
import PipelineStatusAvatar from './PipelineStatusAvatar';
import PropTypes from 'prop-types';
import Icon from 'material-ui/Icon';
import Tooltip from 'material-ui/Tooltip';
import red from 'material-ui/colors/red';

export class UnknownAvatar extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  render() {
    return (
      <PipelineStatusAvatar title='Unknown' backgroundColor={ red[500] } iconName='remove' />
    )
  }
}

export default UnknownAvatar;
