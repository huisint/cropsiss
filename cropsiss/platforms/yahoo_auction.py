# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
import time
import logging

from selenium import webdriver
from selenium.webdriver.remote import webelement
from selenium.webdriver.common import by

from cropsiss import exceptions
from cropsiss.platforms import base


logger = logging.getLogger(__name__)


class YahooAuction(base.BasePlatform):
    _id: int = 2
    _code: str = "yahoo_auction"
    _name: str = "ヤフオク!"
    CANCEL_PAGE: str = "https://page.auctions.yahoo.co.jp/jp/show/cancelauction?aID={id}"
    CANCEL_BUTTON_XPATH: str = "/html/body/center[1]/form/table/tbody/tr[3]/td/input"

    @property
    def sold_mail_query(self) -> str:
        return 'from:(auction-master@mail.yahoo.co.jp) AND {subject:("ヤフオク! - 終了（落札者あり）")}'

    @property
    def item_id_pattern(self) -> str:
        return "(?<=オークションID：)[a-zA-Z0-9]+"

    def get_selling_page_url(self, item_id: str) -> str:
        return f"https://page.auctions.yahoo.co.jp/jp/auction/{item_id}"

    def cancel(self, item_id: str, chrome_options: webdriver.ChromeOptions) -> None:
        url: str = self.CANCEL_PAGE.format(id=item_id)
        with self.chrome(chrome_options) as driver:
            try:
                driver.get(url)
                assert driver.current_url == url, "Make sure you logged in to Yahoo!Auction on the browser"
                logger.debug(f"Accessed {url}")
            except Exception as err:  # pragma: no cover
                raise exceptions.NotCancelError(f"Can't access the cancel page. Please Make sure URL: {url}") from err
            try:
                cancel_element = driver.find_element(by.By.XPATH, self.CANCEL_BUTTON_XPATH)
                assert isinstance(cancel_element, webelement.WebElement)
                logger.debug(f"{self.CANCEL_BUTTON_XPATH} was found on the page")
            except Exception as err:  # pragma: no cover
                raise exceptions.NotCancelError(
                    f"Can't find the cancel button. Please Make sure XPATH: {self.CANCEL_BUTTON_XPATH}"
                ) from err
            try:
                cancel_element.click()
                logger.debug("The cancel button was clicked")
            except Exception as err:  # pragma: no cover
                raise exceptions.NotCancelError("Can't click the cancel button") from err
            time.sleep(1)
