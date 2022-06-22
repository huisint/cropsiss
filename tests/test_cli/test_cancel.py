# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
from unittest import TestCase, mock
import pathlib
import base64
import typing as t

from click import testing
from selenium import webdriver

import cropsiss
from cropsiss import exceptions, google
from cropsiss.cli import cancel, root, sheet


RUNNER = testing.CliRunner()
CHROME_OPTIONS = mock.Mock(spec_set=webdriver.ChromeOptions)
CHROME_OPTIONS_PATCHER = mock.patch("selenium.webdriver.ChromeOptions", return_value=CHROME_OPTIONS)


def setUpModule() -> None:
    CHROME_OPTIONS_PATCHER.start()


def tearDownModule() -> None:
    CHROME_OPTIONS_PATCHER.stop()


@mock.patch("cropsiss.platforms.mercari.Mercari.cancel")
class Test_cancel_mercari(TestCase):

    def _test(self, item_ids: list[str], output: str) -> None:
        result = RUNNER.invoke(
            root.main,
            [str(cancel.main.name), str(cancel.cancel_mercari.name), *item_ids],
            catch_exceptions=False
        )
        self.assertEqual(result.output, output)
        self.assertEqual(result.exit_code, 0)

    def test_success(self, cancel_mock: mock.Mock) -> None:
        item_ids = [f"m{i:09}" for i in range(3)]
        output = "".join(f"{item_id}: succeeded\n" for item_id in item_ids)
        self._test(item_ids, output)
        self.assertListEqual(
            cancel_mock.mock_calls,
            [mock.call(item_id, CHROME_OPTIONS) for item_id in item_ids]
        )

    def test_fail(self, cancel_mock: mock.Mock) -> None:
        cancel_mock.side_effect = exceptions.NotCancelError()
        item_ids = [f"m{i:09}" for i in range(3)]
        output = "".join(f"{item_id}: failed\n" for item_id in item_ids)
        self._test(item_ids, output)
        self.assertListEqual(
            cancel_mock.mock_calls,
            [mock.call(item_id, CHROME_OPTIONS) for item_id in item_ids]
        )


@mock.patch("cropsiss.platforms.yahoo_auction.YahooAuction.cancel")
class Test_cancel_yahuoku(TestCase):

    def _test(self, item_ids: list[str], output: str) -> None:
        result = RUNNER.invoke(
            root.main,
            [str(cancel.main.name), str(cancel.cancel_yahuoku.name), *item_ids],
            catch_exceptions=False
        )
        self.assertEqual(result.output, output)
        self.assertEqual(result.exit_code, 0)

    def test_success(self, cancel_mock: mock.Mock) -> None:
        item_ids = [f"m{i:09}" for i in range(3)]
        output = "".join(f"{item_id}: succeeded\n" for item_id in item_ids)
        self._test(item_ids, output)
        self.assertListEqual(
            cancel_mock.mock_calls,
            [mock.call(item_id, CHROME_OPTIONS) for item_id in item_ids]
        )

    def test_fail(self, cancel_mock: mock.Mock) -> None:
        cancel_mock.side_effect = exceptions.NotCancelError()
        item_ids = [f"m{i:09}" for i in range(3)]
        output = "".join(f"{item_id}: failed\n" for item_id in item_ids)
        self._test(item_ids, output)
        self.assertListEqual(
            cancel_mock.mock_calls,
            [mock.call(item_id, CHROME_OPTIONS) for item_id in item_ids]
        )


@mock.patch("cropsiss.google.mail.GmailAPI", spec_set=google.GmailAPI)
class Test_get_donelabel_id(TestCase):

    def test_label_exist(
        self,
        gmail_api_mock: mock.Mock
    ) -> None:
        labels = [
            {"id": "Label_1", "name": cancel.DONE_LABEL},
            {"id": "Label_2", "name": "label_2"},
            {"id": "Label_3", "name": "label_3"},
        ]
        gmail_api_mock.get_labels.return_value = labels
        self.assertEqual(cancel.get_donelabel_id(gmail_api_mock), labels[0]["id"])
        gmail_api_mock.get_labels.assert_called_once_with()
        gmail_api_mock.create_label.assert_not_called()

    def test_label_does_not_exist(
        self,
        gmail_api_mock: mock.Mock,
    ) -> None:
        label = {"id": "Label_1", "name": cancel.DONE_LABEL}
        gmail_api_mock.get_labels.return_value = []
        gmail_api_mock.create_label.return_value = label
        self.assertEqual(cancel.get_donelabel_id(gmail_api_mock), label["id"])
        gmail_api_mock.get_labels.assert_called_once_with()
        gmail_api_mock.create_label.assert_called_once_with(cancel.DONE_LABEL)


@mock.patch("cropsiss.cli.cancel.get_donelabel_id", return_value="donelabel")
@mock.patch("cropsiss.google.mail.GmailAPI", spec_set=google.GmailAPI)
class Test_generate_sold_mail_ids(TestCase):

    def test_platform(
        self,
        gmail_api_mock: mock.Mock,
        get_donelabel_id_mock: mock.Mock
    ) -> None:
        for platform in cropsiss.PLATFORMS:
            gmail_api_mock.reset_mock()
            get_donelabel_id_mock.reset_mock()
            mail_ids = [f"mail_id_{i}" for i in range(3)]
            gmail_api_mock.search_mail.return_value = mail_ids
            with self.subTest(platform=platform.name):
                gen = cancel.generate_sold_mail_ids(gmail_api_mock, platform)
                self.assertListEqual(list(gen), mail_ids)
                self.assertListEqual(
                    gmail_api_mock.add_labels.mock_calls,
                    [mock.call(mail_id, [get_donelabel_id_mock.return_value]) for mail_id in mail_ids]
                )
                self.assertEqual(gmail_api_mock.add_labels.call_count, len(mail_ids))
                query = platform.sold_mail_query + " AND -{label:" + cancel.DONE_LABEL + "}"
                gmail_api_mock.search_mail.assert_called_once_with(query)
                get_donelabel_id_mock.assert_called_once_with(gmail_api_mock)


@mock.patch("cropsiss.cli.cancel.generate_sold_mail_ids")
@mock.patch("cropsiss.google.mail.GmailAPI", spec_set=google.GmailAPI)
class Test_generate_sold_item_ids(TestCase):
    maildir = pathlib.Path(__file__).parent / "mails"

    def get_gmail(self, filename: str) -> dict[str, t.Any]:
        with open(self.maildir / filename) as f:
            body = f.read()
        return {
            "payload": {
                "body": {
                    "data": base64.urlsafe_b64encode(body.encode("utf-8"))
                }
            }
        }

    def test_platform(
        self,
        gmail_api_mock: mock.Mock,
        generate_sold_mail_ids_mock: mock.Mock,
    ) -> None:
        for platform in cropsiss.PLATFORMS:
            gmail_api_mock.reset_mock()
            generate_sold_mail_ids_mock.reset_mock()
            filenames = [
                f"{platform.code}_sold_mail_with_id.txt",
                f"{platform.code}_sold_mail_without_id.txt"
            ]
            gmails = [self.get_gmail(filename) for filename in filenames]
            gmail_api_mock.get_mail.side_effect = gmails
            mail_ids = [f"mail_id_{i}" for i in range(len(gmails))]
            generate_sold_mail_ids_mock.return_value = mail_ids
            with self.subTest(platform=platform.name):
                gen = cancel.generate_sold_item_ids(gmail_api_mock, platform)
                self.assertListEqual(list(gen), ["XXXXXXXXX"])
                generate_sold_mail_ids_mock.assert_called_once_with(gmail_api_mock, platform)


@mock.patch("cropsiss.google.sheet.SpreadsheetAPI", spec_set=google.SpreadsheetAPI)
class Test_update_sold_to_true(TestCase):

    def test_spreadsheet_id(
        self,
        spreadsheet_api_mock: mock.Mock
    ) -> None:
        spreadsheet_ids = [f"spreadsheet_id{i}" for i in range(3)]
        index = 1
        for spreadsheet_id in spreadsheet_ids:
            spreadsheet_api_mock.reset_mock()
            with self.subTest(index=index):
                cancel.update_sold_to_true(spreadsheet_api_mock, spreadsheet_id, index)
                spreadsheet_api_mock.update_values.assert_called_once_with(
                    spreadsheet_id=spreadsheet_id,
                    range=f"{sheet.SOLD_COLUMN}{index+2}",
                    values=[["TRUE"]],
                    input_option="USER_ENTERED"
                )

    def test_index(
        self,
        spreadsheet_api_mock: mock.Mock
    ) -> None:
        spreadsheet_id = "spreadsheet_id"
        indexes = list(range(3))
        for index in indexes:
            spreadsheet_api_mock.reset_mock()
            with self.subTest(index=index):
                cancel.update_sold_to_true(spreadsheet_api_mock, spreadsheet_id, index)
                spreadsheet_api_mock.update_values.assert_called_once_with(
                    spreadsheet_id=spreadsheet_id,
                    range=f"{sheet.SOLD_COLUMN}{index+2}",
                    values=[["TRUE"]],
                    input_option="USER_ENTERED"
                )
