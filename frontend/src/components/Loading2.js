import React, { Component } from "react";
import { Spinner } from "reactstrap";

export default class Loading2 extends Component {
  render() {
    return (
      <div>
        <Spinner size="lg" color="danger" />
      </div>
    );
  }
}
