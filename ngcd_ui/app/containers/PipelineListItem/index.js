/**
 * PipelineListItem
 *
 * Lists the name and the issue count of a repository
 */

import React from 'react';
import PropTypes from 'prop-types';
import Moment from 'react-moment';
import ListItem from 'components/ListItem';
import PipelineStatusIndicator from 'components/PipelineStatusIndicator';
import PipelineDetails from 'containers/PipelineDetails';
import Card, { CardHeader, CardContent, CardActions } from 'material-ui/Card';
import Wrapper from './Wrapper';
import Collapse from 'material-ui/transitions/Collapse';
import Typography from 'material-ui/Typography';
import ExpandMoreIcon from 'material-ui-icons/ExpandMore';
import classnames from 'classnames';
import IconButton from 'material-ui/IconButton';
import { withStyles } from 'material-ui/styles';
import { loadPipelineDetails } from './actions';
import injectSaga from 'utils/injectSaga';
import saga from './saga';
import { selectPipelineDetails } from './selectors';
import { connect } from 'react-redux';
import { compose } from 'redux';
import { createStructuredSelector } from 'reselect';
import reducer from './reducer';
import injectReducer from 'utils/injectReducer';

const headerStyle = { fontWeight: '500' };
const cardStyle = { width: '50%' };

const styles = theme => ({
  card: {
    width: '50%',
  },
  header: {
    fontWeight: '500',
  },
  actions: {
    display: 'flex',
  },
  expand: {
    transform: 'rotate(0deg)',
    transition: theme.transitions.create('transform', {
      duration: theme.transitions.duration.shortest,
    }),
    marginLeft: 'auto',
  },
  expandOpen: {
    transform: 'rotate(180deg)',
  },
});

class PipelineListItem extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  state = { expanded: false };

  handleExpandClick = (itemId) => {
    this.setState({ expanded: !this.state.expanded });
    this.props.loadPipelineDetails(itemId);
  };

  render() {
    const { classes, item, loadPipelineDetails, pipelineDetails } = this.props;
    // Put together the content of the pipeline
    const content = (
      <Wrapper>
        <Card style={cardStyle}>

          <CardHeader
            title={item.external_id}
            subheader={<Moment fromNow>{ item.started_running_at }</Moment>}
            avatar={<PipelineStatusIndicator running={item.currently_running} result={item.result} />}
            style={headerStyle}
            />
          <CardContent>
            <PipelineDetails item={item} />
          </CardContent>
          <CardActions disableActionSpacing>
            <IconButton
              className={classnames(classes.expand, {
                [classes.expandOpen]: this.state.expanded,
              })}
              onClick={() => this.handleExpandClick(item.external_id)}
              aria-expanded={this.state.expanded}
              aria-label="Show more"
            >
              <ExpandMoreIcon />
            </IconButton>
          </CardActions>

          <Collapse in={this.state.expanded} timeout="auto" unmountOnExit>
            <CardContent>
              <Typography paragraph>
                { pipelineDetails }
              </Typography>
            </CardContent>
          </Collapse>
        </Card>
      </Wrapper>
    );
    // Render the content into a list item
    return (
      <ListItem key={`pipeline-list-item-${item.id}`} item={content} />
    );
  }
}
PipelineListItem.propTypes = {
  classes: PropTypes.object.isRequired,
  item: PropTypes.object,
  loadPipelineDetails: PropTypes.func,
  pipelineDetails: PropTypes.object,
};

export function mapDispatchToProps(dispatch) {
  return {
    /* eslint-disable no-unused-vars */
    loadPipelineDetails: (pipelineId) => dispatch(loadPipelineDetails(pipelineId)),
  };
}

const makeMapStateToProps = () => {
  const mapStateToProps = (state, props) => {
    return {
      pipelineDetails: selectPipelineDetails(state, props)
    }
  }
  return mapStateToProps
}

const withConnect = connect(makeMapStateToProps, mapDispatchToProps);
const withSaga = injectSaga({ key: 'pipelineDetails', saga });
const withReducer = injectReducer({ key: 'pipelineDetails', reducer });

export default withStyles(styles)(compose(
  withReducer,
  withSaga,
  withConnect,
)(PipelineListItem));
