import base64
import json
from io import BytesIO
import numpy as np
import requests
from flask import Flask, request, jsonify


# from flask_cors import CORS

app = Flask(__name__)


# Uncomment this line if you are making a Cross domain request
# CORS(app)

# Testing URL
@app.route('/hello/', methods=['GET', 'POST'])
def hello_world():
    return 'Hello, World!'


@app.route('/sentiment/predict/', methods=['POST'])
def classifier():

    txt = request.json
    sentence = txt["comment"]

    # Creating payload for TensorFlow serving request
    payload = {
        "instances": [{'input': sentence.toString()}]
    }

    # Making POST request
    r = requests.post('http://localhost:9000/v1/models/classifier:predict', json=payload)

    # Decoding results from TensorFlow Serving server
    pred = json.loads(r.content.decode('utf-8'))

    # Returning JSON response to the frontend
    return jsonify(pred['predictions'])