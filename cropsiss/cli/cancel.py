# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
import base64
import functools
import logging
import re
import typing as t

import click
from selenium import webdriver

import cropsiss
from cropsiss import platforms, exceptions
from cropsiss import google
from cropsiss.cli import root, config, login, sheet, browse


logger = logging.getLogger(__name__)


DONE_LABEL = "cropsiss-done"

item_ids = click.argument(
    "item_ids",
    nargs=-1,
)


@root.main.group(
    name="cancel",
    help="Cancel selling on a platform"
)
def main() -> None:
    pass


def cancel(
    item_id: str,
    platform: platforms.AbstractPlatform,
    chrome_options: webdriver.ChromeOptions
) -> None:
    try:
        platform.cancel(item_id, chrome_options)
        click.echo(f"{item_id}: succeeded")
    except exceptions.NotCancelError as err:
        logger.error(err)
        click.echo(f"{item_id}: failed")


@main.command(
    name="mercari",
    help="Cancel one or more items selling on Mercari"
)
@item_ids
@browse.chrome_options
def cancel_mercari(
    item_ids: tuple[str, ...],
    chrome_options: webdriver.ChromeOptions
) -> None:
    platform = platforms.Mercari()
    for item_id in item_ids:
        cancel(item_id, platform, chrome_options)


@main.command(
    name="yahuoku",
    help="Cancel one or more items selling on Yahoo!Auction"
)
@item_ids
@browse.chrome_options
def cancel_yahuoku(
    item_ids: tuple[str, ...],
    chrome_options: webdriver.ChromeOptions
) -> None:
    platform = platforms.YahooAuction()
    for item_id in item_ids:
        cancel(item_id, platform, chrome_options)


@main.command(
    name="mail",
    help="Cancel items through Gmail massages"
)
@click.option(
    "--mail-to",
    type=str,
    default="",
    help="An email is sent to the address when a cancellation is executed"
)
@browse.chrome_options
@login.credentials_option
@config.config_file_option
def cancel_through_mail(
    mail_to: str,
    chrome_options: webdriver.ChromeOptions,
    credentials: google.Credentials,
    config_file: str
) -> None:
    cfg = config.Config.load(config_file)
    sheet_api = google.SpreadsheetAPI(credentials)
    gmail_api = google.GmailAPI(credentials)
    system = root.System(gmail_api)
    RANGE = f"A2:{sheet.SOLD_COLUMN}"
    values = sheet_api.get_values(
        spreadsheet_id=cfg.spreadsheet_id,
        range=RANGE,
        major_dimension="ROWS"
    )
    logger.info(f"Getting values of {RANGE} on the Google Spreadsheet succeeded")
    logger.debug(
        f"The values of {RANGE}:\n"
        "\n".join(f"row {i}: {row}" for (i, row) in enumerate(values))
    )
    for platform in cropsiss.PLATFORMS:
        item_id_to_index = {
            str(row[platform.column_index]): idx
            for idx, row in enumerate(values)
            if row[platform.column_index]
        }
        for item_id in filter(item_id_to_index.__contains__, generate_sold_item_ids(gmail_api, platform)):
            index = item_id_to_index[item_id]
            update_sold_to_true(sheet_api, cfg.spreadsheet_id, index)
            row = [str(val) for val in values[index]]
            cropsiss_id = row[0]
            logger.info(f"Item:{cropsiss_id} should be canceled")
            for platform_to_cancel in filter(lambda p: p.id != platform.id, cropsiss.PLATFORMS):
                if item_id := row[platform_to_cancel.column_index]:
                    try:
                        platform_to_cancel.cancel(item_id, chrome_options)
                        logger.info(f"{item_id} of {platform_to_cancel.name} was canceled")
                        if mail_to:
                            system.notify_success(
                                mail_to=mail_to,
                                platform=platform_to_cancel,
                                item_id=item_id,
                                cropsiss_id=cropsiss_id
                            )
                    except exceptions.NotCancelError as err:
                        logger.error(err)
                        logger.error(f"Faild cancelling {cropsiss_id} - {item_id} on {platform_to_cancel.name}")
                        if mail_to:
                            system.notify_fail(
                                mail_to=mail_to,
                                platform=platform_to_cancel,
                                item_id=item_id,
                                cropsiss_id=cropsiss_id
                            )


@functools.lru_cache()
def get_donelabel_id(api: google.GmailAPI) -> str:
    donelabels = [label for label in api.get_labels() if label["name"] == DONE_LABEL]
    assert len(donelabels) <= 1, "The number of donelabels must be 1 or less"
    if donelabels:
        donelabel_id = str(donelabels[0]["id"])
    else:
        donelabel_id = str(api.create_label(DONE_LABEL)["id"])
    assert donelabel_id
    logger.info(f"Getting Label:{donelabel_id} as a done-label succeeded")
    return donelabel_id


def generate_sold_mail_ids(
    api: google.GmailAPI,
    platform: platforms.AbstractPlatform
) -> t.Generator[str, None, None]:
    DONELABEL_ID = get_donelabel_id(api)
    QUERY = platform.sold_mail_query + " AND -{label:" + DONE_LABEL + "}"
    for mail_id in api.search_mail(QUERY):
        yield mail_id
        api.add_labels(mail_id, [DONELABEL_ID])
        logger.info(f"The done-label was added to Mail: {mail_id}")


def generate_sold_item_ids(
    api: google.GmailAPI,
    platform: platforms.AbstractPlatform
) -> t.Generator[str, None, None]:
    for mail_id in generate_sold_mail_ids(api, platform):
        gmail = api.get_mail(mail_id)
        body = base64.urlsafe_b64decode(gmail["payload"]["body"]["data"]).decode("utf-8")
        if match := re.search(platform.item_id_pattern, body):
            yield match[0]


def update_sold_to_true(
    api: google.SpreadsheetAPI,
    spreadsheet_id: str,
    index: int
) -> None:
    RANGE = f"{sheet.SOLD_COLUMN}{index+2}"
    api.update_values(
        spreadsheet_id=spreadsheet_id,
        range=RANGE,
        values=[["TRUE"]],
        input_option="USER_ENTERED"
    )
    logger.info(f"The value of {RANGE} was updated to TRUE")
