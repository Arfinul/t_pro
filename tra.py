import glob
import os, shutil
import time
import zipfile
import jsonpickle, configparser
from flask import Flask, request, Response, send_file
# from gevent import wsgi
from werkzeug.utils import secure_filename
import PIL.Image
import cv2
import io, numpy as np
import sys

import warnings
import datetime

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload():
    try:
        resp = None
        if 'userId' not in request.form:
            resp = {'success': 'false', 'message': "userId is missing", 'status': 'fail'}
        if 'sectionId' not in request.form:
            resp = {'success': 'false', 'message': "sectionId is missing", 'status': 'fail'}
        if 'class' not in request.form:
            resp = {'success': 'false', 'message': "class is missing", 'status': 'fail'}
        if 'image' not in request.files:
            resp = {'success': 'false', 'message': "image is missing", 'status': 'fail'}
        if resp is not None:
            response_pickled = jsonpickle.encode(resp)
            return Response(response=response_pickled, status=400, mimetype="application/json")
        
        userId = request.form['userId']
        sectionId = request.form['sectionId']
        className = request.form['class']
        imageName = "TRAgNext/" + className + '/' + datetime.datetime.now().strftime("%d-%m-%y %H:%M:%S")  + '_u-' + userId + '_s-' + sectionId + '_c-' + className  + ".jpg"

        if not os.path.exists("TRAgNext/" + className):
            os.makedirs("TRAgNext/" + className)
        start = time.time()
        if request.method == 'POST':
            file = request.files['image']
            if file and allowed_file(file.filename):
                print('\nImage Checking ... Wait !!!\n')
                file.save(imageName)
                print('Uploaded tea image - ', file.filename)
                end = time.time()
                print('Image upload time = ', round((end - start), 2), ' seconds')
                responses = {'tea_image_uploaded': imageName,
                             'success': 'true',
                             'message': 'image accepted',
                             'status': 'pass'
                             }
            if not allowed_file(file.filename):
                print('unsupported file')
                wrong_extension = '.' in file.filename and file.filename.rsplit('.', 1)[1].lower()
                responses = {'success': 'false',
                             'message': str(wrong_extension) + ' not supported',
                             'status': 'fail'
                             }

        response_pickled = jsonpickle.encode(responses)
        return Response(response=response_pickled, status=200, mimetype="application/json")
    except Exception as e:
        responses_fail = {'success': 'false',
                          'message': str(e),
                          'status': 'fail'
                          }
        response_pickled = jsonpickle.encode(responses_fail)
        return Response(response=response_pickled, status=500, mimetype="application/json")

app.run(host="0.0.0.0", port=8000, threaded=True)  # Server