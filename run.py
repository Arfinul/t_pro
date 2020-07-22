import requests
import json
import argparse

ap  = argparse.ArgumentParser()
ap.add_argument('-p','--image',required=True,help='path to input image')
args = vars(ap.parse_args())

url = "http://localhost:9000/api/image"

payload = {
			"userId": "salil",
			"sectionId": "1",
			"image": args['image']
		  }

headers = {
    'content-type': "application/json",
    }

response = requests.request("GET", url, data=json.dumps(payload), headers=headers)

print(response.status_code)

url = "http://localhost:9000/api/flc"

payload = {
			"userId": "salil",
			"sectionId": "1",
		  }

response = requests.request("GET", url, data=json.dumps(payload), headers=headers)

print(response.text)