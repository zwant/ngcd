import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from 'material-ui/styles';
import MaterialAppBar from 'material-ui/AppBar';
import Toolbar from 'material-ui/Toolbar';
import Typography from 'material-ui/Typography';

const menuWidth = '160px';

const styles = (theme) => ({
  appBar: {
    width: `calc(100% - ${menuWidth})`,
    marginLeft: menuWidth,
  },
});

class AppBar extends React.Component { // eslint-disable-line react/prefer-stateless-function
  render() {
    const { classes, text } = this.props;

    return (
      <MaterialAppBar
        position="absolute"
        className={classes.appBar}
      >
        <Toolbar>
          <Typography variant="title" color="inherit" noWrap>
            {text}
          </Typography>
        </Toolbar>
      </MaterialAppBar>
    );
  }
}

AppBar.propTypes = {
  classes: PropTypes.object.isRequired,
  text: PropTypes.string.isRequired,
};

export default withStyles(styles)(AppBar);
