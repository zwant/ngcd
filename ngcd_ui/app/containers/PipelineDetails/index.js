import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';
import Moment from 'react-moment';

const millisecondsToMinutesSeconds = (ms) => {
  const duration = moment.duration(ms, 'milliseconds');
  const fromMinutes = Math.floor(duration.asMinutes());
  const fromSeconds = Math.floor(duration.asSeconds() - fromMinutes * 60);

  return Math.floor(duration.asSeconds()) >= 60
    ? `${fromMinutes <= 9 ? `0${fromMinutes}` : fromMinutes}h ${
        fromSeconds <= 9 ? `0${fromSeconds}` : fromSeconds
      }`
    : `00m ${fromSeconds <= 9 ? `0${fromSeconds}` : fromSeconds}s`;
};

export class PipelineDetails extends React.PureComponent {
  // eslint-disable-line react/prefer-stateless-function
  render() {
    const item = this.props.item;

    return (
      <div>
        {item.average_duration != null && (
          <div>
            {' '}
            Average Duration:{' '}
            {millisecondsToMinutesSeconds(item.average_duration)}{' '}
          </div>
        )}
        {item.last_duration != null && (
          <div>
            {' '}
            Last Duration: {millisecondsToMinutesSeconds(
              item.last_duration
            )}{' '}
          </div>
        )}
        {item.number_of_runs != null && (
          <div> Number of runs: {item.number_of_runs} </div>
        )}
        {item.finished_running_at != null && (
          <div>
            {' '}
            Finished running:{' '}
            <Moment fromNow>{item.finished_running_at}</Moment>{' '}
          </div>
        )}
      </div>
    );
  }
}

PipelineDetails.propTypes = {
  item: PropTypes.object,
};

export default PipelineDetails;
