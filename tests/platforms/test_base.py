# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
from unittest import TestCase

from selenium import webdriver

from cropsiss.platforms import base


class TestBasePlatform_property(TestCase):

    def test_id(self) -> None:
        for i in range(3):
            platform = base.BasePlatform()
            platform._id = i
            with self.subTest(id=i):
                self.assertEqual(platform.id, i)

    def test_code(self) -> None:
        for i in range(3):
            code = f"code{i}"
            platform = base.BasePlatform()
            platform._code = code
            with self.subTest(code=code):
                self.assertEqual(platform.code, code)

    def test_name(self) -> None:
        for i in range(3):
            name = f"name{i}"
            platform = base.BasePlatform()
            platform._name = name
            with self.subTest(name=name):
                self.assertEqual(platform.name, name)

    def test_column_index(self) -> None:
        for i in range(3):
            platform = base.BasePlatform()
            platform._id = i
            with self.subTest(id=i):
                self.assertEqual(platform.column_index, i + 1)

    def test_sold_mail_query(self) -> None:
        platform = base.BasePlatform()
        with self.assertRaises(NotImplementedError):
            platform.sold_mail_query

    def test_item_id_pattern(self) -> None:
        platform = base.BasePlatform()
        with self.assertRaises(NotImplementedError):
            platform.item_id_pattern


class TestBasePlatform_get_selling_page_url(TestCase):
    def test_item_id(self) -> None:
        platform = base.BasePlatform()
        item_ids = [f"abc123{i}" for i in range(3)]
        for item_id in item_ids:
            with self.subTest(item_id=item_id):
                with self.assertRaises(NotImplementedError):
                    platform.get_selling_page_url(item_id)


class TestBasePlatform_cancel(TestCase):
    def test(self) -> None:
        platform = base.BasePlatform()
        options = webdriver.ChromeOptions()
        with self.assertRaises(NotImplementedError):
            platform.cancel("", options)


class TestBasePlatform___repr__(TestCase):
    def test(self) -> None:
        names = [f"platform{i}" for i in range(3)]
        for name in names:
            platform = base.BasePlatform()
            platform._name = name
            with self.subTest(name=name):
                self.assertEqual(repr(platform), name)
