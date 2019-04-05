# Upload white image

import os, ConfigParser
from flask import Flask, send_file
import flc

# Initialize the Flask application
app = Flask(__name__)

config = ConfigParser.ConfigParser()
config.read('flc.conf')
root_folder = config.get('input_path', 'root_folder')
url = root_folder + '/reports'


@app.route('/api/flc/pdf', methods=['GET'])
def pdf():
    try:
        flc.flc_with_report()
        p = sorted(os.listdir(url))
        urlpdf = url + '/' + p[-1]
        print(urlpdf)
        return send_file(urlpdf, attachment_filename='test.pdf')

    except Exception as e:
        return str(e)


app.run(host="0.0.0.0", port=5002)  # Server
# app.run(port=4002)  # Local


