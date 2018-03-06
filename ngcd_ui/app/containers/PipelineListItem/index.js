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
import { makeSelectPipelineDetailsData, makeSelectPipelineDetailsLoading, makeSelectPipelineDetailsLoadingError } from './selectors';
import ExpandedDetails from './ExpandedDetails';
import { connect } from 'react-redux';
import { compose } from 'redux';
import { createStructuredSelector } from 'reselect';
import reducer from './reducer';
import injectReducer from 'utils/injectReducer';
import LoadingIndicator from 'components/LoadingIndicator';

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
    if (!this.state.expanded) {
      this.props.loadPipelineDetails(itemId);
    }
    this.setState({ expanded: !this.state.expanded });
  };

  render() {
    const { classes, item, loadPipelineDetails, pipelineDetailsData, pipelineDetailsLoading, pipelineDetailsLoadingError } = this.props;
    let expanderContents = null;
    if (pipelineDetailsLoading) {
      expanderContents = <LoadingIndicator />;
    } else if (pipelineDetailsData) {
      expanderContents = <ExpandedDetails
                            pipeline={pipelineDetailsData.pipeline}
                            stages={pipelineDetailsData.stages} />;
    } else if (pipelineDetailsLoadingError) {
      expanderContents = 'Oops, something went wrong';
    }

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
                { expanderContents }
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
  pipelineDetailsData: PropTypes.object,
  pipelineDetailsLoading: PropTypes.bool,
  pipelineDetailsLoadingError: PropTypes.bool,
};

export function mapDispatchToProps(dispatch) {
  return {
    /* eslint-disable no-unused-vars */
    loadPipelineDetails: (pipelineId) => dispatch(loadPipelineDetails(pipelineId)),
  };
}


const makeMapStateToProps = () => {
  const pipelineDetailsData = makeSelectPipelineDetailsData();
  const pipelineDetailsLoading = makeSelectPipelineDetailsLoading();
  const pipelineDetailsLoadingError = makeSelectPipelineDetailsLoadingError();

  const mapStateToProps = (state, props) => {
    return {
      pipelineDetailsData: pipelineDetailsData(state, props),
      pipelineDetailsLoading: pipelineDetailsLoading(state, props),
      pipelineDetailsLoadingError: pipelineDetailsLoadingError(state, props),
    }
  }
  return mapStateToProps
}

const withConnect = connect(makeMapStateToProps, mapDispatchToProps);
const withReducer = injectReducer({ key: 'pipelineDetails', reducer });

export default withStyles(styles)(compose(
  withReducer,
  withConnect,
)(PipelineListItem));
