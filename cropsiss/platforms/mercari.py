# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
import time
import logging

from selenium import webdriver
from selenium.webdriver.remote import webelement
from selenium.webdriver.common import by

from cropsiss import exceptions
from cropsiss.platforms import base


logger = logging.getLogger(__name__)


class Mercari(base.BasePlatform):
    _id: int = 1
    _code: str = "mercari"
    _name: str = "メルカリ"
    EDIT_PAGE: str = "https://jp.mercari.com/sell/edit/{id}"
    SUSPEND_BUTTON_XPATH: str = '//*[@id="main"]/form/div[2]/mer-button[2]/button'

    @property
    def sold_mail_query(self) -> str:
        return 'from:(no-reply@mercari.jp) AND "購入しました"'

    @property
    def item_id_pattern(self) -> str:
        return "(?<=商品ID : )[a-zA-Z0-9]+"

    def get_selling_page_url(self, item_id: str) -> str:
        return f"https://jp.mercari.com/item/{item_id}"

    def cancel(self, item_id: str, chrome_options: webdriver.ChromeOptions) -> None:
        url: str = self.EDIT_PAGE.format(id=item_id)
        with self.chrome(chrome_options) as driver:
            try:
                driver.get(url)
                assert driver.current_url == url, "Make sure you logged in to Mercari on the browser"
                logger.debug(f"Accessed {url}")
            except Exception as err:  # pragma: no cover
                raise exceptions.NotCancelError(f"Can't access the edit page. Please Make sure URL: {url}") from err
            try:
                suspend_element = driver.find_element(by.By.XPATH, self.SUSPEND_BUTTON_XPATH)
                assert isinstance(suspend_element, webelement.WebElement)
                logger.debug(f"{self.SUSPEND_BUTTON_XPATH} was found on the page")
            except Exception as err:  # pragma: no cover
                raise exceptions.NotCancelError(
                    f"Can't find the suspend button. Please Make sure XPATH: {self.SUSPEND_BUTTON_XPATH}"
                ) from err
            try:
                suspend_element.click()
                logger.debug("The suspend button was clicked")
            except Exception as err:  # pragma: no cover
                raise exceptions.NotCancelError("Can't click the suspend button") from err
            time.sleep(1)
