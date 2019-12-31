import React, { Component } from "react";
import { Container, Row, Card, CardText } from "reactstrap";
import axios from "axios";
import Loading from "./Loading2";

const textStyle = {
  fontFamily: "Oswald, sans-serif",
  fontSize: "20px",
  color: "gray",
  textShadow: "5px 5px 5px pink"
};

export default class Questions extends Component {
  state = {
    loading: false,
    mainQuestions: []
  };
  async componentDidMount() {
    this.setState({ loading: true });
    let url = "http://104.41.155.40:5000/question/video/";
    let data = {
      url: localStorage.getItem("url"),
      nos: 10
    };
    if (localStorage.getItem("type") === "twitter") {
      url = "http://104.41.155.40:5000/question/tweet/";
      data = {
        user: localStorage.getItem("url"),
        nos: 10
      };
    }
    try {
      const res = await axios.post(url, data);
      let questions = res.data.questions;
      var qkeys = [];
      for (var b in questions) qkeys.push(b);
      let mainQuestions = [];
      for (var a = 0; a < qkeys.length; a++) {
        var qu = {
          question: questions[qkeys[a]]
        };
        mainQuestions.push(qu);
      }
      this.setState({ mainQuestions: mainQuestions, loading: false });
      console.log(this.state);
    } catch (error) {
      console.log(error);
    }
  }
  render() {
    return (
      <div>
        {this.state.loading && <Loading />}
        {!this.state.loading && (
          <div>
            <h4 style={textStyle}>Questions:</h4>
            <Container>
              {this.state.mainQuestions.map((question, index) => (
                <div key={index}>
                  <Row>
                    <Card body className="cards">
                      <CardText>{question.question}</CardText>
                    </Card>
                  </Row>
                  <br />
                </div>
              ))}
            </Container>
          </div>
        )}
      </div>
    );
  }
}
