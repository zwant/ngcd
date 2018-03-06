import React from 'react';
import PropTypes from 'prop-types';
import { ListItem, ListItemText } from 'material-ui/List';
import PipelineStatusIndicator from 'components/PipelineStatusIndicator';

const styles = theme => ({
  root: {
    width: '100%',
    maxWidth: 360,
    backgroundColor: theme.palette.background.paper,
  },
});

export class StageListItem extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  render() {
    const { item } = this.props;

    return (
      <ListItem divider>
        <PipelineStatusIndicator running={item.currently_running} result={item.result} />
        <ListItemText primary={ item.id } secondary={ item.result } />
      </ListItem>
    );
  }
}

StageListItem.propTypes = {
  item: PropTypes.object,
};

export default StageListItem;
