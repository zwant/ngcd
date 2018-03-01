import React from 'react';
import styled from 'styled-components';

const Title = styled.section`
  padding-bottom: .3em;
  font-size: 1.5em;
  line-height: 1.334;
  border-bottom: 1px solid #eee;
`;

function PageTitle(props) {
  return (
    <Title {...props} />
  );
}

export default PageTitle;
