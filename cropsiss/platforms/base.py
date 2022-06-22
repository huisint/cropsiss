# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
import contextlib
from typing import Iterator

from selenium import webdriver
import chromedriver_binary  # noqa

from cropsiss.platforms import abstract


class BasePlatform(abstract.AbstractPlatform):
    _id: int
    _code: str
    _name: str
    _implicitly_wait_second: int = 30

    @property
    def id(self) -> int:
        return self._id

    @property
    def code(self) -> str:
        return self._code

    @property
    def name(self) -> str:
        return self._name

    @property
    def column_index(self) -> int:
        return self.id + 1

    @property
    def sold_mail_query(self) -> str:
        raise NotImplementedError()

    @property
    def item_id_pattern(self) -> str:
        raise NotImplementedError()

    def get_selling_page_url(self, item_id: str) -> str:
        raise NotImplementedError()

    @contextlib.contextmanager
    def chrome(
        self,
        chrome_options: webdriver.ChromeOptions
    ) -> Iterator[webdriver.Chrome]:
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(self._implicitly_wait_second)
        try:
            yield driver
        finally:
            driver.quit()

    def cancel(self, item_id: str, chrome_options: webdriver.ChromeOptions) -> None:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return self.name
