/**
*
* App.js
*
* This component is the skeleton around the actual pages, and should only
* contain code that should be seen on all pages. (e.g. navigation bar)
*
* NOTE: while this component should technically be a stateless functional
* component (SFC), hot reloading does not currently support SFCs. If hot
* reloading is not a necessity for you then you can refactor it and remove
* the linting exception.
*/

import React from 'react';

import { Switch, Route } from 'react-router-dom';
import AppBar from 'components/AppBar';
import LeftNavigation from 'components/LeftNavigation';
import HomePage from 'containers/HomePage/Loadable';
import PipelinePage from 'containers/PipelinePage/Loadable';
import NotFoundPage from 'containers/NotFoundPage/Loadable';
import styled from 'styled-components';
import PropTypes from 'prop-types';

const MainContentWrapper = styled.main`
padding: 24px;
flex-grow: 1;
`;

const AppWrapper = styled.div`
display: flex;
overflow: hidden;
position: relative;
`;

const ToolBarDiv = styled.div`
min-height: 64px;
`;

class App extends React.Component {
  render() {
    return (
      <AppWrapper>
        <Switch>
          <Route exact path="/"
            render={(props) => <AppBar text='Home' />} />
          <Route exact path="/pipelines"
            render={(props) => <AppBar text='Pipelines' />} />
          <Route component={NotFoundPage} />
        </Switch>
        <LeftNavigation />
        <MainContentWrapper>
          <ToolBarDiv />
          <Switch>
            <Route exact path="/" component={HomePage} />
            <Route exact path="/pipelines" component={PipelinePage} />
            <Route component={NotFoundPage} />
          </Switch>
        </MainContentWrapper>
      </AppWrapper>
    );
  }
}

export default App;
