# Upload multiple images and prpocess flc

import glob
import os, shutil
import flc
import time
import zipfile
import jsonpickle, configparser
from flask import Flask, request, Response, send_file
from gevent import wsgi
from werkzeug.utils import secure_filename
import PIL.Image
import cv2
import io, numpy as np
# Initialize the Flask application
#####################
import fastai
import sys

from fastai.vision import *
import warnings

warnings.filterwarnings("ignore")

PATH = '/home/agnext/Documents/tea_infer/'  # Location of .pkl file file

learn = load_learner(PATH, test=ImageList.from_folder('test'))

###################

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('flc.conf')

root_folder = config.get('input_path', 'root_folder')
test_data_dir = root_folder + '/test_data'

image_dir = '/1_images'
cropped_dir = '/2_cropped_images'
result_dir = '/3_resulted_images'
augmented_dir = '/4_augmented'
join_dir = '/5_join'
tracked_image_dir = '/6_trapped_images'
pdf_dir = '/7_pdf_files'
url = root_folder + '/reports'

subdir_list = None
# ALLOWED_EXTENSIONS = {'zip'}
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

print("Flc server started")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/white', methods=['POST'])
def upload_white():
    userId = request.form['userId']
    sectionId = request.form['sectionId']

    cwd = test_data_dir + '/u-' + userId + '/s-' + sectionId + '/1_images'
    print(cwd)

    os.makedirs(cwd, exist_ok=True)
    os.chdir(cwd)

    start = time.time()

    file = request.files['image']
    file.save(file.filename)
    end = time.time()
    print('Uploaded white image - ', file.filename)
    print('white image upload time = ', round((end - start), 2), ' seconds')
    responses = {'white_image_uploaded': file.filename
                 }
    response_pickled = jsonpickle.encode(responses)
    return Response(response=response_pickled, status=200, mimetype="application/json")


# Route http posts to this method
@app.route('/api/image', methods=['POST'])
def upload_image():
    try:
        userId = request.form['userId']
        sectionId = request.form['sectionId']
        user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId

        test_images = user_dir + image_dir
        os.makedirs(test_images, exist_ok=True)
        cropped_path = user_dir + cropped_dir
        os.makedirs(cropped_path, exist_ok=True)
        result_image_path = user_dir + result_dir
        os.makedirs(result_image_path, exist_ok=True)
        augmented_path = user_dir + augmented_dir
        os.makedirs(augmented_path, exist_ok=True)
        join_path = user_dir + join_dir
        os.makedirs(join_path, exist_ok=True)
        tracked_images_path = user_dir + tracked_image_dir
        os.makedirs(tracked_images_path, exist_ok=True)
        pdf_path = user_dir + pdf_dir
        os.makedirs(pdf_path, exist_ok=True)

        os.chdir(test_images)
        start = time.time()

        # Upload multiple images
        if request.method == 'POST':
            file = request.files['image']
            if file and allowed_file(file.filename):
                print('...............................\nImage Checking ... Wait !!!\n')
                file.save(file.filename)
                print('Uploaded tea image - ', file.filename)
                end = time.time()
                print('leaf image upload time = ', round((end - start), 2), ' seconds')
                img = open_image(file.filename)
                pred_class, pred_idx, outputs = learn.predict(img)
                print("Predicted Class = ", pred_class)
                print("Prediction Probability = %.2f" % (outputs.numpy()[1] * 100))

                if str(pred_class) == 'Normal':
                    responses = {'tea_image_uploaded': file.filename,
                                 'success': 'true',
                                 'message': 'image accepted',
                                 'status': 'pass'
                                 }
                if str(pred_class) == 'Abnormal':
                    os.remove(test_data_dir + '/u-' + userId + '/s-' + sectionId + image_dir + '/' + file.filename)
                    responses = {'success': 'true',
                                 'message': 'image rejected',
                                 'status': 'fail'
                                 }

            if not allowed_file(file.filename):
                print('unsupported file')
                wrong_extension = '.' in file.filename and file.filename.rsplit('.', 1)[1].lower()
                responses = {'success': 'false',
                             'message': str(wrong_extension) + ' not supported',
                             'status': 'fail'
                             }

        # Upload single image
        # file = request.files['image']
        # file.save(file.filename)
        # print('Uploaded - ', file.filename, '\n')

        response_pickled = jsonpickle.encode(responses)
        return Response(response=response_pickled, status=200, mimetype="application/json")
    except Exception as e:
        responses_fail = {'success': 'false',
                          'message': str(e),
                          'status': 'fail'
                          }
        response_pickled = jsonpickle.encode(responses_fail)
        return Response(response=response_pickled, status=200, mimetype="application/json")


@app.route('/api/flc', methods=['POST'])
def classification_flc_only():
    try:
        userId = request.form['userId']
        sectionId = request.form['sectionId']

        start = time.time()
        lb_1, lb_2, lb_3, lbj_1, lbj_2, lbj_3, b_1, bj_1, l_1, l_2, l_3, total = flc.flc_as_per_best_among_7_rotation_by_priotising_leaf_def(
            userId, sectionId)
        end = time.time()
        time_cons = (end - start)
        print('classification time = ', round(time_cons, 2), ' seconds')
        responses = {'1LeafBud_Count': lb_1,
                     '2LeafBud_Count': lb_2,
                     '3LeafBud_Count': lb_3,
                     '1LeafBanjhi_Count': lbj_1,
                     '2LeafBanjhi_Count': lbj_2,
                     '3LeafBanjhi_Count': lbj_3,
                     '1Bud_Count': b_1,
                     '1Banjhi_Count': bj_1,
                     '1Leaf_Count': l_1,
                     '2Leaf_Count': l_2,
                     '3Leaf_Count': l_3,
                     'Total_Bunches': total,
                     'Time Taken(seconds)': round(time_cons, 2)
                     }
        response_pickled = jsonpickle.encode(responses)
        return Response(response=response_pickled, status=200, mimetype="application/json")
    except Exception as e:
        try:
            print("Below is the Exceptional Error")
            print(e)
            if '209' in str(e):
                shutil.rmtree(test_data_dir + '/u-' + userId + '/s-' + sectionId + '/')
                responses = {'status': 'Images must have same resolution'
                             }
                response_pickled = jsonpickle.encode(responses)
                return Response(response=response_pickled, status=200, mimetype="application/json")
            if 'assignment' in str(e):
                shutil.rmtree(test_data_dir + '/u-' + userId + '/s-' + sectionId + '/')
                responses = {'status': 'GPU Memory Error'
                             }
                response_pickled = jsonpickle.encode(responses)
                return Response(response=response_pickled, status=200, mimetype="application/json")
            else:
                shutil.rmtree(test_data_dir + '/u-' + userId + '/s-' + sectionId + '/')
                responses = {'status': 'Error - Try Again'
                             }
                response_pickled = jsonpickle.encode(responses)
                return Response(response=response_pickled, status=200, mimetype="application/json")
        except Exception as e:
            return str(e)


@app.route('/api/bigdata/flc/cropped/all_rotation/pdf', methods=['GET'])
def pdf():
    print("Big Data Report server started")
    try:
        start = time.time()
        userId = request.form['userId']
        sectionId = request.form['sectionId']
        flc.flc_with_report_without_filter(userId, sectionId)
        p = sorted(os.listdir(url))
        urlpdf = url + '/' + p[-1]
        print('location - ', urlpdf)
        end = time.time()
        print('leaf image upload time = ', round((end - start), 2), ' seconds')
        return send_file(urlpdf, attachment_filename='test.pdf')

        # except Exception as e:
        # return str(e)
    except Exception as e:
        try:
            print("Below is the Exceptional Error")
            print(e)
            if 'empty' in str(e):
                shutil.rmtree(test_data_dir + '/u-' + userId + '/s-' + sectionId + '/')
                responses = {'status': 'GPU Memory Error'
                             }
                response_pickled = jsonpickle.encode(responses)
                return Response(response=response_pickled, status=200, mimetype="application/json")
            else:
                shutil.rmtree(test_data_dir + '/u-' + userId + '/s-' + sectionId + '/')
                responses = {'status': 'Error - Try Again'
                             }
                response_pickled = jsonpickle.encode(responses)
                return Response(response=response_pickled, status=200, mimetype="application/json")
        except Exception as e:
            return str(e)


@app.route('/api/bigdata/flc/pdf', methods=['GET'])
def pdf_cropped_all_rotation():
    print("Big Data Report server started")
    try:
        start = time.time()
        userId = request.form['userId']
        sectionId = request.form['sectionId']
        flc.flc_with_report_for_cropped(userId, sectionId)
        p = sorted(os.listdir(url))
        urlpdf = url + '/' + p[-1]
        print('location - ', urlpdf)
        end = time.time()
        print('leaf image upload time = ', round((end - start), 2), ' seconds')
        return send_file(urlpdf, attachment_filename='test.pdf')

        # except Exception as e:
        # return str(e)
    except Exception as e:
        try:
            print("Below is the Exceptional Error")
            print(e)
            if 'empty' in str(e):
                shutil.rmtree(test_data_dir + '/u-' + userId + '/s-' + sectionId + '/')
                responses = {'status': 'GPU Memory Error'
                             }
                response_pickled = jsonpickle.encode(responses)
                return Response(response=response_pickled, status=200, mimetype="application/json")
            else:
                shutil.rmtree(test_data_dir + '/u-' + userId + '/s-' + sectionId + '/')
                responses = {'status': 'Error - Try Again'
                             }
                response_pickled = jsonpickle.encode(responses)
                return Response(response=response_pickled, status=200, mimetype="application/json")
        except Exception as e:
            return str(e)


@app.route('/api/bigdata', methods=['POST'])
def upload_big_data():
    userId = request.form['userId']
    sectionId = request.form['sectionId']
    user_dir = test_data_dir + '/u-' + userId + '/s-' + sectionId

    test_images = user_dir + cropped_dir
    os.makedirs(test_images, exist_ok=True)
    result_image_path = user_dir + result_dir
    os.makedirs(result_image_path, exist_ok=True)
    augmented_path = user_dir + augmented_dir
    os.makedirs(augmented_path, exist_ok=True)
    join_path = user_dir + join_dir
    os.makedirs(join_path, exist_ok=True)
    tracked_images_path = user_dir + tracked_image_dir
    os.makedirs(tracked_images_path, exist_ok=True)
    pdf_path = user_dir + pdf_dir
    os.makedirs(pdf_path, exist_ok=True)

    print('started uploading Big Data ...')
    os.chdir(test_images)
    start = time.time()
    if request.method == 'POST':
        # print('\nUploading the file ... Wait !!!')
        file = request.files['bigData']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(test_images, filename))
            zip_ref = zipfile.ZipFile(os.path.join(test_images, filename), 'r')
            zip_ref.extractall(test_images)
            zip_ref.close()
            r = glob.glob(test_images + '/*.zip')
            for i in sorted(r):
                os.remove(i)
            for x, y, z in os.walk(test_images):
                subdir_list = y
                break
            for each in subdir_list:
                os.system('mv ' + test_images + '/' + each + '/* ' + test_images)
                os.system('rm -r ' + test_images + '/' + each)
    end = time.time()
    time_cons = (end - start)
    image_count = len([name for name in os.listdir(test_images) if os.path.isfile(os.path.join(test_images, name))])
    print('Uploaded - ', file.filename)
    print('Time_Taken(seconds) - ', round(time_cons, 2))
    print('Total images - ', image_count)
    responses = {'Uploaded': file.filename,
                 'image_counts': image_count,
                 'Time_Taken(seconds)': round(time_cons, 2)
                 }
    response_pickled = jsonpickle.encode(responses)
    return Response(response=response_pickled, status=200, mimetype="application/json")


@app.route('/api/cleandir', methods=['POST'])
def post():
    try:
        userId = request.form['userId']
        sectionId = request.form['sectionId']

        if os.path.exists(test_data_dir + '/u-' + userId + '/s-' + sectionId):
            shutil.rmtree(test_data_dir + '/u-' + userId + '/s-' + sectionId + '/')
            print('Deleted the directory - ', sectionId, ', under ', userId)
            responses = {'status': 'Reset_Done'
                         }
            response_pickled = jsonpickle.encode(responses)
            return Response(response=response_pickled, status=200, mimetype="application/json")
        else:
            print('Deleted the directory - ', sectionId, ', under ', userId)
            responses = {'status': 'Fail - directory not found'
                         }
            response_pickled = jsonpickle.encode(responses)
            return Response(response=response_pickled, status=200, mimetype="application/json")

    except Exception as e:
        return str(e)


# start flask app
app.run(host="0.0.0.0", port=9000, threaded=True)  # Server
# sapp.run(port=6000)  # Local

# server = wsgi.WSGIServer(('0.0.0.0', 6000), app)
# server.serve_forever()
