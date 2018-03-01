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
import LeftNavigation from 'components/LeftNavigation';
import HomePage from 'containers/HomePage/Loadable';
import PipelinePage from 'containers/PipelinePage/Loadable';
import NotFoundPage from 'containers/NotFoundPage/Loadable';
import styled from 'styled-components';

const MainContentWrapper = styled.section`
padding-left: 256px;
margin-left: 48px;
`;

export default function App() {
  return (
    <div>
      <LeftNavigation />
      <MainContentWrapper>
        <Switch>
          <Route exact path="/" component={HomePage} />
          <Route exact path="/pipelines" component={PipelinePage} />
          <Route component={NotFoundPage} />
        </Switch>
      </MainContentWrapper>
    </div>
  );
}
