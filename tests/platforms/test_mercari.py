# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
from unittest import TestCase
import threading

from selenium import webdriver

from cropsiss import exceptions
from cropsiss.platforms import mercari
from tests.platforms import http


class TestMercari_property(TestCase):
    def test_id(self) -> None:
        self.assertEqual(mercari.Mercari().id, 1)

    def test_code(self) -> None:
        self.assertEqual(mercari.Mercari().code, "mercari")

    def test_name(self) -> None:
        self.assertEqual(mercari.Mercari().name, "メルカリ")

    def test_column_index(self) -> None:
        self.assertEqual(mercari.Mercari().column_index, 2)

    def test_sold_mail_query(self) -> None:
        self.assertEqual(mercari.Mercari().sold_mail_query, 'from:(no-reply@mercari.jp) AND "購入しました"')

    def test_item_id_pattern(self) -> None:
        self.assertEqual(mercari.Mercari().item_id_pattern, "(?<=商品ID : )[a-zA-Z0-9]+")


class TestMercari_get_selling_page_url(TestCase):
    def test_item_id(self) -> None:
        platform = mercari.Mercari()
        item_ids = [f"m{i:09}" for i in range(3)]
        for item_id in item_ids:
            with self.subTest(item_id=item_id):
                self.assertEqual(
                    platform.get_selling_page_url(item_id),
                    f"https://jp.mercari.com/item/{item_id}"
                )


class TestMercari_cancel(TestCase):
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
        self.platform = mercari.Mercari()
        self.platform._implicitly_wait_second = 1
        self.url_base: str = f"http://localhost:{self.port}"

    def test_url_exists(self) -> None:
        self.platform.EDIT_PAGE = self.url_base + "/tests/platforms/mercari_edit_page.html"
        self.platform.cancel("m00000000000", self.chrome_options)

    def test_url_does_not_exist(self) -> None:
        self.platform.EDIT_PAGE = self.url_base + "/unexist_here"
        with self.assertRaises(exceptions.NotCancelError):
            self.platform.cancel("m00000000000", self.chrome_options)
