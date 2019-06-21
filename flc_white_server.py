# Upload white image

from flask import Flask, request, Response
from gevent import wsgi
import jsonpickle
import os, configparser, time

# Initialize the Flask application
app = Flask(__name__)

config = configparser.ConfigParser()
config.read('flc.conf')
root_folder = config.get('input_path', 'root_folder')
test_data_dir = root_folder + '/test_data'

print("White image upload server started")
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


# start flask app
app.run(host="0.0.0.0", port=8001, threaded=True)  # Server
# app.run(port=4002)  # Local

#server = wsgi.WSGIServer(('0.0.0.0', 6001), app)
#server.serve_forever()
