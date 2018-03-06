import React from 'react';
import Avatar from 'material-ui/Avatar';
import PropTypes from 'prop-types';
import Icon from 'material-ui/Icon';
import Tooltip from 'material-ui/Tooltip';

const getStyle = (backgroundColor) => {
  return { backgroundColor: backgroundColor };
}

export class PipelineStatusAvatar extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  render() {
    const { title, backgroundColor, iconName } = this.props;

    return (
      <Tooltip title={ title }>
        <Avatar style={ getStyle(backgroundColor) } >
          <Icon>{ iconName }</Icon>
        </Avatar>
      </Tooltip>
    )
  }
}

PipelineStatusAvatar.propTypes = {
  title: PropTypes.string.isRequired,
  backgroundColor: PropTypes.string.isRequired,
  iconName: PropTypes.string.isRequired,
};

export default PipelineStatusAvatar;
