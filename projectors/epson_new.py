import time as root_time
import re
import requests
from requests.auth import HTTPDigestAuth
from urllib3.exceptions import InsecureRequestWarning

default_login = {"username": "EPSONWEB", "password": "ADMIN"}

auth_mode = "digest"

control_page = "/cgi-bin/Remote/Basic_Control"
request_timeout = 3
status_callback = "PWSTATUS?"
source_page = "103"

req_headers = {
    "Referer": "http://{ip}/cgi-bin/Remote/Basic_Control",
    "X-Requested-With": "XMLHttpRequest",
}

source_codes = {
    "30": "HDMI1",
    "A0": "HDMI2",
    "10": "Computer",
    "41": "Video",
    "51": "USB Display",
    "52": "USB",
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
        "params": [["SOURCE", "30"], ["_", "$$time"]],
    },
    "HDMI2": {
        "type": "source",
        "mode": "get",
        "duplicate": False,
        "path": "/cgi-bin/Remote/directsend?",
        "default_kvjoiner": "=",
        "default_kjoiner": "&",
        "params": [["SOURCE", "A0"], ["_", "$$time"]],
    },
    "Computer": {
        "type": "source",
        "mode": "get",
        "duplicate": False,
        "path": "/cgi-bin/Remote/directsend?",
        "default_kvjoiner": "=",
        "default_kjoiner": "&",
        "params": [["SOURCE", "10"], ["_", "$$time"]],
    },
    "Video": {
        "type": "source",
        "mode": "get",
        "duplicate": False,
        "path": "/cgi-bin/Remote/directsend?",
        "default_kvjoiner": "=",
        "default_kjoiner": "&",
        "params": [["SOURCE", "41"], ["_", "$$time"]],
    },
    "USB Display": {
        "type": "source",
        "mode": "get",
        "duplicate": False,
        "path": "/cgi-bin/Remote/directsend?",
        "default_kvjoiner": "=",
        "default_kjoiner": "&",
        "params": [["SOURCE", "51"], ["_", "$$time"]],
    },
    "USB": {
        "type": "source",
        "mode": "get",
        "duplicate": False,
        "path": "/cgi-bin/Remote/directsend?",
        "default_kvjoiner": "=",
        "default_kjoiner": "&",
        "params": [["SOURCE", "52"], ["_", "$$time"]],
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
}


def request_status(user, password, ip):
    try:
        payload = _json_query(user, password, ip, status_callback)
        reply = _feature_reply(payload)
        # PWSTATUS? returns 01 for standby, 02 while warming, 03 when on.
        return bool(reply) and reply.split(maxsplit=1)[0] in {"02", "03"}
    except (KeyError, TypeError, ValueError, requests.exceptions.RequestException):
        return False


def request_source(user, password, ip):
    full_url = f"https://{ip}/cgi-bin/webconf"
    try:
        _disable_ssl_warnings()
        response = requests.post(
            full_url,
            data={"page": source_page},
            auth=HTTPDigestAuth(user, password),
            headers=_web_control_headers(ip),
            timeout=request_timeout,
            verify=False,
        )
        response.raise_for_status()
        return _webconf_source(response.text)
    except requests.exceptions.RequestException:
        return None


def time():
    return str(round(root_time.time() * 1000))


def _formatted_headers(ip):
    return {
        key: value.format(ip=ip) if isinstance(value, str) else value
        for key, value in req_headers.items()
    }


def _web_control_headers(ip):
    return {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": f"https://{ip}",
        "Referer": f"https://{ip}/cgi-bin/WebControl/Advanced/Info.page?",
        "X-Requested-With": "XMLHttpRequest",
    }


def _json_query_headers(ip):
    return {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": f"https://{ip}/cgi-bin/WebControl/Advanced/Info.page?",
        "X-Requested-With": "XMLHttpRequest",
    }


def _json_query(user, password, ip, callback):
    _disable_ssl_warnings()
    full_url = (
        f"https://{ip}/cgi-bin/json_query?jsoncallback={callback}&_={time()}"
    )
    response = requests.get(
        full_url,
        auth=HTTPDigestAuth(user, password),
        headers=_json_query_headers(ip),
        timeout=request_timeout,
        verify=False,
    )
    response.raise_for_status()
    return response.json()


def _feature_reply(payload):
    feature = payload["projector"]["feature"]
    return None if feature.get("error") else feature.get("reply", "").strip()


def _webconf_source(text):
    source = _webconf_value(text, "source")
    cur_source = _webconf_value(text, "cur_source")
    return source or source_codes.get(cur_source)


def _webconf_value(text, field):
    if match := re.search(rf'^\s*{re.escape(field)}:\s*"([^"]*)"', text, re.M):
        return match.group(1).strip() or None
    return None


def _disable_ssl_warnings():
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
