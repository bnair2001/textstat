import React, { Component } from "react";
import Navbar from "./Navbar";
import axios from "axios";
import Loading from "./Loading";
import Quest from "./Questions";
import Popover from "./Popover";
import {
  Container,
  Row,
  Col,
  Card,
  CardText,
  Progress,
  CardBody,
  CardTitle
} from "reactstrap";
const styles = {
  marginTop: "25px"
};
const style2 = {
  marginTop: "65px"
};
const dotstyle = {
  backgroundColor: " #dd4746"
};
const dotstyle2 = {
  backgroundColor: "#53A846"
};
const textStyle = {
  fontFamily: "Oswald, sans-serif",
  fontSize: "20px",
  color: "gray",
  textShadow: "5px 5px 5px pink"
};
const stylepop = {
  float:"right"
};
export default class Stat extends Component {
  state = {
    sentimentScore: 0,
    criticalComments: [],
    loading: false,
    pos: false
  };
  shuffle = array => {
    var currentIndex = array.length,
      temporaryValue,
      randomIndex;

    // While there remain elements to shuffle...
    while (0 !== currentIndex) {
      // Pick a remaining element...
      randomIndex = Math.floor(Math.random() * currentIndex);
      currentIndex -= 1;

      // And swap it with the current element.
      temporaryValue = array[currentIndex];
      array[currentIndex] = array[randomIndex];
      array[randomIndex] = temporaryValue;
    }

    return array;
  };
  async componentDidMount() {
    if (localStorage.getItem("url") !== null) {
      this.setState({ loading: true });
      let url = "http://104.41.155.40:5000/video/predict/";
      let data = {
        url: localStorage.getItem("url"),
        nos: 5
      };
      if (localStorage.getItem("type") === "twitter") {
        url = "http://104.41.155.40:5000/tweet/predict/";
        data = {
          user: localStorage.getItem("url"),
          nos: 10
        };
      }

      try {
        const res = await axios.post(url, data);
        console.log(res.data);

        let sentimentScore = Math.round(
          res.data.scorebypointfive + res.data.scoretotalsum
        );
        const positive = res.data.positive;
        const negative = res.data.negative;
        var poskeys = [];
        for (var k in positive) poskeys.push(k);
        var negkeys = [];
        for (var y in negative) negkeys.push(y);
        let criticalComments = [];
        for (var i = 0; i < poskeys.length; i++) {
          var comment = {
            comment: positive[poskeys[i]],
            type: 1
          };
          criticalComments.push(comment);
        }
        for (var j = 0; j < negkeys.length; j++) {
          var comment2 = {
            comment: negative[negkeys[j]],
            type: 0
          };
          criticalComments.push(comment2);
        }
        if (criticalComments.length > 15) {
          criticalComments = criticalComments.slice(0, 15);
        }
        let pos = false;
        if (sentimentScore > 50) {
          pos = true;
        }
        sentimentScore = Math.round(sentimentScore / 2);
        criticalComments = this.shuffle(criticalComments);

        this.setState({
          criticalComments: criticalComments,
          sentimentScore: sentimentScore,
          loading: false,
          pos: pos,
          wordCloud: res.data.wordcloud
        });
        console.log(this.state);
      } catch (error) {
        this.setState({ loading: false });
        localStorage.setItem("error", "Invalid Url");
        this.props.history.push("/");
      }
    } else {
      this.props.history.push("/");
    }
  }
  render() {
    return (
      <div>
        <Navbar />
        {this.state.loading && <Loading />}
        {!this.state.loading && (
          <Container>
            <img
              src={this.state.wordCloud}
              width="1110"
              height="410"
              alt="word-cloud"
              style={styles}
              className="cards"
            />
            <Row>
              <Col>
                <Card body className="cards">
                  <CardTitle>
                    <h4 style={textStyle}>Sentiment Score:</h4>
                    <Popover style={stylepop} title="Sentiment Score" body="Higher the score. Higher is the positivity of the comments. Lower the score. Higher is the negativity.(Minimum:0 and Maximum:100) " />
                  </CardTitle>
                  <CardBody>
                    <Container>
                      <Row>
                        <Col xs="2">
                          <div
                            className="dot"
                            style={this.state.pos ? dotstyle2 : dotstyle}
                          >
                            {this.state.sentimentScore}
                          </div>
                        </Col>
                        <Col xs="10" style={style2}>
                          <Progress
                            color={this.state.pos ? "success" : "danger"}
                            value={this.state.sentimentScore}
                          />
                        </Col>
                      </Row>
                    </Container>
                  </CardBody>
                </Card>
              </Col>
            </Row>
            <br />
            <Row>
              <Col xs="6">
                <h4 style={textStyle}>Critical Comments:</h4>
                <Container>
                  {this.state.criticalComments.map((comment, index) => (
                    <div key={index}>
                      <Row>
                        <Card body className="cards">
                          <CardText>{comment.comment}</CardText>
                        </Card>
                      </Row>
                      <br />
                    </div>
                  ))}
                </Container>
              </Col>
              <Col xs="6">
                <Quest />
              </Col>
            </Row>
          </Container>
        )}
      </div>
    );
  }
}
