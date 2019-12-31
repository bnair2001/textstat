import React, { Component } from "react";
import { Form, FormGroup, Input, Button, Container, Alert } from "reactstrap";
import { withRouter } from "react-router-dom";
const styles = {
  marginTop: "30%"
};
const buttonStyle = {
  marginLeft: "50%"
};
const alertStyle = {
  marginTop: "15px"
};
class urlForm extends Component {
  state = {
    url: "",
    unknown: false
  };
  onChange = e => {
    this.setState({ [e.target.name]: e.target.value });
  };
  onSubmit = event => {
    event.preventDefault();
    const youtube = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=|\?v=)([^#\&\?]*).*/;
    const fb = /^(https?:\/\/)?((w{3}\.)?)facebook.com\/.*/;
    const twitter = /^@/;
    this.props.history.push("/stat");
    if (youtube.test(this.state.url)) {
      localStorage.setItem("url", this.state.url);
      localStorage.setItem("type", "yt");
      this.props.history.push("/stat");
    } else if (fb.test(this.state.url)) {
      this.setState({ unknown: true });
    } else if (twitter.test(this.state.url)) {
      localStorage.setItem("url", this.state.url);
      localStorage.setItem("type", "twitter");
      this.props.history.push("/stat");
    } else {
      this.setState({ unknown: true });
    }
  };

  componentDidMount() {
    if (localStorage.getItem("error") !== null) {
      this.setState({ unknown: true });
      localStorage.removeItem("error");
    }
  }
  render() {
    return (
      <Container className="as" fluid="sm">
        <Form onSubmit={this.onSubmit} style={styles}>
          <FormGroup>
            <Input
              type="text"
              name="url"
              id="url"
              value={this.state.url}
              onChange={this.onChange}
              placeholder="Enter youtube video url or twitter profile id(start with @)."
              required
            />
          </FormGroup>

          <Button color="danger" style={buttonStyle} className="btn-lg">
            Go!
          </Button>
          <br />
          {this.state.unknown && (
            <Alert color="danger" style={alertStyle}>
              Invalid entry!! Try a twitter profile id or youtube video url!
            </Alert>
          )}
        </Form>
      </Container>
    );
  }
}

export default withRouter(urlForm);
