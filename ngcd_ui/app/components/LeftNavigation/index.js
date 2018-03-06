import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from 'material-ui/styles';
import Drawer from 'material-ui/Drawer';
import { MenuList, MenuItem } from 'material-ui/Menu';
import { Link } from 'react-router-dom';
import { FormattedMessage } from 'react-intl';
import messages from './messages';

const styles = (theme) => ({
  drawerPaper: {
    position: 'relative',
    width: '160px',
  },
});

class LeftNavigation extends React.Component { // eslint-disable-line react/prefer-stateless-function
  render() {
    const { classes } = this.props;

    return (
      <div>
        <Drawer
          variant="permanent"
          anchor="left"
          classes={{
            paper: classes.drawerPaper,
          }}
        >
          <MenuList component="nav">
            <MenuItem component={Link} to='/pipelines'>
              <FormattedMessage {...messages.pipelinesLink} />
            </MenuItem>
          </MenuList>
        </Drawer>
      </div>
    );
  }
}

LeftNavigation.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(LeftNavigation);
