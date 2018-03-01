import React from 'react';
import PropTypes from 'prop-types';
import Avatar from 'material-ui/Avatar';
import FontIcon from 'material-ui/FontIcon';
import { red500, orange500, green500, blue500 } from 'material-ui/styles/colors';

const iconStyles = { marginRight: '16px' };

const getIconColor = (running, result) => {
  if (running === true) {
    return blue500;
  }
  switch (result) {
    case 'SUCCESS':
      return green500;
    case 'FAILURE':
      return red500;
    case 'ABORTED':
      return orange500;
    default:
      return blue500;
  }
};

const getIconName = (running, result) => {
  if (running === true) {
    return 'directions_run';
  }
  switch (result) {
    case 'SUCCESS':
      return 'done';
    case 'FAILURE':
      return 'error_outline';
    case 'ABORTED':
      return 'highlight_off';
    default:
      return 'remove';
  }
};

export class PipelineStatusIndicator extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  render() {
    const { running, result } = this.props;

    return (
      <Avatar
        icon={<FontIcon className="material-icons">{getIconName(running, result)}</FontIcon>}
        style={iconStyles}
        backgroundColor={getIconColor(running, result)}
      />
    );
  }
}

PipelineStatusIndicator.propTypes = {
  running: PropTypes.bool,
  result: PropTypes.string,
};

export default PipelineStatusIndicator;
