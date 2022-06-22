# Copyright (c) 2022 Shuhei Nitta. All rights reserved.


class ConfigFileNotFoundError(FileNotFoundError):
    """Raises when config file is not found"""


class ConfigInsufficientError(Exception):
    """Raises when config is not sufficient"""


class GoogleCredentialsInvalidError(Exception):
    """Raises when credentials for google API is invalid"""


class NotCancelError(Exception):
    """Raises on error when canceling"""
