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
model = loadModel('/home/bharathrajeevnair/commentstat/backend/serving/my_classifier/model.json', '/home/bharathrajeevnair/commentstat/backend/serving/my_classifier/model.h5')
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
    print(sentence)
    #sentence = base64.b64encode(bytes(sentence, 'utf-8'))
    encoded_sample_pred_text = encoder.encode(sentence)
    print("encode 1")
    encoded_sample_pred_text = tf.cast(encoded_sample_pred_text, tf.float32)
    print("encode 2")
    sentence = tf.expand_dims(encoded_sample_pred_text, 0)
    pred = sample_predict(sentence, pad=True)
    # Creating payload for TensorFlow serving request
    """ payload = {
        "instances": [{'input': sentence}]
    }
    print("after payload")
    # Making POST request
    r = requests.post('http://localhost:9000/v1/models/classifier:predict', json=payload)
    print(r)
    # Decoding results from TensorFlow Serving server
    pred = json.loads(r.content.decode('utf-8')) """
    print(pred)
    # Returning JSON response to the frontend
    return jsonify(pred)

def pad_to_size(vec, size):
  zeros = [0] * (size - len(vec))
  vec.extend(zeros)
  return vec

def loadModel(jsonStr, weightStr):
    json_file = open(jsonStr, 'r')
    loaded_nnet = json_file.read()
    json_file.close()

    serve_model = tf.keras.models.model_from_json(loaded_nnet)
    serve_model.load_weights(weightStr)

    serve_model.compile(optimizer=tf.keras.optimizers.Adam(1e-4),
                        loss='categorical_crossentropy',
                        metrics=['accuracy'])
    return serve_model

def sample_predict(sample_pred_text, pad):
  encoded_sample_pred_text = encoder.encode(sample_pred_text)

  if pad:
    encoded_sample_pred_text = pad_to_size(encoded_sample_pred_text, 64)
  encoded_sample_pred_text = tf.cast(encoded_sample_pred_text, tf.float32)
  predictions = model.predict(tf.expand_dims(encoded_sample_pred_text, 0))

  return (predictions)
