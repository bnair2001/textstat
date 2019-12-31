import React, { Component } from "react";
import lod from "../load.gif";
import { Container } from "reactstrap";
export default class Loading extends Component {
  render() {
    return (
      <div>
        <Container>
          <img src={lod} alt="logo" className="center" />
        </Container>
      </div>
    );
  }
}
