# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
from unittest import TestCase, mock
from typing import Literal

from cropsiss.google import sheet, credentials


Credentials = mock.Mock(spec_set=credentials.Credentials)
MajorDimension = Literal["ROWS", "COLUMNS"]
InputOption = Literal["RAW", "USER_ENTERED"]


class TestSpreasheetAPI_properties(TestCase):
    api: sheet.SpreadsheetAPI

    def setUp(self) -> None:
        self.api = sheet.SpreadsheetAPI(Credentials())

    def test_service_name(self) -> None:
        self.assertEqual(self.api.service_name, "sheets")


class TestSpreadsheetAPI_get_values(TestCase):
    api: sheet.SpreadsheetAPI

    def setUp(self) -> None:
        self.api = sheet.SpreadsheetAPI(Credentials())

    def _test(
        self, spreadsheet_id: str, range: str, major_dimension: MajorDimension, values: list[list[str]]
    ) -> None:
        self.api._service = mock.Mock()
        self.api._service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            "values": values
        }
        self.assertListEqual(self.api.get_values(spreadsheet_id, range, major_dimension), values)
        self.api._service.spreadsheets.return_value.values.return_value.get.assert_called_once_with(
            spreadsheetId=spreadsheet_id, range=range, majorDimension=major_dimension
        )

    def test_spreadsheet_id(self) -> None:
        spreadsheet_ids = [f"spreadsheetId{i}" for i in range(3)]
        _range = "A1:C10"
        major_dimension: MajorDimension = "ROWS"
        for spreadsheet_id in spreadsheet_ids:
            with self.subTest(spreadsheet_id=spreadsheet_id):
                values = [[spreadsheet_id]]
                self._test(spreadsheet_id, _range, major_dimension, values)

    def test_range(self) -> None:
        spreadsheet_id = "spreadsheetId"
        ranges = [f"A{i}:C{i+3}" for i in range(1, 4)]
        major_dimension: MajorDimension = "ROWS"
        for _range in ranges:
            with self.subTest(range=_range):
                values = [[_range]]
                self._test(spreadsheet_id, _range, major_dimension, values)

    def test_major_dimension(self) -> None:
        spreadsheet_id = "spreadsheetId"
        _range = "A1:C10"
        major_dimensions: list[MajorDimension] = ["ROWS", "COLUMNS"]
        for major_dimension in major_dimensions:
            with self.subTest(major_dimension=major_dimension):
                values = [[str(major_dimension)]]
                self._test(spreadsheet_id, _range, major_dimension, values)


class TestSpreadsheetAPI_update_values(TestCase):
    api: sheet.SpreadsheetAPI

    def setUp(self) -> None:
        self.api = sheet.SpreadsheetAPI(Credentials())

    def _test(
        self,
        spreadsheet_id: str,
        range: str,
        values: list[list[str]],
        major_dimension: MajorDimension,
        input_option: InputOption,
    ) -> None:
        self.api._service = mock.Mock()
        self.api.update_values(spreadsheet_id, range, values, major_dimension, input_option)
        self.api._service.spreadsheets.return_value.values.return_value.update.assert_called_once_with(
            spreadsheetId=spreadsheet_id,
            range=range,
            valueInputOption=input_option,
            body={"range": range, "majorDimension": major_dimension, "values": values},
        )

    def test_spreadsheet_id(self) -> None:
        spreadsheet_ids = [f"spreadsheetId{i}" for i in range(3)]
        _range = "A1:C10"
        major_dimension: MajorDimension = "ROWS"
        input_option: InputOption = "RAW"
        for spreadsheet_id in spreadsheet_ids:
            with self.subTest(spreadsheet_id=spreadsheet_id):
                values = [[spreadsheet_id]]
                self._test(spreadsheet_id, _range, values, major_dimension, input_option)

    def test_range(self) -> None:
        spreadsheet_id = "spreadsheetId"
        ranges = [f"A{i}:C{i+3}" for i in range(1, 4)]
        major_dimension: MajorDimension = "ROWS"
        input_option: InputOption = "RAW"
        for _range in ranges:
            with self.subTest(range=_range):
                values = [[_range]]
                self._test(spreadsheet_id, _range, values, major_dimension, input_option)

    def test_major_dimension(self) -> None:
        spreadsheet_id = "spreadsheetId"
        _range = "A1:C10"
        major_dimensions: list[MajorDimension] = ["ROWS", "COLUMNS"]
        input_option: InputOption = "RAW"
        for major_dimension in major_dimensions:
            with self.subTest(major_dimension=major_dimension):
                values = [[str(major_dimension)]]
                self._test(spreadsheet_id, _range, values, major_dimension, input_option)

    def test_input_option(self) -> None:
        spreadsheet_id = "spreadsheetId"
        _range = "A1:C10"
        major_dimension: MajorDimension = "ROWS"
        input_options: list[InputOption] = ["RAW", "USER_ENTERED"]
        for input_option in input_options:
            with self.subTest(input_option=input_option):
                values = [[str(input_option)]]
                self._test(spreadsheet_id, _range, values, major_dimension, input_option)


class TestSpreadsheetAPI_clear_values(TestCase):
    api: sheet.SpreadsheetAPI

    def setUp(self) -> None:
        self.api = sheet.SpreadsheetAPI(Credentials())

    def _test(self, spreadsheet_id: str, range: str) -> None:
        self.api._service = mock.Mock()
        self.api.clear_values(spreadsheet_id, range)
        self.api._service.spreadsheets.return_value.values.return_value.clear.assert_called_once_with(
            spreadsheetId=spreadsheet_id, range=range, body={}
        )

    def test_spreadsheet_id(self) -> None:
        spreadsheet_ids = [f"spreadsheetId{i}" for i in range(3)]
        _range = "A1:C10"
        for spreadsheet_id in spreadsheet_ids:
            with self.subTest(spreadsheet_id=spreadsheet_id):
                self._test(spreadsheet_id, _range)

    def test_range(self) -> None:
        spreadsheet_id = "spreadsheetId"
        ranges = [f"A{i}:C{i+3}" for i in range(1, 4)]
        for _range in ranges:
            with self.subTest(range=_range):
                self._test(spreadsheet_id, _range)


class TestSpreadsheetAPI_batch_update(TestCase):
    api: sheet.SpreadsheetAPI

    def setUp(self) -> None:
        self.api = sheet.SpreadsheetAPI(Credentials())

    def test_spreadsheet_id(self) -> None:
        spreadsheet_ids = [f"spreadsheetId{i}" for i in range(3)]
        for spreadsheet_id in spreadsheet_ids:
            self.api._service = mock.Mock()
            requests = {"requests": [spreadsheet_id]}
            with self.subTest(spreadsheet_id=spreadsheet_id):
                self.api.batch_update(
                    spreadsheet_id,
                    requests,
                )
                self.api._service.spreadsheets.return_value.batchUpdate.assert_called_once_with(
                    spreadsheetId=spreadsheet_id,
                    body=requests,
                )
