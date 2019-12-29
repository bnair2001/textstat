from __future__ import absolute_import, division, print_function, unicode_literals
import base64
import json
from io import BytesIO
import numpy as np
import requests
import tensorflow_datasets as tfds
import tensorflow as tf
from flask import Flask, request, jsonify


# from flask_cors import CORS

app = Flask(__name__)


# Uncomment this line if you are making a Cross domain request
# CORS(app)
dataset, info = tfds.load('imdb_reviews/subwords8k', with_info=True, as_supervised=True)
encoder = info.features['text'].encoder
# Testing URL
@app.route('/hello/', methods=['GET', 'POST'])
def hello_world():
    return 'Hello, World!'


@app.route('/sentiment/predict/', methods=['POST'])
def classifier():
    txt = request.json
    print(request.json)
    #s1 = json.dumps(txt)
    #txt = json.loads(s1)
    sentence = txt["comment"]
    encoded_sample_pred_text = encoder.encode(sentence)
    encoded_sample_pred_text = tf.cast(encoded_sample_pred_text, tf.float32)
    sentence = tf.expand_dims(encoded_sample_pred_text, 0)
    # Creating payload for TensorFlow serving request
    payload = {
        "instances": [{'input': sentence}]
    }

    # Making POST request
    r = requests.post('http://localhost:9000/v1/models/classifier:predict', json=payload)

    # Decoding results from TensorFlow Serving server
    pred = json.loads(r.content.decode('utf-8'))

    # Returning JSON response to the frontend
    return jsonify(pred['predictions'])

def pad_to_size(vec, size):
  zeros = [0] * (size - len(vec))
  vec.extend(zeros)
  return vec
