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
import time
from selenium.webdriver import Chrome
from cleantext import clean
from contextlib import closing
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from urllib.request import urlopen
from urllib.parse import urlencode, quote_plus
from twitterscraper import query_tweets

from flask_cors import CORS

app = Flask(__name__)


# Uncomment this line if you are making a Cross domain request
CORS(app)
chrome_options = Options()
chrome_options.add_argument("--headless")


dataset, info = tfds.load('imdb_reviews/subwords8k',
                          with_info=True, as_supervised=True)
encoder = info.features['text'].encoder
# cloud path
jsonStr = '/home/bnair2001/commentstat/backend/serving/my_classifier/model.json'
weightStr = '/home/bnair2001/commentstat/backend/serving/my_classifier/model.h5'
# local path
#jsonStr = '/Users/bharathnair/Documents/GitHub/commentstat/backend/serving/my_classifier/model.json'
#weightStr = '/Users/bharathnair/Documents/GitHub/commentstat/backend/serving/my_classifier/model.h5'

json_file = open(jsonStr, 'r')
loaded_nnet = json_file.read()
json_file.close()

serve_model = tf.keras.models.model_from_json(loaded_nnet)
serve_model.load_weights(weightStr)

serve_model.compile(optimizer=tf.keras.optimizers.Adam(
    1e-4), loss='categorical_crossentropy', metrics=['accuracy'])
model = serve_model
Question_Words = ['what', 'where', 'when','how','why','did','do','does','have','has','am','is','are','can','could','may','would','will','should'
"didn't","doesn't","haven't","isn't","aren't","can't","couldn't","wouldn't","won't","shouldn't",'?']
# Testing URL
@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return 'Hello, World!'

@app.route('/question/video/', methods=['POST'])
def vidq():
    req = request.json
    url = req["url"]
    nos = req["nos"]
    questions = {
    }
    questioncount = 0
    count = 0
    with closing(Chrome(chrome_options=chrome_options)) as driver:
        wait = WebDriverWait(driver, 10)
        driver.get(url)

        for item in range(nos):  # by increasing the highest range you can get more content
            wait.until(EC.visibility_of_element_located(
                (By.TAG_NAME, "body"))).send_keys(Keys.END)
            time.sleep(3)

        for comment in wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#comment #content-text"))):
            # print(comment.text)
            com = comment.text
            count = count + 1
            com = clean(comment.text,
                        fix_unicode=True,               # fix various unicode errors
                        to_ascii=True,                  # transliterate to closest ASCII representation
                        lower=True,                     # lowercase text
                        # fully strip line breaks as opposed to only normalizing them
                        no_line_breaks=True,
                        no_urls=True,                  # replace all URLs with a special token
                        no_emails=True,                # replace all email addresses with a special token
                        no_phone_numbers=True,         # replace all phone numbers with a special token
                        no_numbers=False,               # replace all numbers with a special token
                        no_digits=False,                # replace all digits with a special token
                        no_currency_symbols=False,      # replace all currency symbols with a special token
                        no_punct=False,                 # fully remove punctuation
                        replace_with_url="",
                        replace_with_email="",
                        replace_with_phone_number="",
                        replace_with_number="",
                        replace_with_digit="0",
                        replace_with_currency_symbol="",
                        lang="en"                       # set to 'de' for German special handling
                        )
            words = com.split()
            for word in Question_Words:
                if word in words:
                    questions[word] = com
                    questioncount = questioncount + 1
    qpercent = abs((questioncount/count)*100)
    payload = {
        "questions": questions,
        "percentageofquestions": qpercent
    }                
    return jsonify(payload)


@app.route('/question/tweet/', methods=['POST'])
def vidq():
    req = request.json
    user = req["user"]
    nos = req["nos"]
    questions = {
    }
    questioncount = 0
    count = 0
    list_of_tweets = query_tweets(user, nos)
    for tweet in query_tweets(user, nos):
        tw = tweet.text
        count = count + 1
        com = clean(tw,
                    fix_unicode=True,               # fix various unicode errors
                    to_ascii=True,                  # transliterate to closest ASCII representation
                    lower=True,                     # lowercase text
                    # fully strip line breaks as opposed to only normalizing them
                    no_line_breaks=True,
                    no_urls=True,                  # replace all URLs with a special token
                    no_emails=True,                # replace all email addresses with a special token
                    no_phone_numbers=True,         # replace all phone numbers with a special token
                    no_numbers=False,               # replace all numbers with a special token
                    no_digits=False,                # replace all digits with a special token
                    no_currency_symbols=False,      # replace all currency symbols with a special token
                    no_punct=False,                 # fully remove punctuation
                    replace_with_url="",
                    replace_with_email="",
                    replace_with_phone_number="",
                    replace_with_number="",
                    replace_with_digit="0",
                    replace_with_currency_symbol="",
                    lang="en"                       # set to 'de' for German special handling
                    )
        words = com.split()
        for word in Question_Words:
            if word in words:
                questions[word] = com
                questioncount = questioncount + 1
    qpercent = abs((questioncount/count)*100)
    payload = {
        "questions": questions,
        "percentageofquestions": qpercent
    }                
    return jsonify(payload)


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
    url = req["url"]
    nos = req["nos"]
    lessthanpointtwo = {
    }
    morethanpointeight = {
    }
    findict = {
    }
    sentivals = []
    count = 0
    totalsentiment = 0
    positive = 0
    text = ""
    # video_comment_threads = get_comment_threads(service, 'kMtN9KJHn5Y')
    # comments = get_video_comments(service, part='snippet', videoId='IcJhmhA8tHE', textFormat='plainText', maxResults = 100)
    with closing(Chrome(chrome_options=chrome_options)) as driver:
        wait = WebDriverWait(driver, 10)
        driver.get(url)

        for item in range(nos):  # by increasing the highest range you can get more content
            wait.until(EC.visibility_of_element_located(
                (By.TAG_NAME, "body"))).send_keys(Keys.END)
            time.sleep(3)

        for comment in wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#comment #content-text"))):
            # print(comment.text)
            com = comment.text
            com = clean(comment.text,
                        fix_unicode=True,               # fix various unicode errors
                        to_ascii=True,                  # transliterate to closest ASCII representation
                        lower=True,                     # lowercase text
                        # fully strip line breaks as opposed to only normalizing them
                        no_line_breaks=True,
                        no_urls=True,                  # replace all URLs with a special token
                        no_emails=True,                # replace all email addresses with a special token
                        no_phone_numbers=True,         # replace all phone numbers with a special token
                        no_numbers=False,               # replace all numbers with a special token
                        no_digits=False,                # replace all digits with a special token
                        no_currency_symbols=False,      # replace all currency symbols with a special token
                        no_punct=False,                 # fully remove punctuation
                        replace_with_url="",
                        replace_with_email="",
                        replace_with_phone_number="",
                        replace_with_number="",
                        replace_with_digit="0",
                        replace_with_currency_symbol="",
                        lang="en"                       # set to 'de' for German special handling
                        )
            analysis = TextBlob(com)
            text = text + com
            pol = analysis.sentiment.polarity
            senti = sample_predict(com, pad=True)
            senti = senti.tolist()
            senti = senti[0][0]
            """ if senti < 0.8 or pol != 0 and pol > 0:
               count = count + 1
               positive = positive + 1
               sentivals.append(senti) """
            if pol != 0 and pol < 0:
                lessthanpointtwo[senti] = com
                count = count + 1
                totalsentiment = totalsentiment + senti
                #positive = positive - 1
            elif pol != 0 and pol > 0:
                morethanpointeight[senti] = com
                count = count + 1
                positive = positive + 1
                totalsentiment = totalsentiment + senti
            else:
                abcdef = 0

    #positive = count - positive
    negative = len(sentivals)
    sentivals.sort()
    """ for x in sentivals:
      findict[lessthanpointtwo[x]] = x """
    #print(abs(positive/count)*100)
    #print(abs(negative/count)*100)
    """ findict["positive"] = abs(positive/count)*100
    findict["negative"] = abs(negative/count)*100  """
    scoretotalsum = (totalsentiment/count)*100
    scorebypointfive = abs(positive/count)*100
    cloud = WordCloud().generate(text)
    cloud.to_file('N.png')
    f = open("N.png", "rb")  # open our image file as read only in binary mode
    image_data = f.read()
    b64_image = base64.standard_b64encode(image_data)
    client_id = "2cb3e1b4f5c5ea3"  # put your client ID here
    headers = {'Authorization': 'Client-ID ' + client_id}
    url = "https://api.imgur.com/3/image"
    j1 = requests.post(
        url,
        headers=headers,
        data={
            'image': b64_image,
            'type': 'base64'
        }
    )
    data = json.loads(j1.text)['data']
    wcloud = data['link']
    payload = {
        "positive": morethanpointeight,
        "negative": lessthanpointtwo,
        "scoretotalsum": scoretotalsum,
        "scorebypointfive": scorebypointfive,
        "wordcloud": wcloud
    }
    print(findict)
    return jsonify(payload)


@app.route('/tweet/predict/', methods=['POST'])
def tweet():
    req = request.json
    user = req["user"]
    nos = req["nos"]
    positivetweets = {
    }
    negativetweets = {       
    }
    count = 0
    totalsenticount = 0
    positive = 0
    list_of_tweets = query_tweets(user, nos)
    wctext = ""
    for tweet in query_tweets(user, nos):
        tw = tweet.text
        tw = clean(tweet.text,
                        fix_unicode=True,               # fix various unicode errors
                        to_ascii=True,                  # transliterate to closest ASCII representation
                        lower=True,                     # lowercase text
                        # fully strip line breaks as opposed to only normalizing them
                        no_line_breaks=True,
                        no_urls=True,                  # replace all URLs with a special token
                        no_emails=True,                # replace all email addresses with a special token
                        no_phone_numbers=True,         # replace all phone numbers with a special token
                        no_numbers=False,               # replace all numbers with a special token
                        no_digits=False,                # replace all digits with a special token
                        no_currency_symbols=False,      # replace all currency symbols with a special token
                        no_punct=False,                 # fully remove punctuation
                        replace_with_url="",
                        replace_with_email="",
                        replace_with_phone_number="",
                        replace_with_number="",
                        replace_with_digit="0",
                        replace_with_currency_symbol="",
                        lang="en"                       # set to 'de' for German special handling
                        )

        blobscore = TextBlob(tw)
        wctext = wctext + tw
        polar = blobscore.sentiment.polarity
        sentiscore = sample_predict(tw, pad=True)
        sentiscore = sentiscore.tolist()
        sentiscore = sentiscore[0][0]
        if polar !=0 and polar < 0:
            negativetweets[sentiscore] = tw
            count = count + 1
            totalsenticount = totalsenticount + sentiscore
        elif polar !=0 and polar > 0:
            positivetweets[sentiscore] = tw
            count = count + 1
            positive = positive + 1
            totalsenticount = totalsenticount + sentiscore
        else:
            random = 0
    scoretotalsum = (totalsenticount/count)*100
    scorebypointfive = abs(positive/count)*100
    cloud = WordCloud().generate(wctext)
    cloud.to_file('T.png')
    f = open("T.png", "rb")
    image_data = f.read()
    b64_image = base64.standard_b64encode(image_data)
    client_id = "2cb3e1b4f5c5ea3"  # put your client ID here
    headers = {'Authorization': 'Client-ID ' + client_id}
    url = "https://api.imgur.com/3/image"
    j1 = requests.post(
        url,
        headers=headers,
        data={
            'image': b64_image,
            'type': 'base64'
        }
    )
    data = json.loads(j1.text)['data']
    wcloud = data['link']
    payload = {
        "positive": positivetweets,
        "negative": negativetweets,
        "scoretotalsum": scoretotalsum,
        "scorebypointfive": scorebypointfive,
        "wordcloud": wcloud
    }
    return jsonify(payload)


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


def get_statistics_views(youtube, video_id, token=""):
    response = youtube.videos().list(
        part='statistics, snippet',
        id=video_id).execute()

    view_count = response['items'][0]['statistics']['viewCount']
    like_count = response['items'][0]['statistics']['likeCount']
    dislike_count = response['items'][0]['statistics']['dislikeCount']
    return view_count, like_count, dislike_count


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
