import time as root_time
import requests
from requests.auth import HTTPDigestAuth

default_login = {"username": "EPSONWEB", "password": "ADMIN"}

auth_mode = "digest"

control_page = "/cgi-bin/Remote/Basic_Control"
request_timeout = 3

req_headers = {
    "Referer": "http://{ip}/cgi-bin/Remote/Basic_Control",
    "X-Requested-With": "XMLHttpRequest",
}

commands = {
    "power_on": {
        "type": "power",
        "mode": "get",
        "duplicate": False,
        "path": "/cgi-bin/Remote/directsend?",
        "default_kvjoiner": "=",
        "default_kjoiner": "&",
        "params": [["KEY", "3B"], ["_", "$$time"]],
    },
    "power_off": {
        "type": "power",
        "mode": "get",
        "duplicate": True,
        "path": "/cgi-bin/Remote/directsend?",
        "default_kvjoiner": "=",
        "default_kjoiner": "&",
        "params": [["KEY", "3B"], ["_", "$$time"]],
    },
    "HDMI1": {
        "type": "source",
        "mode": "get",
        "duplicate": False,
        "path": "/cgi-bin/Remote/directsend?",
        "default_kvjoiner": "=",
        "default_kjoiner": "&",
        "params": [["KEY", ""], ["_", "$$time"]],
    },
    "HDMI2": {
        "type": "source",
        "mode": "get",
        "duplicate": False,
        "path": "/cgi-bin/Remote/directsend?",
        "default_kvjoiner": "=",
        "default_kjoiner": "&",
        "params": [["KEY", ""], ["_", "$$time"]],
    },
    "USB": {
        "type": "source",
        "mode": "get",
        "duplicate": False,
        "path": "/cgi-bin/Remote/directsend?",
        "default_kvjoiner": "=",
        "default_kjoiner": "&",
        "params": [["KEY", ""], ["_", "$$time"]],
    },
    "BLANK": {
        "type": "toggle",
        "mode": "get",
        "duplicate": False,
        "path": "/cgi-bin/Remote/directsend?",
        "default_kvjoiner": "=",
        "default_kjoiner": "&",
        "params": [["KEY", "3E"], ["_", "$$time"]],
    },
    "FREEZE": {
        "type": "toggle",
        "mode": "get",
        "duplicate": False,
        "path": "/cgi-bin/Remote/directsend?",
        "default_kvjoiner": "=",
        "default_kjoiner": "&",
        "params": [["KEY", "47"], ["_", "$$time"]],
    },
    "A/V MUTE": {
        "type": "toggle",
        "mode": "get",
        "duplicate": False,
        "path": "/cgi-bin/Remote/directsend?",
        "default_kvjoiner": "=",
        "default_kjoiner": "&",
        "params": [["KEY", "3E"], ["_", "$$time"]],
    },
    "SEARCH": {
        "type": "toggle",
        "mode": "get",
        "duplicate": False,
        "path": "/cgi-bin/Remote/directsend?",
        "default_kvjoiner": "=",
        "default_kjoiner": "&",
        "params": [["KEY", "67"], ["_", "$$time"]],
    },
}


def request_status(user, password, ip):
    p = "05"
    payload = {"page": p}
    full_url = f"http://{ip}/cgi-bin/webconf"
    try:
        response = requests.post(
            full_url,
            data=payload,
            auth=HTTPDigestAuth(user, password),
            headers=_formatted_headers(ip),
            timeout=request_timeout,
        )
        return "The projector is currently on standby" not in response.text
    except requests.exceptions.RequestException:
        return False


def request_source(user, password, ip):
    p = "05"
    payload = {"page": p}
    full_url = f"http://{ip}/cgi-bin/webconf"
    try:
        response = requests.post(
            full_url,
            data=payload,
            auth=HTTPDigestAuth(user, password),
            headers=_formatted_headers(ip),
            timeout=request_timeout,
        )
        if "The projector is currently on standby" in response.text:
            return None
        text = response.text
        idx = text.find("Source")
        return text[idx + 155 : idx + 166].strip(" ").split("<")[0]
    except requests.exceptions.RequestException:
        return None


def time():
    return str(round(root_time.time() * 1000))


def _formatted_headers(ip):
    return {
        key: value.format(ip=ip) if isinstance(value, str) else value
        for key, value in req_headers.items()
    }
