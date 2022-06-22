# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
import logging
import webbrowser

import click

import cropsiss
from cropsiss import google
from cropsiss.cli import root, config, login


logger = logging.getLogger(__name__)

SOLD_COLUMN = "E"
SOLD_COLUMN_INDEX = ord(SOLD_COLUMN) - 65


@root.main.group(
    name="sheet",
    help="Manage the Google Spreadsheet"
)
def main() -> None:
    pass


CLEAR = {
    "deleteRange": {
        "range": {
            "sheetId": 0,
            "startColumnIndex": 0,
            "endColumnIndex": SOLD_COLUMN_INDEX + 1
        },
        "shiftDimension": "COLUMNS"
    }
}
SET_SHEET_NAME = {
    "updateSheetProperties": {
        "properties": {
            "sheetId": 0,
            "title": "ID管理"
        },
        "fields": "title"
    }
}
FORMAT_CROPSISS_COLUMN = [
    {
        "updateDimensionProperties": {
            "range": {
                "sheetId": 0,
                "dimension": "COLUMNS",
                "startIndex": 0,
                "endIndex": 1
            },
            "properties": {
                "pixelSize": 100
            },
            "fields": "pixelSize"
        }
    },
    {
        "repeatCell": {
            "range": {
                "sheetId": 0,
                "startColumnIndex": 0,
                "endColumnIndex": 1
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 0.8117,
                        "green": 0.8862,
                        "blue": 0.9529
                    }
                }
            },
            "fields": "userEnteredFormat"
        }
    },
    {
        "repeatCell": {
            "range": {
                "sheetId": 0,
                "startColumnIndex": 0,
                "endColumnIndex": 1,
                "startRowIndex": 0,
                "endRowIndex": 1
            },
            "cell": {
                "userEnteredValue": {
                    "stringValue": "CropsissID"
                },
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 0.2392,
                        "green": 0.5215,
                        "blue": 0.7764
                    },
                    "textFormat": {
                        "foregroundColor": {
                            "red": 1.0,
                            "green": 1.0,
                            "blue": 1.0
                        }
                    }
                }
            },
            "fields": "userEnteredFormat,userEnteredValue"
        }
    },
]
FORMAT_NAME_CULUMN = [
    {
        "updateDimensionProperties": {
            "range": {
                "sheetId": 0,
                "dimension": "COLUMNS",
                "startIndex": 1,
                "endIndex": 2
            },
            "properties": {
                "pixelSize": 250
            },
            "fields": "pixelSize"
        }
    },
    {
        "repeatCell": {
            "range": {
                "sheetId": 0,
                "startColumnIndex": 1,
                "endColumnIndex": 2
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 0.8510,
                        "green": 0.9176,
                        "blue": 0.8274
                    }
                }
            },
            "fields": "userEnteredFormat"
        }
    },
    {
        "repeatCell": {
            "range": {
                "sheetId": 0,
                "startColumnIndex": 1,
                "endColumnIndex": 2,
                "startRowIndex": 0,
                "endRowIndex": 1
            },
            "cell": {
                "userEnteredValue": {
                    "stringValue": "商品名"
                },
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 0.2196,
                        "green": 0.4627,
                        "blue": 0.1137
                    },
                    "textFormat": {
                        "foregroundColor": {
                            "red": 1.0,
                            "green": 1.0,
                            "blue": 1.0
                        }
                    }
                }
            },
            "fields": "userEnteredFormat,userEnteredValue"
        }
    },
]
FORMAT_MERCARI_COLUMN = [
    {
        "updateDimensionProperties": {
            "range": {
                "sheetId": 0,
                "dimension": "COLUMNS",
                "startIndex": cropsiss.PLATFORMS[0].column_index,
                "endIndex": cropsiss.PLATFORMS[0].column_index + 1
            },
            "properties": {
                "pixelSize": 200
            },
            "fields": "pixelSize"
        }
    },
    {
        "repeatCell": {
            "range": {
                "sheetId": 0,
                "startColumnIndex": cropsiss.PLATFORMS[0].column_index,
                "endColumnIndex": cropsiss.PLATFORMS[0].column_index + 1
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 0.8509,
                        "green": 0.8235,
                        "blue": 0.9137
                    }
                }
            },
            "fields": "userEnteredFormat"
        }
    },
    {
        "repeatCell": {
            "range": {
                "sheetId": 0,
                "startColumnIndex": cropsiss.PLATFORMS[0].column_index,
                "endColumnIndex": cropsiss.PLATFORMS[0].column_index + 1,
                "startRowIndex": 0,
                "endRowIndex": 1
            },
            "cell": {
                "userEnteredValue": {
                    "stringValue": "メルカリ商品ID"
                },
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 0.6,
                        "green": 0.0,
                        "blue": 1.0
                    },
                    "textFormat": {
                        "foregroundColor": {
                            "red": 1.0,
                            "green": 1.0,
                            "blue": 1.0
                        }
                    }
                }
            },
            "fields": "userEnteredFormat,userEnteredValue"
        }
    },
]
FORMAT_YAHUOKU_COLUMN = [
    {
        "updateDimensionProperties": {
            "range": {
                "sheetId": 0,
                "dimension": "COLUMNS",
                "startIndex": cropsiss.PLATFORMS[1].column_index,
                "endIndex": cropsiss.PLATFORMS[1].column_index + 1
            },
            "properties": {
                "pixelSize": 200
            },
            "fields": "pixelSize"
        }
    },
    {
        "repeatCell": {
            "range": {
                "sheetId": 0,
                "startColumnIndex": cropsiss.PLATFORMS[1].column_index,
                "endColumnIndex": cropsiss.PLATFORMS[1].column_index + 1
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 1.0,
                        "green": 0.9490,
                        "blue": 0.8
                    }
                }
            },
            "fields": "userEnteredFormat"
        }
    },
    {
        "repeatCell": {
            "range": {
                "sheetId": 0,
                "startColumnIndex": cropsiss.PLATFORMS[1].column_index,
                "endColumnIndex": cropsiss.PLATFORMS[1].column_index + 1,
                "startRowIndex": 0,
                "endRowIndex": 1
            },
            "cell": {
                "userEnteredValue": {
                    "stringValue": "ヤフオク!オークションID"
                },
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 1.0,
                        "green": 1.0,
                        "blue": 0.0
                    }
                }
            },
            "fields": "userEnteredFormat,userEnteredValue"
        }
    }
]
FORMAT_SOLD_COLUMN = [
    {
        "updateDimensionProperties": {
            "range": {
                "sheetId": 0,
                "dimension": "COLUMNS",
                "startIndex": SOLD_COLUMN_INDEX,
                "endIndex": SOLD_COLUMN_INDEX + 1
            },
            "properties": {
                "pixelSize": 100
            },
            "fields": "pixelSize"
        }
    },
    {
        "repeatCell": {
            "range": {
                "sheetId": 0,
                "startColumnIndex": SOLD_COLUMN_INDEX,
                "endColumnIndex": SOLD_COLUMN_INDEX + 1
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 0.8509,
                        "green": 0.8509,
                        "blue": 0.8509
                    }
                },
                "userEnteredValue": {
                    "boolValue": False
                }
            },
            "fields": "userEnteredFormat,userEnteredValue"
        }
    },
    {
        "repeatCell": {
            "range": {
                "sheetId": 0,
                "startColumnIndex": SOLD_COLUMN_INDEX,
                "endColumnIndex": SOLD_COLUMN_INDEX + 1,
                "startRowIndex": 0,
                "endRowIndex": 1
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 0.6,
                        "green": 0.6,
                        "blue": 0.6
                    },
                    "textFormat": {
                        "foregroundColor": {
                            "red": 1.0,
                            "green": 1.0,
                            "blue": 1.0
                        }
                    }
                },
                "userEnteredValue": {
                    "stringValue": "売却済み"
                }
            },
            "fields": "userEnteredFormat,userEnteredValue"
        }
    },
    {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": {
                    "sheetId": 0,
                    "startColumnIndex": SOLD_COLUMN_INDEX,
                    "endColumnIndex": SOLD_COLUMN_INDEX + 1,
                    "startRowIndex": 1
                },
                "booleanRule": {
                    "condition": {
                        "type": "TEXT_EQ",
                        "values": [
                            {
                                "userEnteredValue": "TRUE"
                            }
                        ]
                    },
                    "format": {
                        "backgroundColor": {
                            "red": 0.9529,
                            "green": 0.9529,
                            "blue": 0.9529
                        }
                    }
                }
            }
        }
    }
]
INIT_REQUESTS = [
    SET_SHEET_NAME,
    *FORMAT_NAME_CULUMN,
    *FORMAT_CROPSISS_COLUMN,
    *FORMAT_MERCARI_COLUMN,
    *FORMAT_YAHUOKU_COLUMN,
    *FORMAT_SOLD_COLUMN
]


@main.command(
    name="init",
    help="Initialize the Google Spreadsheet for the application"
)
@click.option(
    "--clear",
    is_flag=True,
    help=f"Clear all of the cells in A:{SOLD_COLUMN}"
)
@login.credentials_option
@config.config_file_option
def init_sheet(
    clear: bool,
    credentials: google.Credentials,
    config_file: str
) -> None:
    cfg = config.Config.load(config_file)
    SHEET_API = google.SpreadsheetAPI(credentials)
    requests = [CLEAR, *INIT_REQUESTS] if clear else INIT_REQUESTS
    SHEET_API.batch_update(
        spreadsheet_id=cfg.spreadsheet_id,
        requests={"requests": requests}
    )
    SHEET_API.update_values(
        spreadsheet_id=cfg.spreadsheet_id,
        range="A2:A1000",
        values=[[f"c{i:05}" for i in range(1, 1000)]],
        major_dimension="COLUMNS"
    )
    click.echo("Initialized the Google Spreadsheet")


@main.command(
    name="open",
    help="Open the Google Spreadsheet"
)
@config.config_file_option
def open_sheet(
    config_file: str
) -> None:
    cfg = config.Config.load(config_file)
    url = f"https://docs.google.com/spreadsheets/d/{cfg.spreadsheet_id}/edit"
    webbrowser.open(url)


@main.command(
    name="update",
    help="Update the value of a cell on the Google Spreadsheet"
)
@click.option(
    "--cropsiss-id", "-c",
    type=str,
    required=True,
    help="The cropsiss ID"
)
@click.option(
    "--platform", "-p",
    type=click.Choice([platform.code for platform in cropsiss.PLATFORMS]),
    required=True,
    help="The target platform"
)
@click.option(
    "--value", "-v",
    type=str,
    required=True,
    help="The ID assigned by the platform"
)
@login.credentials_option
@config.config_file_option
def update_sheet(
    cropsiss_id: str,
    platform: str,
    value: str,
    credentials: google.Credentials,
    config_file: str
) -> None:
    cfg = config.Config.load(config_file)
    SHEET_API = google.SpreadsheetAPI(credentials)
    CROPSISS_IDS = SHEET_API.get_values(
        spreadsheet_id=cfg.spreadsheet_id,
        range="A2:A",
        major_dimension="COLUMNS"
    )[0]
    try:
        idx = CROPSISS_IDS.index(cropsiss_id)
    except ValueError:
        exit(f"cropsissID-{cropsiss_id} does not exist on the Google Spreadsheet")
    COLUMNS: dict[str, str] = {p.code: chr(p.column_index+65) for p in cropsiss.PLATFORMS}
    CELL = f"{COLUMNS[platform]}{idx+2}"
    SHEET_API.update_values(
        spreadsheet_id=cfg.spreadsheet_id,
        range=CELL,
        values=[[value]]
    )
    click.echo(f"Updated {CELL} to {value}")
