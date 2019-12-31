import React, { Component } from "react";
import {
  Button,
  UncontrolledPopover,
  PopoverHeader,
  PopoverBody
} from "reactstrap";

export default class Popover extends Component {
  render() {
    return (
      <div>
        <Button id="UncontrolledPopover" type="button">
          <strong>?</strong>
        </Button>
        <UncontrolledPopover placement="bottom" target="UncontrolledPopover">
          <PopoverHeader>{this.props.title}</PopoverHeader>
          <PopoverBody>{this.props.body}</PopoverBody>
        </UncontrolledPopover>
      </div>
    );
  }
}
