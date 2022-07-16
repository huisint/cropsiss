# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
from http import server


class NoLogHTTPRequestHandler(server.SimpleHTTPRequestHandler):
    def log_request(self, code=None, size=None) -> None:  # type: ignore
        return

    def log_error(self, format: str, *args) -> None:  # type: ignore
        return


def create_server(address: str = "", port: int = 8080) -> server.HTTPServer:
    return server.HTTPServer((address, port), NoLogHTTPRequestHandler)
