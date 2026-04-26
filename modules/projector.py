import time
import math
import requests
import json
import importlib
from requests.auth import HTTPDigestAuth


class Projector:
    def __init__(self, ip, projector_type, username=None, password=None):
        self.ip = ip
        self.projector_type = projector_type
        self.projector_lib = importlib.import_module(f"projectors.{projector_type}")
        self._username_override = username or None
        self._password_override = password or None

    def _credentials(self):
        defaults = self.projector_lib.default_login
        user = self._username_override or defaults["username"]
        password = self._password_override or defaults["password"]
        return user, password

    def _format_headers(self):
        headers = getattr(self.projector_lib, "req_headers", {}) or {}
        return {
            key: value.format(ip=self.ip) if isinstance(value, str) else value
            for key, value in headers.items()
        }

    def _resolved_command_params(self, command):
        params = []
        for key, value in command["params"]:
            if value == "$$time":
                value = self.projector_lib.time()
            params.append((key, value))
        return params

    def _command_auth_mode(self):
        return getattr(self.projector_lib, "auth_mode", "url_credentials")

    def _generate_command_digest(self, command_name):
        command = self.projector_lib.commands[command_name]
        url = f"http://{self.ip}{command['path']}"
        params = self._resolved_command_params(command)

        # Structured params/data are only safe for standard key/value joiners.
        standard_encoding = (
            command["default_kvjoiner"] == "=" and command["default_kjoiner"] == "&"
        )
        if not standard_encoding:
            suffix = ""
            for key, value in params:
                suffix += (
                    key
                    + command["default_kvjoiner"]
                    + value
                    + command["default_kjoiner"]
                )
            url += suffix.rstrip(command["default_kjoiner"])
            params = None

        return url, command["mode"], command["duplicate"], params

    def _generate_command_legacy(self, command_name):
        command = self.projector_lib.commands[command_name]
        user, password = self._credentials()
        url = f"http://{user}:{password}@{self.ip}{command['path']}"
        suffix = "".join(
            (
                key
                + command["default_kvjoiner"]
                + value
                + command["default_kjoiner"]
            )
            for key, value in self._resolved_command_params(command)
        )
        url += suffix.rstrip(command["default_kjoiner"])
        return url, command["mode"], command["duplicate"]

    def _execute_command(self, command_name):
        """
        Execute a low-level command defined in the projector library.
        Handles GET/POST and duplicate-send semantics.

        If the projector module exposes a custom `handle_command` function
        (e.g. for an in-process test projector), that is used instead of
        performing any HTTP requests.
        """
        # Allow a projector module to fully override command execution.
        handler = getattr(self.projector_lib, "handle_command", None)
        if callable(handler):
            return handler(command_name, self)

        timeout = getattr(self.projector_lib, "request_timeout", None)
        auth_mode = self._command_auth_mode()

        if auth_mode == "digest":
            url, mode, duplicate, params = self._generate_command_digest(command_name)
            user, password = self._credentials()
            headers = self._format_headers()
            session = requests.Session()
            session.auth = HTTPDigestAuth(user, password)

            # Prime digest challenge and any remote-control session state.
            control_url = f"http://{self.ip}{self.projector_lib.control_page}"
            prime_kwargs = {"headers": headers}
            if timeout is not None:
                prime_kwargs["timeout"] = timeout
            session.get(control_url, **prime_kwargs)

            caller = session.get if mode == "get" else session.post
            request_kwargs = {"headers": headers}
            if timeout is not None:
                request_kwargs["timeout"] = timeout
            if params is not None:
                payload_key = "params" if mode == "get" else "data"
                request_kwargs[payload_key] = params
            response = caller(url, **request_kwargs)
            if duplicate:
                time.sleep(0.5)
                url, _, _, params = self._generate_command_digest(command_name)
                request_kwargs = {"headers": headers}
                if timeout is not None:
                    request_kwargs["timeout"] = timeout
                if params is not None:
                    payload_key = "params" if mode == "get" else "data"
                    request_kwargs[payload_key] = params
                response = caller(url, **request_kwargs)
            return response

        # Legacy transport path preserves original behavior for existing modules.
        url, mode, duplicate = self._generate_command_legacy(command_name)
        caller = requests.get if mode == "get" else requests.post
        headers = getattr(self.projector_lib, "req_headers", {})
        request_kwargs = {"headers": headers}
        if timeout is not None:
            request_kwargs["timeout"] = timeout
        response = caller(url, **request_kwargs)
        if duplicate:
            time.sleep(0.5)
            url, _, _ = self._generate_command_legacy(command_name)
            response = caller(url, **request_kwargs)
        return response

    def on(self):
        self._execute_command("power_on")

    def off(self):
        self._execute_command("power_off")

    def status(self):
        ip = self.ip
        user, password = self._credentials()
        return self.projector_lib.request_status(user, password, ip)

    def source(self):
        ip = self.ip
        user, password = self._credentials()
        return self.projector_lib.request_source(user, password, ip)

    def toggle(self, command_name):
        """
        Generic helper for toggle-style commands like MUTE, BLANK, FREEZE, etc.
        """
        if command_name not in self.projector_lib.commands:
            raise ValueError(
                f"Unknown command '{command_name}' for projector type {self.projector_type}"
            )
        self._execute_command(command_name)

    def get_targets(self, target_cycle):
        targets = []
        for target, cycle in self.projector_lib.TARGET_TO_CYCLE_COMMAND.items():
            if cycle == target_cycle:
                if target.lower().replace(" ", "").replace("-", "") in [
                    i.lower().replace(" ", "") for i in targets
                ]:
                    continue
                targets.append(target)
        return targets

    def set_source(self, target_source, max_attempts=12):
        """
        Set the projector to a given source.

        For projectors that expose cycle-based source selection (e.g. Epson with
        VIDEO/OTHER/USB/LAN keys), we:
          - look up which cycle key to use based on the requested source
          - repeatedly send that key, checking request_source() after each press,
            until we reach the desired source or hit max_attempts.

        For projectors that support direct source commands (e.g. Christie with
        HDMI1, HDMI2, HDBASET, etc.), we call the appropriate direct command.
        """
        current = self.source()
        if current == target_source:
            return True

        # First, try cycle-based sources if this projector exposes a mapping
        cycle_map = getattr(self.projector_lib, "TARGET_TO_CYCLE_COMMAND", {})
        cycle_cmd = cycle_map.get(target_source)
        if cycle_cmd is not None:
            for _ in range(max_attempts):
                # Re-check current source each loop; bail early if we've reached target
                current = self.source()
                if current.lower() == target_source.lower():
                    return True
                self._execute_command(cycle_cmd)
                time.sleep(0.5)

            # Final check after last press
            return self.source() == target_source
        # Otherwise, fall back to direct source commands where available
        name_map = {
            "HDMI 1": "HDMI1",
            "HDMI 2": "HDMI2",
            "HDBaseT": "HDBASET",
            "Computer 1": "COMPUTER1",
        }
        command_name = name_map.get(target_source, target_source)

        if command_name not in self.projector_lib.commands:
            raise ValueError(
                f"Cannot set source '{target_source}' for projector type {self.projector_type}"
            )

        self._execute_command(command_name)
        return True


def determine(ip):
    try:
        x = requests.get(f"http://{ip}/html/remote.html", timeout=0.5)
        if x.status_code in {401, 200}:
            return "Cristie"
        elif x.status_code == 404:
            x = requests.get(f"http://{ip}/cgi-bin/webconf", timeout=0.5)
            if x.status_code in {401, 200}:
                return "Epson"
        return None
    except Exception:
        return None


def discover():
    for i in range(255):
        ip = f"192.168.0.{i}"
        if projector := determine(ip):
            print(ip, projector)
