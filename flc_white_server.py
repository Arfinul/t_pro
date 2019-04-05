# Upload white image

from flask import Flask, request, Response
import jsonpickle
import os, ConfigParser

# Initialize the Flask application
app = Flask(__name__)

config = ConfigParser.ConfigParser()
config.read('flc.conf')
root_folder = config.get('input_path', 'root_folder')
test_data_dir = root_folder + '/test_data'
cwd = test_data_dir + '/1_images'


@app.route('/api/white', methods=['POST'])
def upload_white():
    os.chdir(cwd)
    file = request.files['image']
    file.save(file.filename)
    print('Uploaded - ', file.filename, '\n')
    responses = {'white_image_uploaded': file.filename
                 }
    response_pickled = jsonpickle.encode(responses)
    return Response(response=response_pickled, status=200, mimetype="application/json")


# start flask app
app.run(host="0.0.0.0", port=5001)  # Server
# app.run(port=4002)  # Local
