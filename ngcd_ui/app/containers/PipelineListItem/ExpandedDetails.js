import React from 'react';
import PropTypes from 'prop-types';

export class ExpandedDetails extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  render() {
    const {pipeline, stages} = this.props;

    return (
      <div>
        <div>
          { pipeline.average_duration }
        </div>
        <div>
          { stages.map( (stage) =>
            stage.last_duration
          ) }
        </div>
      </div>
    );
  }
}

ExpandedDetails.propTypes = {
  pipeline: PropTypes.object,
  stages: PropTypes.array,
};

export default ExpandedDetails;
