# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
import abc
from typing import Any

from cropsiss.google import credentials


class AbstractAPI(abc.ABC):
    @abc.abstractmethod
    def __init__(self, credentials: credentials.Credentials, version: str, *args: Any, **kwargs: Any) -> None:
        """
        Parameters
        ----------
        credentials : cropsiss.google.credentials.Credentials
            Credentials for Google API.
        version : str
            Version of Google API
        """

    @property
    @abc.abstractmethod
    def service_name(self) -> str:
        """Service name of Google API."""
