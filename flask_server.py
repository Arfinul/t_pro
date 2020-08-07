import requests
import json
import argparse

def server(image):
	url = "http://localhost:9000/api/image"

	payload = {
				"userId": "salil",
				"sectionId": "1",
				"image": image
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

	return response.text