/**
 * PipelineListItem
 *
 * Lists the name and the issue count of a repository
 */

import React from 'react';
import PropTypes from 'prop-types';
import Moment from 'react-moment';
import ListItem from 'components/ListItem';
import PipelineStatusIndicator from 'containers/PipelineStatusIndicator';
import PipelineDetails from 'containers/PipelineDetails';
import { Card, CardHeader, CardText } from 'material-ui/Card';
import Wrapper from './Wrapper';

const headerStyle = { fontWeight: '500' };
const cardStyle = { width: '50%' };

export class PipelineListItem extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  render() {
    const item = this.props.item;
    // Put together the content of the pipeline
    const content = (
      <Wrapper>
        <Card style={cardStyle}>
          <CardHeader
            title={item.external_id}
            subtitle={<Moment fromNow>{ item.started_running_at }</Moment>}
            avatar={<PipelineStatusIndicator running={item.currently_running} result={item.result} />}
            style={headerStyle}
          />
          <CardText>
            <PipelineDetails item={item} />
          </CardText>
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
  item: PropTypes.object,
};

export default PipelineListItem;
