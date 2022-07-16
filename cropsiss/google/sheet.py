# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
import dataclasses
import typing as t

from cropsiss.google import abstract


@dataclasses.dataclass()
class SpreadsheetAPI(abstract.AbstractAPI):

    def __post_init__(self) -> None:
        super().__init__(self.credentials, self.version or "v4")

    @property
    def service_name(self) -> str:
        return "sheets"

    @property
    def _service(self) -> t.Any:
        return abstract.build_service(self)

    def get_values(
        self,
        spreadsheet_id: str,
        range: str,
        major_dimension: t.Literal["ROWS", "COLUMNS"] = "ROWS"
    ) -> list[list[t.Any]]:
        """Get a range of values from a spreadsheet.

        Parameters
        ----------
        spreadsheet_id : str
            The ID of the spreadsheet to retrieve data from.
        range : str
            The A1 notation or R1C1 notation of the range to retrieve.
        major_dimenstion : Literal["ROWS", "COLUMNS"]
            The major dimension that results should use.

        Returns
        -------
        list[list[Any]]
            A range of values from a spreadsheet.

        See Also
        --------
        https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/get
        """
        response = self._service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range,
            majorDimension=major_dimension
        ).execute()
        return [list(row) for row in response["values"]]

    def update_values(
        self,
        spreadsheet_id: str,
        range: str,
        values: list[list[str]],
        major_dimension: t.Literal["ROWS", "COLUMNS"] = "ROWS",
        input_option: t.Literal["RAW", "USER_ENTERED"] = "RAW"
    ) -> None:
        """Set values in a range of a spreadsheet.

        Parameters
        ----------
        spreadsheet_id : str
            The ID of the spreadsheet to update.
        range : str
            The A1 notation of the values to update.
        major_dimension : Literal["ROWS", "COLUMNS"]
            The major dimension of the values.
        input_option : Literal["RAW", "USER_ENTERED"]
            How the input data should be interpreted.
            See also https://developers.google.com/sheets/api/reference/rest/v4/ValueInputOption

        See Also
        --------
        https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/update
        """
        body = {
            "range": range,
            "majorDimension": major_dimension,
            "values": values
        }
        self._service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range,
            valueInputOption=input_option,
            body=body
        ).execute()

    def clear_values(
        self,
        spreadsheet_id: str,
        range: str
    ) -> None:
        """Clear values from a spreadsheet.

        Parameters
        ----------
        spreadsheet_id : str
            The ID of the spreadsheet to update.
        range : str
            The A1 notation or R1C1 notation of the values to clear.

        See Also
        --------
        https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/clear
        """
        self._service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=range,
            body={}
        ).execute()

    def batch_update(
        self,
        spreadsheet_id: str,
        requests: t.Any
    ) -> None:
        """Apply one or more updates to the spreadsheet.

        Parameters
        ----------
        spreadsheet_id : str
            The ID of the spreadsheet to update.
        requests : Any
            A list of updates to apply to the spreadsheet.

        See Also
        --------
        https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/batchUpdate
        """
        self._service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=requests,
        ).execute()
