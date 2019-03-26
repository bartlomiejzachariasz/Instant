from requests import get
from requests.exceptions import RequestException
from contextlib import closing
import json


def simple_get(url):
    try:
        with closing(get(url)) as resp:
            if check_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))


def get_json(url):
    try:
        with closing(get(url)) as resp:
            resp = resp.content.decode("utf-8")
            if validate_json(resp):
                return resp
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))


def check_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def validate_json(resp):
    try:
        json.loads(resp)
        return True
    except ValueError as e:
        print(e)
        return False


def log_error(e):
    print(e)
