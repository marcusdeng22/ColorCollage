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
from flask import Flask, render_template, request, send_from_directory, Response, send_file
import os
import io
from google.cloud import vision
from google.cloud.vision import types
import scraper
from urllib.request import urlopen
from PIL import Image
from datetime import datetime

marcus_path = r"C:\Users\Marcus\Documents\ColorCollage-e1e555b3681d.json"
victor_path = r"C:\Users\Victor Mao\Documents\ColorCollage-7afdc23cc638.json"

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = victor_path	#remove this
client = vision.ImageAnnotatorClient()

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

UPLOAD_FOLDER = os.path.basename('uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DOWNLOAD_FOLDER = os.path.basename('downloads')
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

app.config["TEMP_FILE"] = ""
downloadFile = ""

labelList = []
colorList = []
nameList = []

@app.route('/')
def hello():
    print("hello")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file(swapLabel=None, swapColor=None, inFile=None):
    print("upload")
    if swapLabel is None and swapColor is None and inFile is None:
        try:
            file = request.files['image']
        except:
            print("no file uploaded")
            return render_template('index.html')

    if inFile is None:
        f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename.replace(" ", ""))
        file.save(f)
        app.config["TEMP_FILE"] = f
    else:
        f = app.config["TEMP_FILE"]
    
    with io.open(f, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    labelList = []
    colorList = []
    nameList = []

    labels = client.label_detection(image=image).label_annotations

    colors = client.image_properties(image=image).image_properties_annotation

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

        temp_name = scraper.get_color_name(color.color.red, color.color.green, color.color.blue)
        if (temp_name not in nameList):
            nameList.append(temp_name)
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
    print(nameList)
    if swapLabel is not None:
        i = labelList.index(swapLabel)
        labelList[0], labelList[i] = labelList[i], labelList[0]
    if swapColor is not None:
        print("swapping")
        i = nameList.index(swapColor)
        print(i)
        colorList[0], colorList[i] = colorList[i], colorList[0]
        nameList[0], nameList[i] = nameList[i], nameList[0]
    print(labelList)
    print(colorList)
    print(nameList)
    images = scraper.getUrls(labelList, colorList)

    images.insert(4, str(f))
    print(images)

    finalImage = Image.new("RGB", (600, 600))
    for x in range(3):
        for y in range(3):
            if (x*3 + y == 4):
                tempImage = Image.open(images[x*3 + y])
            else:
                tempImage = Image.open(urlopen(images[x*3 + y]))
            width, height = tempImage.size
            ratio = min(width, height) / 200
            width /= ratio
            height /= ratio
            tempImage.thumbnail((width, height), Image.ANTIALIAS)
            cropSize = 200
            width, height = tempImage.size
            tempImage = tempImage.crop(((width/2)-100, (height/2)-100, (width/2)+100, (height/2)+100))
            finalImage.paste(im=tempImage, box=(y*200, x*200))
    downloadFile = str(datetime.now()).replace(" ", "_").replace(".", "-").replace(":", "-") + ".jpg"
    #app.config["TEMP_FILE"] = os.path.join(app.config['DOWNLOAD_FOLDER'], downloadFile)
    finalImage.save(os.path.join(app.config['DOWNLOAD_FOLDER'], downloadFile))
    print("created file: ", downloadFile)
    return render_template('results.html',
                            urls = images,
                            labels = labelList,
                            colors = colorList,
                            colorNames = nameList,
                            filePath = downloadFile)

@app.route('/value_select', methods=['GET', 'POST'])
def search_label():
    print("search labels")
    #option = request.form["label"]
    #print(option)
    #options = request.form.getlist("label")
    #print(options)
    #opt = request.form.get("label")
    #print(opt)
    print(request.form)
    print(request.form.get("labelBtn"))
    print(request.form.get("colorBtn"))
    if len(request.form.getlist("labelBtn")) > 0:
        print("swapping labels")
        return upload_file(swapLabel=request.form.get("labelBtn"), inFile=app.config["TEMP_FILE"])
    print("swapping colors")
    return upload_file(swapColor=request.form.get("colorBtn"), inFile=app.config["TEMP_FILE"])

@app.route('/uploads/<filename>')
def send_image(filename):
    print("send image")
    print(labelList)
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route('/downloads/<filename>', methods=['GET'])
def download(filename):
    print("download image")
    return send_file(os.path.join(app.config["DOWNLOAD_FOLDER"], filename), mimetype="image/jpg")

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
