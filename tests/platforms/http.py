# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
from http.server import SimpleHTTPRequestHandler


class NoLogHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_request(self, code=None, size=None) -> None:  # type: ignore
        return

    def log_error(self, format: str, *args) -> None:  # type: ignore
        return
