# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python37_app]
from flask import Flask, render_template, request
import os
import io
from google.cloud import vision
from google.cloud.vision import types
import scraper

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\Users\Marcus\Documents\ColorCollage-e1e555b3681d.json"	#remove this
client = vision.ImageAnnotatorClient()

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

UPLOAD_FOLDER = os.path.basename('uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['image']
    if file == None:
        print("no file uploaded")
        return render_template('index.html')

    f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

    file.save(f)
    
    with io.open(f, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    labels = client.label_detection(image=image).label_annotations
    labelList = []
    colors = client.image_properties(image=image).image_properties_annotation
    colorList = []
    print('Labels:')
    for label in labels:
        print(label.description)
        labelList.append(label.description)
    sumPixels = 0
    sumScore = 0
    print(colors)
    print('Colors:')
    for color in colors.dominant_colors.colors:
        #print(color)
        sumPixels += color.pixel_fraction
        sumScore += color.score
        colorList.append((color.color.red, color.color.green, color.color.blue))
        #print('fraction: {}'.format(color.pixel_fraction))
        #print('\tr: {}'.format(color.color.red))
        #print('\tg: {}'.format(color.color.green))
        #print('\tb: {}'.format(color.color.blue))
        #print('\ta: {}'.format(color.color.alpha))
    print("sumPixels: ", sumPixels)
    print("sumScore: ", sumScore)
    for color in colors.dominant_colors.colors:
        print('color: {} pixels: {}   score: {} percentage: {} rev: {}'.format(color.color, color.pixel_fraction/sumPixels*100, color.score/sumScore*100, color.pixel_fraction/color.score, color.score/color.pixel_fraction))
    print(labelList)
    print(colorList)
    images = scraper.getUrls(labelList, colorList)
    print(images)
    return render_template('index.html')


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
