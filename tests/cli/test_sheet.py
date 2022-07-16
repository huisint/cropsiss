# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
from unittest import TestCase, mock
import typing as t

from click import testing

import cropsiss
from cropsiss import platforms
from cropsiss.cli import sheet, root, config


RUNNER = testing.CliRunner()
CONFIG = config.Config(spreadsheet_id="spreadsheet_id")
CONFIG_PATCHER = mock.patch("cropsiss.cli.config.Config.load", return_value=CONFIG)
CREDENTIALS_PATCHER = mock.patch("cropsiss.google.credentials.Credentials.from_file")

MajorDimension = t.Literal["ROWS", "COLUMNS"]
InputOption = t.Literal["RAW", "USER_ENTERED"]


def setUpModule() -> None:
    CONFIG_PATCHER.start()
    CREDENTIALS_PATCHER.start()


def tearDownModule() -> None:
    CONFIG_PATCHER.stop()
    CREDENTIALS_PATCHER.stop()


@mock.patch("cropsiss.google.sheet.SpreadsheetAPI.update_values")
@mock.patch("cropsiss.google.sheet.SpreadsheetAPI.batch_update")
class Test_init_sheet(TestCase):

    def _test(
        self,
        args: list[str],
        batch_update_mock: mock.Mock,
        update_values_mock: mock.Mock
    ) -> None:
        result = RUNNER.invoke(root.main, args, catch_exceptions=False)
        self.assertEqual(result.output, "Initialized the Google Spreadsheet\n")
        self.assertEqual(result.exit_code, 0)
        batch_update_mock.assert_called_once_with(
            spreadsheet_id=CONFIG.spreadsheet_id,
            requests={
                "requests": [sheet.CLEAR, *sheet.INIT_REQUESTS] if "--clear" in args else sheet.INIT_REQUESTS
            }
        )
        update_values_mock.assert_called_once_with(
            spreadsheet_id=CONFIG.spreadsheet_id,
            range="A2:A1000",
            values=[[f"c{i:05}" for i in range(1, 1000)]],
            major_dimension="COLUMNS"
        )

    def test_success(
        self,
        batch_update_mock: mock.Mock,
        update_values_mock: mock.Mock,
    ) -> None:
        args = [str(sheet.main.name), str(sheet.init_sheet.name)]
        self._test(args, batch_update_mock, update_values_mock)

    def test_clear(
        self,
        batch_update_mock: mock.Mock,
        update_values_mock: mock.Mock,
    ) -> None:
        args = [str(sheet.main.name), str(sheet.init_sheet.name), "--clear"]
        self._test(args, batch_update_mock, update_values_mock)


@mock.patch("webbrowser.open")
class Test_open_sheet(TestCase):

    def test_success(self, open_mock: mock.Mock) -> None:
        result = RUNNER.invoke(root.main, [str(sheet.main.name), str(sheet.open_sheet.name)], catch_exceptions=False)
        self.assertEqual(result.output, "")
        url = f"https://docs.google.com/spreadsheets/d/{CONFIG.spreadsheet_id}/edit"
        open_mock.assert_called_once_with(url)


@mock.patch("cropsiss.google.sheet.SpreadsheetAPI.update_values")
@mock.patch("cropsiss.google.sheet.SpreadsheetAPI.get_values")
class Test_update_sheet(TestCase):

    def _test_success(
        self,
        get_values_mock: mock.Mock,
        update_values_mock: mock.Mock,
        cropsiss_id: str = "c00001",
        platform: platforms.AbstractPlatform = cropsiss.PLATFORMS[0],
        value: str = "m0000000001"
    ) -> None:
        cell = f"{chr(platform.column_index+65)}{int(cropsiss_id.strip('c'))+1}"
        result = RUNNER.invoke(
                root.main,
                [
                    str(sheet.main.name),
                    str(sheet.update_sheet.name),
                    "-c", cropsiss_id,
                    "-p", platform.code,
                    "-v", value
                ],
                catch_exceptions=False
            )
        self.assertEqual(result.output, f"Updated {cell} to {value}\n")
        self.assertEqual(result.exit_code, 0)
        get_values_mock.assert_called_once_with(
            spreadsheet_id=CONFIG.spreadsheet_id,
            range="A2:A",
            major_dimension="COLUMNS"
        )
        update_values_mock.assert_called_once_with(
            spreadsheet_id=CONFIG.spreadsheet_id,
            range=cell,
            values=[[value]]
        )

    def test_cropsiss_id_exists(
        self,
        get_values_mock: mock.Mock,
        update_values_mock: mock.Mock
    ) -> None:
        cropsiss_ids = [f"c{i:05}" for i in range(1, 5)]
        get_values_mock.return_value = [cropsiss_ids]
        for cropsiss_id in cropsiss_ids:
            get_values_mock.reset_mock()
            update_values_mock.reset_mock()
            with self.subTest(cropsiss_id=cropsiss_id):
                self._test_success(
                    get_values_mock,
                    update_values_mock,
                    cropsiss_id=cropsiss_id
                )

    def test_cropsiss_id_does_not_exist(
        self,
        get_values_mock: mock.Mock,
        update_values_mock: mock.Mock
    ) -> None:
        get_values_mock.return_value = [[f"c{i:05}" for i in range(1, 5)]]
        cropsiss_id = "c10000"
        platform = cropsiss.PLATFORMS[0]
        value = "m0000000001"
        result = RUNNER.invoke(
            root.main,
            [
                str(sheet.main.name),
                str(sheet.update_sheet.name),
                "-c", cropsiss_id,
                "-p", platform.code,
                "-v", value
            ],
            catch_exceptions=False
        )
        self.assertEqual(
            result.output, f"cropsissID-{cropsiss_id} does not exist on the Google Spreadsheet\n"
        )
        self.assertEqual(result.exit_code, 1)
        update_values_mock.assert_not_called()

    def test_platform(
        self,
        get_values_mock: mock.Mock,
        update_values_mock: mock.Mock
    ) -> None:
        get_values_mock.return_value = [[f"c{i:05}" for i in range(1, 5)]]
        for platform in cropsiss.PLATFORMS:
            get_values_mock.reset_mock()
            update_values_mock.reset_mock()
            with self.subTest(platform=platform.name):
                self._test_success(
                    get_values_mock,
                    update_values_mock,
                    platform=platform
                )

    def test_value(
        self,
        get_values_mock: mock.Mock,
        update_values_mock: mock.Mock
    ) -> None:
        get_values_mock.return_value = [[f"c{i:05}" for i in range(1, 5)]]
        values = [f"m{i:09}" for i in range(3)]
        for value in values:
            get_values_mock.reset_mock()
            update_values_mock.reset_mock()
            with self.subTest(value=value):
                self._test_success(
                    get_values_mock,
                    update_values_mock,
                    value=value
                )
