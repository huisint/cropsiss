# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
from unittest import TestCase, mock
import itertools

import click
from selenium import webdriver

from cropsiss.cli import browse


@mock.patch("selenium.webdriver.ChromeOptions", return_value=mock.Mock(spec_set=webdriver.ChromeOptions))
class Test_chrome_args_callback(TestCase):

    def test_value(self, chrome_options_mock: mock.Mock) -> None:
        ctx = mock.Mock(spec_set=click.Context)
        param = mock.Mock(spec_set=click.Argument)
        value = ("--headless",)
        self.assertEqual(browse.chrome_args_callback(ctx, param, value), chrome_options_mock.return_value)
        self.assertListEqual(
            chrome_options_mock.return_value.add_argument.mock_calls,
            list(map(mock.call, itertools.chain(browse.DEFAULT_CHROME_ARGS, value)))
        )
