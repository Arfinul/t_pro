import os
import requests
import datetime
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from urllib.request import urlopen
import configparser
import math
import cv2
import glob
from requests_toolbelt.multipart.encoder import MultipartEncoder

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

configparser = configparser.RawConfigParser()
configparser.read('flc_utils/screens/touchScreen/gui.cfg')

def get_class_count():
    txt_file = open("result.txt", "r").read()
    li = txt_file.split("\n")
    frame_count = li[0].split(": ")[1]
    _1lb = int(li[1].split(": ")[1])
    _2lb = int(li[2].split(": ")[1])
    _3lb = int(li[3].split(": ")[1]) 
    _1bj = int(li[4].split(": ")[1])
    _2bj = int(li[5].split(": ")[1])
    _cluster = int(li[6].split(": ")[1])
    _coarse = int(li[7].split(": ")[1])
    _perc = round(float(li[8].split(": ")[1]), 2)
    _perc = _perc if math.isnan(float(_perc)) == False else 0

    totalCount = int(_1lb + _2lb + _3lb + _1bj + _2bj + _coarse)
    return _1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc

def get_saved_status(token, userID, ccId, sectionId, farmer_id):
    payload = {}
    _perc = 0.0
    if is_internet_available():
        _1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc = get_class_count()

        head = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        }
        load = {
            "userId": int(userID),
            "ccId": int(ccId),
            "sectionId": int(sectionId),
            "assistId": int(farmer_id),
            "oneLeafBud": _1lb,
            "twoLeafBud": _2lb,
            "threeLeafBud": _3lb,
            "oneLeafBanjhi": _1bj,
            "twoLeafBanjhi": _2bj,
            "oneBudCount": "0",
            "oneBanjhiCount": "0",
            "oneLeafCount": "0",
            "twoLeafCount": "0",
            "threeLeafCount": "0",
            "qualityScore": _perc,
            "totalCount": totalCount,
        }
        payload = {'one_leaf_bud': _1lb, 'two_leaf_bud': _2lb, 'three_leaf_bud': _3lb, 
                    'one_leaf_banjhi': _1bj, 'two_leaf_banjhi': _2bj, 
                    'one_bud_count': 0, 'one_leaf_count': 0, 'two_leaf_count': 0,
                    'three_leaf_count': 0, 'one_banjhi_count': 0, 
                    'total_count': totalCount, 'quality_score': _perc}
        resp = requests.request("POST", configparser.get('gui-config', 'ip') + "/api/user/scans", data=json.dumps(load), headers=head)
        print(resp.json())
        saved = resp.json()['success']
    else:
        txt_file = open("result.txt", "r").read()
        li = txt_file.split("\n")

        with open("flc_utils/noInternetFiles/realTimeTesting.logs", "a") as out_file:
            out_file.write("Datetime " + str(datetime.datetime.now())[:-7] + "\n")
            out_file.write(txt_file)
            out_file.write("\n")
        saved = "true"
    return saved, payload, _perc

def get_payload():
    _1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc = get_class_count()
    payload = {'one_leaf_bud': _1lb, 'two_leaf_bud': _2lb, 'three_leaf_bud': _3lb, 
                'one_leaf_banjhi': _1bj, 'two_leaf_banjhi': _2bj, 
                'one_bud_count': 0, 'one_leaf_count': 0, 'two_leaf_count': 0,
                'three_leaf_count': 0, 'one_banjhi_count': 0, 
                'total_count': totalCount, 'quality_score': _perc}
    return _1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc, payload

def qualix_api(token, payload, sectionId, new_fields):
    li = []
    for i in payload:
        li.append({"analysisName": i, "totalAmount": payload[i]})
    data_ = json.dumps({
                    "section_id": str(sectionId),
                    "batch_id": "Good-001",
                    "commodity_id": "4",
                    "device_serial_no": "FLCP203208P01M3",
                    "device_type": "FLC",
                    "device_type_id": "5",
                    "farmer_code": "QX1409936521", # str(farmer_code)
                    "location": "30.703239_76.692094",
                    "lot_id": str(new_fields['lot_id']),
                    "quantity": str(new_fields['weight']),
                    "quantity_unit": "kg",
                    "sample_id": str(new_fields['sample_id']),
                    "scan_by_user_code": "128",
                    "vendor_code": "1",
                    "inst_center_type_Id":"2",
                    "inst_center_id": str(new_fields['inst_center_id']),
                    "region_id": str(new_fields['region_id']),
                    "weight": str(new_fields['weight']),
                    "commodity_category_id":"2",
                    "commodity_name":"Tea",
                    "area_covered": str(new_fields['area_covered'])
                    })
    data_ = data_.replace("'", '"')
    analyses_ = json.dumps(li)
    analyses_ = analyses_.replace("'", '"')
    mp_encoder = MultipartEncoder(
            fields={
                "data": data_,
                "analyses": analyses_,
                   }
                )
    response = requests.post(
            'http://23.98.216.140:8085/api/scan',
            data=mp_encoder,
            headers={'Content-Type': mp_encoder.content_type,
                     "Authorization": "Bearer " + token
                     }
        )
    print(response.text)
    return response.status_code

def login_api_qualix(username, password):
    access_token = ""
    customer_id = ""
    first_name = ""
    try:
        session = requests.Session()
        session.headers['User-Agent'] = 'Mozilla/5'

        querystring = {"response_type":"code",
                        "client_id": "client-mobile"
                        }
        response = session.get("http://23.98.216.140:8071/oauth/authorize", params=querystring)
        cookie = session.cookies

        mp_encoder =  MultipartEncoder(
                    fields={
                        "Signin": "Sign+In",
                        "bearer": "mobile",
                        "username": username,
                        "password": password
                    })
        headers={'Content-Type': mp_encoder.content_type}
        querystring = {"bearer":"mobile"}
        response = session.post(
                    'http://23.98.216.140:8071/login',
                    data=mp_encoder,
                    params=querystring,
                    headers=headers,
                    cookies=cookie
                )
        access_token = response.json()['access_token']
        customer_id = response.json()['user']['customer_id']
        first_name = response.json()['user']['first_name']
        return True, access_token, customer_id, first_name
    except:
        return False, access_token, customer_id, first_name

def regions_list_qualix(customer_id, token):
    region_names, region_ids = [], []
    url = "http://23.98.216.140:8072/api/regions"
    querystring = {"p":"0","l":"10","customer_id":str(customer_id)}
    headers = {'Authorization': "Bearer " + token}
    response = requests.request("GET", url, headers=headers, params=querystring)
    print("Regions list API", response.status_code)
    if response.status_code == 200:
        for i in response.json():
            region_names.append(i['region_name'])
            region_ids.append(i['region_id'])
    return region_names, region_ids

def inst_centers_list_qualix(region_id, customer_id, token):
    center_names, center_ids = [], []
    url = "http://23.98.216.140:8072/api/commercials/location"
    querystring = {"p":"0","l":"1000","customer_id":str(customer_id),"region_id":str(region_id)}
    headers = {'Authorization': "Bearer " + token}
    response = requests.request("GET", url, headers=headers, params=querystring)
    print("Centers list API", response.status_code)
    if response.status_code == 200:
        for i in response.json():
            center_names.append(i['inst_center_name'])
            center_ids.append(i['installation_center_id'])
    if len(center_names) == 0:
        center_names, center_ids = ['Demo Installation center'], ['13']
    return center_names, center_ids

def is_internet_available():
    try:
        urlopen("http://216.58.192.142", timeout=5)
        return True
    except Exception as e:
        return False

def update_spreadsheet(_1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc):
    if is_internet_available():
        # If modifying these scopes, delete the file token.pickle.
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        # The ID and range of a sample spreadsheet.
        SPREADSHEET_ID = '1OEDMdeegamLGyV9vnU8VF24dHfOl63LB4RH0GsIdfkI'
        RANGE_NAME = 'Sheet1!A:H'

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('flc_utils/token.pickle'):
            with open('flc_utils/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'flc_utils/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('flc_utils/token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)
        
        values = [
                [
                    _1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc
                ],
            ]
        body = {
            'values': values
        }
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME, 
            valueInputOption="USER_ENTERED", body=body).execute()
        print('{0} cells appended.'.format(result \
                                               .get('updates') \
                                               .get('updatedCells')))


def update_graph():
    df = pd.read_csv("flc_utils/records.csv")
    rows = df.shape[0]
    if rows > 9:
        rows = 10
        df = df.iloc[-10:, :]
    fig = plt.figure(figsize=(7,5))
    plot = sns.barplot(df.index, df.FLC)
    plot.set(ylabel='FLC %')
    plt.title("Last " + str(rows) + " FLC results", fontsize=15)
    fig.savefig('flc_utils/result.png')
    cv2_img = cv2.imread("flc_utils/result.png")
    new_img = cv2.resize(cv2_img, (400, 270))
    cv2.imwrite("flc_utils/result.png", new_img)


def free_space():
    files = glob.glob("flc_utils/trainVideo/testing/*.avi")
    if len(files) > 0:
        sizes = [os.path.getsize(i) >> 20 for i in files]
        di = dict(zip(files, sizes))
        for i in di:
            if di[i] < 50:
                os.remove(i)
        rest_files_names = glob.glob("flc_utils/trainVideo/testing/*.avi")
        if len(rest_files_names) > 0:
            rest_files_names.sort()
            delete_files = rest_files_names[:-10]
            for i in delete_files:
                os.remove(i)

def check_expiry(token):
    DEVICE = "DVPRO001"
    url = f"http://70.37.95.226:8072/api/chemical/device/{DEVICE}?v=1"
    headers = {'Authorization': "Bearer " + token}
    response = requests.request("GET", url, headers=headers)
    data = response.json()
    if data:
        EPOCH_DATE = data['crops'][0]["licence_valid"]
        FINAL_DATE = datetime.datetime.fromtimestamp(float(EPOCH_DATE)/1000.)
        NOW = datetime.datetime.now()
        return True, NOW < FINAL_DATE, (FINAL_DATE - NOW).days
    else:
        return False, "", ""