# Upload multiple images and prpocess flc

import glob
import os
import flc
import time
import zipfile

import jsonpickle
from flask import Flask, request, Response
from werkzeug.utils import secure_filename

# Initialize the Flask application
app = Flask(__name__)

# cwd = '/home/agnext/Documents/Flc_copy/test_data/1_images'
cwd = '/home/agnext/Music/flc_2/test_data/1_images'
subdir_list = None
ALLOWED_EXTENSIONS = {'zip'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Route http posts to this method
@app.route('/api/image', methods=['POST'])
def upload_image():
    os.chdir(cwd)
    print('Uploading the file ... Wait !!!\n')

    # Upload multiple images
    if request.method == 'POST' and 'image' in request.files:
        for file in request.files.getlist('image'):
            file.save(file.filename)
            print('Uploaded - ', file.filename, '\n')

    # Upload single image
    # file = request.files['image']
    # file.save(file.filename)
    # print('Uploaded - ', file.filename, '\n')

    responses = {'Uploaded': file.filename
                 }
    response_pickled = jsonpickle.encode(responses)
    return Response(response=response_pickled, status=200, mimetype="application/json")


@app.route('/api/image/flc', methods=['POST'])
def classification_flc_only():
    start = time.time()
    cc, fc = flc.flc_only()
    # cc, fc = flc.one_and_all_testing()
    end = time.time()
    time_cons = (end - start)
    responses = {'Fine_Count': fc,
                 'Coarse_Count': cc,
                 'Time Taken(seconds)': round(time_cons, 2)
                 }
    response_pickled = jsonpickle.encode(responses)
    return Response(response=response_pickled, status=200, mimetype="application/json")


@app.route('/api/report/flc', methods=['POST'])
def classification_flc_with_report():
    start = time.time()
    fc, cc = flc.flc_with_report()
    # cc, fc = flc.one_and_all_testing()
    end = time.time()
    time_cons = (end - start)
    responses = {'Fine_Count': fc,
                 'Coarse_Count': cc,
                 'Time Taken(seconds)': round(time_cons, 2)
                 }
    response_pickled = jsonpickle.encode(responses)
    return Response(response=response_pickled, status=200, mimetype="application/json")


@app.route('/api/bigdata', methods=['POST'])
def upload_big_data():
    os.chdir(cwd)
    start = time.time()
    if request.method == 'POST':
        # print('\nUploading the file ... Wait !!!')
        file = request.files['bigData']
        print('1')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(cwd, filename))
            zip_ref = zipfile.ZipFile(os.path.join(cwd, filename), 'r')
            zip_ref.extractall(cwd)
            zip_ref.close()
            r = glob.glob(cwd + '/*.zip')
            for i in sorted(r):
                os.remove(i)
            for x, y, z in os.walk(cwd):
                subdir_list = y
                break
            for each in subdir_list:
                os.system('mv ' + cwd + '/' + each + '/* ' + cwd)
                os.system('rm -r ' + cwd + '/' + each)
    end = time.time()
    time_cons = (end - start)
    image_count = len([name for name in os.listdir(cwd) if os.path.isfile(os.path.join(cwd, name))])
    print('Uploaded - ', file.filename)
    print('Time_Taken(seconds) - ', round(time_cons, 2))
    print('Total images - ', image_count)
    responses = {'Uploaded': file.filename,
                 'image_counts': image_count,
                 'Time_Taken(seconds)': round(time_cons, 2)
                 }
    response_pickled = jsonpickle.encode(responses)
    return Response(response=response_pickled, status=200, mimetype="application/json")


# start flask app
app.run(host="0.0.0.0", port=5000)  # Server
#sapp.run(port=6000)  # Local



