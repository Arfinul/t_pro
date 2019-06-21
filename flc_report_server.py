# Upload white image

import os, configparser, time
from flask import Flask, send_file, request
from gevent import wsgi
import flc

# Initialize the Flask application
app = Flask(__name__)

config = configparser.ConfigParser()
config.read('flc.conf')
root_folder = config.get('input_path', 'root_folder')
url = root_folder + '/reports'

print("Report server started")
@app.route('/api/flc/pdf', methods=['GET'])
def pdf():
    try:
        userId = request.form['userId']
        sectionId = request.form['sectionId']

        start = time.time()
        flc.flc_with_report(userId, sectionId)
        p = sorted(os.listdir(url))
        urlpdf = url + '/' + p[-1]
        print('location - ', urlpdf)
        end = time.time()
        print('leaf image upload time = ', round((end - start), 2), ' seconds')
        return send_file(urlpdf, attachment_filename='test.pdf')

    except Exception as e:
        return str(e)


app.run(host="0.0.0.0", port=6002, threaded=True)  # Server
# app.run(port=4002)  # Local

#server = wsgi.WSGIServer(('0.0.0.0', 6002), app)
#server.serve_forever()

