# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
from unittest import TestCase
import threading

from selenium import webdriver

from cropsiss import exceptions
from cropsiss.platforms import yahoo_auction
from tests.platforms import http


class TestYahooAuction_property(TestCase):
    def test_id(self) -> None:
        self.assertEqual(yahoo_auction.YahooAuction().id, 2)

    def test_code(self) -> None:
        self.assertEqual(yahoo_auction.YahooAuction().code, "yahoo_auction")

    def test_name(self) -> None:
        self.assertEqual(yahoo_auction.YahooAuction().name, "ヤフオク!")

    def test_column_index(self) -> None:
        self.assertEqual(yahoo_auction.YahooAuction().column_index, 3)

    def test_sold_mail_query(self) -> None:
        self.assertEqual(
            yahoo_auction.YahooAuction().sold_mail_query,
            'from:(auction-master@mail.yahoo.co.jp) AND {subject:("ヤフオク! - 終了（落札者あり）")}',
        )

    def test_item_id_pattern(self) -> None:
        self.assertEqual(
            yahoo_auction.YahooAuction().item_id_pattern,
            "(?<=オークションID：)[a-zA-Z0-9]+"
        )


class TestYahooAuction_get_selling_page_url(TestCase):
    def test_item_id(self) -> None:
        platform = yahoo_auction.YahooAuction()
        item_ids = [f"m{i:09}" for i in range(3)]
        for item_id in item_ids:
            with self.subTest(item_id=item_id):
                self.assertEqual(
                    platform.get_selling_page_url(item_id),
                    f"https://page.auctions.yahoo.co.jp/jp/auction/{item_id}"
                )


class TestYahooAuction_cancel(TestCase):
    server: http.server.HTTPServer
    httpthread: threading.Thread
    port: int = 8080

    @classmethod
    def setUpClass(cls) -> None:
        cls.server = http.create_server(port=cls.port)
        cls.httpthread = threading.Thread(target=cls.server.serve_forever)
        cls.httpthread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.server_close()
        cls.server.shutdown()
        cls.httpthread.join()

    def setUp(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        self.chrome_options = options
        self.platform = yahoo_auction.YahooAuction()
        self.platform._implicitly_wait_second = 1
        self.url_base = f"http://localhost:{self.port}"

    def test_url_exists(self) -> None:
        self.platform.CANCEL_PAGE = self.url_base + "/tests/platforms/yahoo_auction_cancel_page.html"
        self.platform.cancel("d000000000", self.chrome_options)

    def test_url_does_not_exist(self) -> None:
        self.platform.CANCEL_PAGE = self.url_base + "/unexist_here"
        with self.assertRaises(exceptions.NotCancelError):
            self.platform.cancel("d0000000000", self.chrome_options)
