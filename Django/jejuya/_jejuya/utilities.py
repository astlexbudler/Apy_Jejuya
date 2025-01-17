import random
import string
from math import radians, sin, cos, asin, sqrt

import json
import requests
from datetime import datetime
from pyproj import Proj, transform
import haversine
import google.auth.transport.requests
from google.oauth2 import service_account
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from . import models as mo
from . import utilities as ut
from . import daos as do

from colorama import Fore, Back, Style, init
init(autoreset=True)



def get_rand_id(length): # make random id(str + num)
    # first letter is always alphabet
    return ''.join(random.choices(string.ascii_letters, k=1)) + ''.join(random.choices(string.ascii_letters + string.digits, k=length-1))

def get_now_dt(): # "0000-00-00 00:00"
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def get_datetime_from_dt(dt): # 날짜 문자열을 datetime으로
    return datetime.strptime(dt, "%Y-%m-%d %H:%M")

def get_dt_from_datetime(dt): # datetime을 날짜 문자열로
    return dt.strftime("%Y-%m-%d %H:%M")

def send_apppush(title, message): # 앱 푸시 메세지 발송 2024-11-26일 업데이트
    bucket = 'cixt7hh3u'
    app_id = 't29ndrbx' # jejuya's app id
    tokens = []
    docs = requests.get(f"https://firestore.googleapis.com/v1/projects/{bucket}/databases/(default)/documents/{app_id}").json()["documents"]
    for doc in docs:
        doc_token = doc["name"].split("/")[-1] # user's device token
        doc_ad = doc["fields"]["isCommertialPushAllow"]["booleanValue"] # user's ad allow
        doc_push = doc["fields"]["isPushAllow"]["booleanValue"] # user's push notification allow
        doc_id = doc["fields"]["loginId"]["stringValue"] # user's id
        if doc_push == False:
            continue
        tokens.append({
            "token": doc_token
        })

    # send push
    scope = ["https://www.googleapis.com/auth/firebase.messaging"]
    cred = service_account.Credentials.from_service_account_file(f"_alrimi/{bucket}.json", scopes=scope)
    request = google.auth.transport.requests.Request()
    cred.refresh(request)
    access_token = cred.token

    for token in tokens:
        push_data = {
            "message": {
                "token": token,
                "notification": {
                    "title": title,
                    "body": message,
                }
            }
        }
        requests.post(f'https://fcm.googleapis.com/v1/projects/{bucket}/messages:send',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json; UTF-8',
            },
            data=json.dumps(push_data)
        )
    return {"result": "success"}

def send_apppush(title, message): # send app push message. no limit.
    bucket = 'cixt7hh3u'

    try:
        # get tokens
        tokens = []

        all_accounts = mo.ACCOUNT.objects.all()
        for account in all_accounts:
            if account.device_token != '' or account.device_token != None:
                tokens.append({
                    "token": account.device_token
                })
        # send push
        scope = ["https://www.googleapis.com/auth/firebase.messaging"]
        cred = service_account.Credentials.from_service_account_file(f"{bucket}.json", scopes=scope)
        request = google.auth.transport.requests.Request()
        cred.refresh(request)
        access_token = cred.token

        for token in tokens:
            push_data = {
                "message": {
                    "token": token,
                    "notification": {
                        "title": title,
                        "body": message,
                    }
                }
            }
            requests.post(f'https://fcm.googleapis.com/v1/projects/{bucket}/messages:send',
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json; UTF-8',
                },
                data=json.dumps(push_data)
            )
        return {"result": "success"}
    except Exception as e:
        return {"error": str(e)}

def get_ip(request): # get user's ip address from request
    return request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')

def print_dict_structure(d): # print dictionary structure
    structure = ""
    try:
        if type(d) == list:
            d = d[0]
        for key, value in d.items():
            if type(value) == dict:
                structure += f"{key}({print_dict_structure(value)}), "
            structure += f"{key}, "
        structure = structure[:-2]
    except:
        pass
    return structure

def print_info_n_return(request, title, contexts, path): # print debug info and return context
    if settings.DEBUG:
        print(f"\n\n\n{Fore.GREEN}[{get_now_dt()}]{title}{Fore.RESET}")
        print(f"{Fore.BLUE}SESSION:{Fore.RESET} {print_dict_structure(request.session)}")
        print(f"{Fore.BLUE}GET:{Fore.RESET} {print_dict_structure(request.GET)}")
        print(f"{Fore.BLUE}POST:{Fore.RESET} {print_dict_structure(request.POST)}")
        print(f"{Fore.LIGHTMAGENTA_EX}contexts:{Fore.RESET} ")
        for key, value in contexts.items():
            print (f"{Fore.LIGHTMAGENTA_EX}{key}:{Fore.RESET} {print_dict_structure(value)}")
    if request.method == 'POST':
        return JsonResponse(contexts)
    else:
        return render(request, path, contexts)

def address_to_coords(address): # 주소를 기반으로 좌표로 변경
    destination = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    client_id = "jqnqizu970"
    client_secret = "QJgaBXPXVRVNbSUBQexgMJsSW7R6JRQ7iAqYhrG9"
    query = address

    url = destination + "?query=" + query

    header = {
        'X-NCP-APIGW-API-KEY-ID': client_id,
        'X-NCP-APIGW-API-KEY': client_secret,
    }
    response = requests.get(url, headers=header)
    response = response.json()

    latitude = response["addresses"][0]["y"]
    longitude = response["addresses"][0]["x"]

    return {
        "latitude": latitude,
        "longitude": longitude,
    }

def coords_to_address(lat, lng): # 좌표를 기반으로 주소로 변경
    destination = "https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc"
    client_id = "jqnqizu970"
    client_secret = "QJgaBXPXVRVNbSUBQexgMJsSW7R6JRQ7iAqYhrG9"
    coords = str(lng) + "," + str(lat)

    url = destination + "?coords=" + coords + "&output=json&order=addr"

    header = {
        'X-NCP-APIGW-API-KEY-ID': client_id,
        'X-NCP-APIGW-API-KEY': client_secret,
    }

    response = requests.get(url, headers=header).json()
    print(response)

    return response["results"][0]["region"]["area1"]["alias"] + " " + response["results"][0]["region"]["area2"]["name"] + " " + response["results"][0]["region"]["area3"]["name"]

def get_distance(dict): # 두 좌표간 거리를 m로 계산
    coordinate1 = (float(dict['latitude1']), float(dict['longtitude1']))
    coordinate2 = (float(dict['latitude2']), float(dict['longtitude2']))
    try:
        return int(haversine.haversine(coordinate1, coordinate2, unit='m'))
    except:
        return 0

def get_katec_coordinates(dict): # wgs좌표계를 katec 좌표계로 전환
    wgs_x = dict["longtitude"]
    wgs_y = dict["latitude"]
    katec_coordinates = {}
    WGS84 = {'proj': 'latlong', 'datum': 'WGS84', 'ellps': 'WGS84'}
    KATEC = {'proj': 'tmerc', 'lat_0': '38N', 'lon_0': '128E',
             'ellps': 'bessel', 'x_0': '400000', 'y_0': '600000',
             'k': '0.9999', 'units': 'm',
             'towgs84': '-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43'}
    inProj = Proj(**WGS84)
    outProj = Proj(**KATEC)
    coords = transform(inProj, outProj, wgs_x, wgs_y)
    katec_coordinates["katec_x"] = str(coords[0])
    katec_coordinates["katec_y"] = str(coords[1])
    return katec_coordinates

def get_wgs_coordinates(dict):# katec좌표계를 wgs 좌표계로 전환
    wgs_coordinates = {}
    WGS84 = {'proj': 'latlong', 'datum': 'WGS84', 'ellps': 'WGS84'}
    KATEC = {'proj': 'tmerc', 'lat_0': '38N', 'lon_0': '128E',
             'ellps': 'bessel', 'x_0': '400000', 'y_0': '600000',
             'k': '0.9999', 'units': 'm',
             'towgs84': '-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43'}
    inProj = Proj(**KATEC)
    outProj = Proj(**WGS84)
    coords = transform(inProj, outProj, dict["katec_x"], dict["katec_y"])
    wgs_coordinates["longtitude"] = str(coords[0])
    wgs_coordinates["latitude"] = str(coords[1])
    return wgs_coordinates


def calc_distance(latitude1, longitude1, latitude2, longitude2):
    # 위도와 경도를 라디안 단위로 변환
    lon1, lat1, lon2, lat2 = map(radians, [longitude1, latitude1, longitude2, latitude2])
    # haversine 공식
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 6371 * 2 * asin(sqrt(a))


def calc_center(coords):
    coords = json.loads(coords)
    lats = []
    lons = []
    for coord in coords:
        lats.append(float(coord["latitude"]))
        lons.append(float(coord["longitude"]))
    return {
        "latitude": sum(lats) / len(lats),
        "longitude": sum(lons) / len(lons)
    }

def generate_random_jeju_coordinates():
    # 제주도의 위도와 경도 범위
    min_latitude = 33.1
    max_latitude = 33.6
    min_longitude = 126.1
    max_longitude = 126.9

    # 랜덤한 위도와 경도 생성
    latitude = round(random.uniform(min_latitude, max_latitude), 6)
    longitude = round(random.uniform(min_longitude, max_longitude), 6)

    return latitude, longitude

