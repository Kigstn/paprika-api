import configparser
import requests


# init configparser and read config
config = configparser.ConfigParser()
config.read('config.ini')

token = ""


# getting oauth token
def get_token():
    url = config["API"]["paprika_url"] + "/api/v2/account/login/"
    payload = {
        "email": config["USER DATA"]["auth_email"],
        "password": config["USER DATA"]["auth_password"],
    }

    r = requests.post(url, data=payload)
    if r.status_code == 200:
        json = r.json()

        global token
        token = json["result"]["token"]
        print("got token")

    else:
        print("failed getting token")


# return json from given request
def get_request(request_url):
    url = config["API"]["paprika_url"] + request_url
    r = requests.get(url, headers={'Authorization': f'Bearer {token}'})
    json = r.json()

    if r.status_code == 200:
        if json["result"]:
            if "error" not in json:
                return json["result"]

    print(f"Failed GET {url} with error code {r.status_code} - {json}")


# return json from given request
def post_request(request_url, files):
    url = config["API"]["paprika_url"] + request_url
    r = requests.post(url, files=files, headers={'Authorization': f'Bearer {token}'})
    json = r.json()

    if r.status_code == 200:
        if "error" not in json:
            print(f"Success - {json}")
            return json

    print(f"Failed POST {url} with error code {r.status_code} - {json}")

