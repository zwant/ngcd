import React from 'react';
import PropTypes from 'prop-types';
import StageListItem from './StageListItem';
import List from 'material-ui/List';
import { withStyles } from 'material-ui/styles';

const styles = theme => ({
  root: {
    width: '100%',
    maxWidth: 360,
    backgroundColor: theme.palette.background.paper,
  },
});

export class ExpandedDetails extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  render() {
    const { classes, pipeline, stages } = this.props;
    // If we have items, render them
    let stageListContent = (<div></div>)
    if (stages) {
      stageListContent = stages.map((stage) => (
        <StageListItem key={`stage-${stage.id}`} item={stage} />
      ));
    }

    return (
      <div>
        <div className={classes.root}>
          <h3>Stages</h3>
          <List>
            { stageListContent }
          </List>
        </div>
      </div>
    );
  }
}

ExpandedDetails.propTypes = {
  classes: PropTypes.object.isRequired,
  pipeline: PropTypes.object,
  stages: PropTypes.array,
};

export default withStyles(styles)(ExpandedDetails);
