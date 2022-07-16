# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
from unittest import TestCase, mock
import typing as t

from cropsiss.google import sheet, credentials


CREDENTIALS_MOCK = mock.Mock(spec_set=credentials.Credentials)
MajorDimension = t.Literal["ROWS", "COLUMNS"]
InputOption = t.Literal["RAW", "USER_ENTERED"]


class TestSpreasheetAPI_properties(TestCase):

    def setUp(self) -> None:
        self.api = sheet.SpreadsheetAPI(CREDENTIALS_MOCK)

    def test_service_name(self) -> None:
        self.assertEqual(self.api.service_name, "sheets")

    def test__service(self) -> None:
        with mock.patch("cropsiss.google.abstract.build_service") as build_mock:
            self.assertEqual(
                self.api._service,
                build_mock.return_value
            )
            build_mock.assert_called_once_with(self.api)


class TestSpreadsheetAPI_get_values(TestCase):

    def setUp(self) -> None:
        self.api = sheet.SpreadsheetAPI(CREDENTIALS_MOCK)

    def _test(
        self,
        spreadsheet_id: str = "",
        range: str = "",
        major_dimension: MajorDimension = "ROWS",
    ) -> None:
        values = [
            [spreadsheet_id],
            [range],
            [major_dimension]
        ]
        with mock.patch("cropsiss.google.sheet.SpreadsheetAPI._service") as service_mock:
            service_mock \
                .spreadsheets.return_value \
                .values.return_value \
                .get.return_value \
                .execute.return_value = {
                    "values": values
                }
            self.assertListEqual(
                self.api.get_values(spreadsheet_id, range, major_dimension),
                values
            )
        service_mock \
            .spreadsheets.return_value \
            .values.return_value \
            .get.assert_called_once_with(
                spreadsheetId=spreadsheet_id,
                range=range,
                majorDimension=major_dimension
            )

    def test_spreadsheet_id(self) -> None:
        spreadsheet_ids = [f"spreadsheetId{i}" for i in range(3)]
        for spreadsheet_id in spreadsheet_ids:
            with self.subTest(spreadsheet_id=spreadsheet_id):
                self._test(spreadsheet_id=spreadsheet_id)

    def test_range(self) -> None:
        ranges = [f"A{i}:C{i+3}" for i in range(1, 4)]
        for _range in ranges:
            with self.subTest(range=_range):
                self._test(range=_range)

    def test_major_dimension(self) -> None:
        major_dimensions: list[MajorDimension] = ["ROWS", "COLUMNS"]
        for major_dimension in major_dimensions:
            with self.subTest(major_dimension=major_dimension):
                self._test(major_dimension=major_dimension)


class TestSpreadsheetAPI_update_values(TestCase):

    def setUp(self) -> None:
        self.api = sheet.SpreadsheetAPI(CREDENTIALS_MOCK)

    def _test(
        self,
        spreadsheet_id: str = "",
        range: str = "",
        values: list[list[str]] = [[]],
        major_dimension: MajorDimension = "ROWS",
        input_option: InputOption = "RAW",
    ) -> None:
        with mock.patch("cropsiss.google.sheet.SpreadsheetAPI._service") as service_mock:
            self.api.update_values(
                spreadsheet_id,
                range,
                values,
                major_dimension,
                input_option
            )
        service_mock \
            .spreadsheets.return_value \
            .values.return_value \
            .update.assert_called_once_with(
                spreadsheetId=spreadsheet_id,
                range=range,
                valueInputOption=input_option,
                body={
                    "range": range,
                    "majorDimension": major_dimension,
                    "values": values
                }
            )

    def test_spreadsheet_id(self) -> None:
        spreadsheet_ids = [f"spreadsheetId{i}" for i in range(3)]
        for spreadsheet_id in spreadsheet_ids:
            with self.subTest(spreadsheet_id=spreadsheet_id):
                self._test(spreadsheet_id=spreadsheet_id)

    def test_range(self) -> None:
        ranges = [f"A{i}:C{i+3}" for i in range(1, 4)]
        for _range in ranges:
            with self.subTest(range=_range):
                self._test(range=_range)

    def test_values(self) -> None:
        values_list = [
            [
                [f"value{i+j+k}" for i in range(3)]
                for j in range(3)
            ]
            for k in range(3)
        ]
        for values in values_list:
            with self.subTest(values=values):
                self._test(values=values)

    def test_major_dimension(self) -> None:
        major_dimensions: list[MajorDimension] = ["ROWS", "COLUMNS"]
        for major_dimension in major_dimensions:
            with self.subTest(major_dimension=major_dimension):
                self._test(major_dimension=major_dimension)

    def test_input_option(self) -> None:
        input_options: list[InputOption] = ["RAW", "USER_ENTERED"]
        for input_option in input_options:
            with self.subTest(input_option=input_option):
                self._test(input_option=input_option)


class TestSpreadsheetAPI_clear_values(TestCase):

    def setUp(self) -> None:
        self.api = sheet.SpreadsheetAPI(CREDENTIALS_MOCK)

    def _test(
        self,
        spreadsheet_id: str = "",
        range: str = ""
    ) -> None:
        with mock.patch("cropsiss.google.sheet.SpreadsheetAPI._service") as service_mock:
            self.api.clear_values(spreadsheet_id, range)
        service_mock \
            .spreadsheets.return_value \
            .values.return_value \
            .clear.assert_called_once_with(
                spreadsheetId=spreadsheet_id,
                range=range,
                body={}
            )

    def test_spreadsheet_id(self) -> None:
        spreadsheet_ids = [f"spreadsheetId{i}" for i in range(3)]
        for spreadsheet_id in spreadsheet_ids:
            with self.subTest(spreadsheet_id=spreadsheet_id):
                self._test(spreadsheet_id=spreadsheet_id)

    def test_range(self) -> None:
        ranges = [f"A{i}:C{i+3}" for i in range(1, 4)]
        for _range in ranges:
            with self.subTest(range=_range):
                self._test(range=_range)


class TestSpreadsheetAPI_batch_update(TestCase):

    def setUp(self) -> None:
        self.api = sheet.SpreadsheetAPI(CREDENTIALS_MOCK)

    def test_spreadsheet_id(self) -> None:
        spreadsheet_ids = [f"spreadsheetId{i}" for i in range(3)]
        for spreadsheet_id in spreadsheet_ids:
            requests = {"requests": [spreadsheet_id]}
            with self.subTest(spreadsheet_id=spreadsheet_id):
                with mock.patch("cropsiss.google.sheet.SpreadsheetAPI._service") as service_mock:
                    self.api.batch_update(
                        spreadsheet_id,
                        requests,
                    )
                service_mock \
                    .spreadsheets.return_value \
                    .batchUpdate.assert_called_once_with(
                        spreadsheetId=spreadsheet_id,
                        body=requests,
                    )
