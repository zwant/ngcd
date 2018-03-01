import React from 'react';
import Drawer from 'material-ui/Drawer';
import MenuItem from 'material-ui/MenuItem';
import { Link } from 'react-router-dom';
import { FormattedMessage } from 'react-intl';
import messages from './messages';

export default class LeftNavigation extends React.Component { // eslint-disable-line react/prefer-stateless-function
  render() {
    return (
      <div>
        <Drawer>
          <MenuItem containerElement={<Link to="/pipelines" />} >
            <FormattedMessage {...messages.pipelinesLink} />
          </MenuItem>
        </Drawer>
      </div>
    );
  }
}
