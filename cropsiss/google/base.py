# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
from typing import Any

from googleapiclient import discovery

from cropsiss.google import credentials, abstract


class BaseAPI(abstract.AbstractAPI):
    _service: Any

    def __init__(self, credentials: credentials.Credentials, version: str) -> None:
        self._service = discovery.build(
            serviceName=self.service_name,
            version=version,
            credentials=credentials._credentials
        )
