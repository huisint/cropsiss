# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
import abc

from selenium import webdriver


class AbstractPlatform(abc.ABC):
    @property
    @abc.abstractmethod
    def id(self) -> int:
        """
        The ID of the platform.
        """

    @property
    @abc.abstractmethod
    def code(self) -> str:
        """
        The code of the platform.
        """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        The name of the platform.
        """

    @property
    @abc.abstractmethod
    def column_index(self) -> int:
        """
        The column index on the Google Spreadsheet.
        """

    @property
    @abc.abstractmethod
    def sold_mail_query(self) -> str:
        """
        The query string to identify sold mails in the Gmail mailbox.
        """

    @property
    @abc.abstractmethod
    def item_id_pattern(self) -> str:
        """
        The pattern to identify the id used in the platform in the mail body.
        """

    @abc.abstractmethod
    def get_selling_page_url(self, item_id: str) -> str:
        """
        Get the URL of the selling page of the item.
        """

    @abc.abstractmethod
    def cancel(self, item_id: str, chrome_options: webdriver.ChromeOptions) -> None:
        """
        Cancel a selling item.

        Parameters
        ----------
        item_id : str
            An ID assigned by the platform.
        chrome_options : selenium.webdriver.ChromeOptions
            Options for Chrome webbrowser.

        Raises
        ------
        cropsiss.exceptions.NotCancelError
            If cancellnig could not be done.
        """
