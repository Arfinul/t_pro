import os
import requests
import datetime
import json
import gc
import configparser
from requests_toolbelt.multipart.encoder import MultipartEncoder

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
    time_taken = li[9].split(": ")[1]
    # _perc = round(float(li[8].split(": ")[1]), 2)
    # _perc = _perc if math.isnan(float(_perc)) == False else 0

    totalCount = int(_1lb + _2lb + _3lb + _1bj + _2bj + _coarse)

    _1lb = int(round(_1lb * 1.1346, 0))
    _2lb = int(round(_2lb * 1.2006, 0))
    _1bj = int(round(_1bj * 1.3288, 0))
    _3lb = int(round(_3lb * 1.4213, 0))
    _2bj = int(round(_2bj * 0.85, 0))

    _coarse = int(round(_coarse - totalCount * 0.012, 0))
    _coarse = _coarse if _coarse > 0 else 0

    totalCount = _1lb + _2lb + _3lb + _1bj + _2bj + _coarse
    # rainy = int(self.rainy_season.get())

    # try:
    #     if rainy == 0:
    #         print("Non - Rainy season")
    #         _perc = round(((_1lb + _2lb + (_3lb/2) + _1bj) / totalCount)*100, 2)
    #     else:
    #         print("Rainy season")
    #         _perc = round(((_1lb + _2lb + (_3lb*3/4) + _1bj) / totalCount)*100, 2)
    # except Exception as e:
    #     print(e)
    #     _perc = 0

    try:
        _perc = round(((_1lb + _2lb + (_3lb/2) + _1bj) / totalCount)*100, 2)
    except Exception as e:
        print(e)
        _perc = 0

    with open("factor.txt", "w") as factor:
        factor.write("Frame: "+ frame_count + "\n")
        factor.write("1LB: " + str(_1lb) + "\n")
        factor.write("2LB: " + str(_2lb) + "\n")
        factor.write("3LB: " + str(_3lb) + "\n")
        factor.write("1Bj: " + str(_1bj) + "\n")
        factor.write("2Bj: " + str(_2bj) + "\n")
        factor.write("Coarse: " + str(_coarse) + "\n")
        factor.write("Cluster: " + str(_cluster) + "\n")
        factor.write("Total: " + str(totalCount) + "\n")
        factor.write("FLC % " + str(_perc) + "\n")
        factor.write("Time: " + time_taken + "\n")
    gc.collect()
    
    return _1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc

def get_saved_status(token, userID, ccId, sectionId, farmer_id):
    payload = {},
    _perc = 0.0
    if configparser.get('gui-config', 'internet') == 'true':
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

def qualix_api(payload, sectionId, farmer_code, new_fields):
    li = []
    for i in payload:
        li.append({"analysisName": i, "totalAmount": payload[i]})
    print(li)
    mp_encoder = MultipartEncoder(
            fields={
                "data": json.dumps({
                    "section_id": sectionId,
                    "batch_id": new_fields['batchId'],
                    "commodity_id": "4",
                    "device_serial_no": new_fields['device_serial_no'],
                    "device_type": "FLC",
                    "device_type_id": "5",
                    "farmer_code": farmer_code,
                    "location": "30.703239_76.692094",
                    "lot_id": new_fields['lot_id'],
                    "quantity": new_fields['weight'],
                    "quantity_unit": "tonnes",
                    "sample_id": new_fields['sample_id'],
                    "scan_by_user_code": "128",
                    "vendor_code": "1",
                    "inst_center_type_Id":"2",
                    "inst_center_id": new_fields['inst_center_id'],
                    "region_id": new_fields['region_id'],
                    "weight": new_fields['weight'],
                    "commodity_category_id":"2",
                    "commodity_name":"Tea",
                    "area_covered": new_fields['area_covered']
                    }),
                "analyses": json.dumps(li),
                   }
                )
    response = requests.post(
            'http://23.98.216.140:8085/api/scan',
            data=mp_encoder,
            headers={'Content-Type': mp_encoder.content_type,
                     "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2VtYWlsIjoiZGVtb29wZXJhdG9yQGdtYWlsLmNvbSIsInVzZXJfZm5hbWUiOiJPcGVyYXRvciIsInVzZXJfbmFtZSI6ImRlbW9vcGVyYXRvckBnbWFpbC5jb20iLCJjdXN0b21lcl91dWlkIjoiOGE1YTU2YTAtNGY0MS00YTFjLWFiMTQtNmQ1MWFlNjIyZDBiIiwicm9sZXMiOlsib3BlcmF0b3IiXSwiaXNzIjoiUXVhbGl4IiwidXNlcl9sbmFtZSI6Ik9wZXJhdG9yIiwiY2xpZW50X2lkIjoiY2xpZW50LW1vYmlsZSIsInVzZXJfdXVpZCI6Ijc3Nzk3NTkwLTlmMzYtNDM5Ni1iMTA2LTcwNThiZjFkMTc3ZiIsInVzZXJfdHlwZSI6IkNVU1RPTUVSIiwidXNlcl9pZCI6MTg4LCJ1c2VyX21vYmlsZSI6Ijk2NTY1ODU2OTUiLCJzY29wZSI6WyJhbGwiXSwidXNlcl9oaWVyYXJjaHkiOm51bGwsImN1c3RvbWVyX25hbWUiOiJEZW1vIGN1c3RvbWVyIiwiZXhwIjoxNTk5MDEyMjE0LCJjdXN0b21lcl9pZCI6OTEsImp0aSI6Ijc5NDM3NzRiLWY0MTQtNDg1Yi1hZmZiLWYyNGRkODRiOWExOCJ9.KKW07ptym9_ftVoD1BhxBQ1yoal60NkK1gGh62lBT7XZfDKlKGwfIHthQHZRkAvhzpta2y3ePS5LHobyoF4Cir29dodSnM6f-CrNny5yUCQsyysVjVQSENRBFGBB9MzQ_0dU76UU5Ix-uj4N_IXMhaswX8hUn2GLdfKiCqPivqHkyL-jGT6QmFW2rj_GnqGyGZNumMysSm-xFhvIySMjkVgm8hT2DBp6QygTSwitMH3N1eogKIb76VJdvE9IDbUYjKll0AZqkVx0omWBCth9-sCiWkuzBXBPmQ48OFYTZN0j3vFO019IlAve2Ioj7_ewj_Qa2d2ni0uoOkm6RQqc7A"
                     }
        )
    print(response.text)
    return response.status_code

def token_api_qualix():
    url = "http://23.98.216.140:8071/oauth/authorize"
    querystring = {"response_type":"code","client_id":"client-mobile"}
    response = requests.request("GET", url, params=querystring)
    print(response.status_code)

def login_api_qualix():
    success = False
    token = ''
    customer_id = 0
    mp_encoder = MultipartEncoder(
            fields={
                "Signin": "Sign+In",
                "bearer": "mobile",
                "username": "demooperator@gmail.com",
                "password": "Specx123!"
                }
                )
    querystring = {"bearer":"mobile"}
    response = requests.post(
            'http://23.98.216.140:8085/api/scan',
            data=mp_encoder,
            headers={'Content-Type': mp_encoder.content_type},
            params=querystring
        )
    print(response.status_code)
    if response.status_code == 200:
        token = response.json()['access_token']
        customer_id = response.json()['user']['customer_id']
    return success, token, customer_id

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
