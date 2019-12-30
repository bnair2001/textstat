from __future__ import absolute_import, division, print_function, unicode_literals
import base64
import json
from io import BytesIO
import os
import csv
import pickle
import numpy as np
import requests
import tensorflow_datasets as tfds
import tensorflow as tf
from flask import Flask, request, jsonify
import google.oauth2.credentials

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

# from flask_cors import CORS

app = Flask(__name__)


# Uncomment this line if you are making a Cross domain request
# CORS(app)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
#service = get_authenticated_service(0)
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
#auth
credentials = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        credentials = pickle.load(token)
#  Check if the credentials are invalid or do not exist
if not credentials or not credentials.valid:
    # Check if the credentials have expired
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_console()

    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(credentials, token)

service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
dataset, info = tfds.load('imdb_reviews/subwords8k',
                          with_info=True, as_supervised=True)
encoder = info.features['text'].encoder
# cloud path
#jsonStr = '/home/bharathrajeevnair/commentstat/backend/serving/my_classifier/model.json'
#weightStr = '/home/bharathrajeevnair/commentstat/backend/serving/my_classifier/model.h5'
# local path
jsonStr = '/Users/bharathnair/Documents/GitHub/commentstat/backend/serving/my_classifier/model.json'
weightStr = '/Users/bharathnair/Documents/GitHub/commentstat/backend/serving/my_classifier/model.h5'

json_file = open(jsonStr, 'r')
loaded_nnet = json_file.read()
json_file.close()

serve_model = tf.keras.models.model_from_json(loaded_nnet)
serve_model.load_weights(weightStr)

serve_model.compile(optimizer=tf.keras.optimizers.Adam(
    1e-4), loss='categorical_crossentropy', metrics=['accuracy'])
model = serve_model
# Testing URL
@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return 'Hello, World!'


@app.route('/sentiment/predict/', methods=['POST'])
def classifier():
    txt = request.json
    # print(request.json)
    sentence = txt["comment"]
    # print(sentence)
    pred = sample_predict(sentence, pad=True)
    # print(pred.tolist())
    # print(type(pred[0,0]+0))
    pred = pred.tolist()
    val = pred[0][0]
    # print(val)
    # print(type(val))
    return str(val)


@app.route('/video/predict/', methods=['POST'])
def vid():
    req = request.json
    #video_comment_threads = get_comment_threads(service, 'kMtN9KJHn5Y')
    comments = get_video_comments(service, part='snippet', videoId='kMtN9KJHn5Y', textFormat='plainText', maxResults = 1)
    print(comments)
    return 'hey it works'


def pad_to_size(vec, size):
    zeros = [0] * (size - len(vec))
    vec.extend(zeros)
    return vec


def sample_predict(sample_pred_text, pad):
    encoded_sample_pred_text = encoder.encode(sample_pred_text)

    if pad:
        encoded_sample_pred_text = pad_to_size(encoded_sample_pred_text, 64)
    encoded_sample_pred_text = tf.cast(encoded_sample_pred_text, tf.float32)
    predictions = model.predict(tf.expand_dims(
        encoded_sample_pred_text, 0), steps=1)

    return (predictions)
def get_statistics_views(youtube,video_id,token=""):
    response = youtube.videos().list(
    part='statistics, snippet',
    id=video_id).execute()

    view_count = response['items'][0]['statistics']['viewCount']
    like_count = response['items'][0]['statistics']['likeCount']
    dislike_count = response['items'][0]['statistics']['dislikeCount']
    return view_count,like_count,dislike_count

def get_comment_threads(youtube, video_id, comments=[], token=""):
    results = youtube.commentThreads().list(
        part="snippet",
        pageToken=token,
        videoId=video_id,
        textFormat="plainText"
    ).execute()

    for item in results["items"]:
        comment = item["snippet"]["topLevelComment"]
        text = comment["snippet"]["textDisplay"]
        comments.append(text)

    if "nextPageToken" in results:
        return get_comment_threads(youtube, video_id, comments, results["nextPageToken"])
    else:
        return comments

def get_comment_count_threads(youtube, video_id, comments_count=[], token=""):
    results = youtube.commentThreads().list(
        part="snippet",
        pageToken=token,
        videoId=video_id,
        textFormat="plainText"
    ).execute()

    for item in results["items"]:
        comment_count = item["snippet"]["topLevelComment"]
        like_count = comment_count["snippet"]["likeCount"]
        comments_count.append(like_count)

    if "nextPageToken" in results:
        return get_comment_count_threads(youtube, video_id, comments_count, results["nextPageToken"])
    else:
        return comments_count

def get_video_comments(service, **kwargs):
    comments = []
    results = service.commentThreads().list(**kwargs).execute()

    while results:
        for item in results['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)

        # Check if another page exists
        if 'nextPageToken' in results:
            kwargs['pageToken'] = results['nextPageToken']
            results = service.commentThreads().list(**kwargs).execute()
        else:
            break

    return comments