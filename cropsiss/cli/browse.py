# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
import time
import typing as t

import click
from selenium import webdriver

from cropsiss.cli import root


CHROME_DATA_DIR = root.APPDIR / "chrome-user-data"
DEFAULT_CHROME_ARGS = [f"--user-data-dir={CHROME_DATA_DIR}"]


def chrome_args_callback(
    ctx: click.Context,
    param: click.Option,
    value: t.Any
) -> webdriver.ChromeOptions:
    assert isinstance(value, tuple)
    chrome_options = webdriver.ChromeOptions()
    for arg in DEFAULT_CHROME_ARGS:
        chrome_options.add_argument(arg)
    for arg in value:
        chrome_options.add_argument(arg)
    return chrome_options


chrome_options = click.option(
    "--chrome-arg", "chrome_options",
    type=str,
    multiple=True,
    callback=chrome_args_callback,
    help="Additional arguments for Chrome browser"
)


@root.main.command(
    name="browser",
    help="Open a browser for the application"
)
@click.argument(
    "url",
    nargs=1,
    default=""
)
@chrome_options
def main(
    url: str,
    chrome_options: webdriver.ChromeOptions
) -> None:  # pragma: no cover
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url or "https://google.com")
        while driver.current_url:
            time.sleep(1)
    except Exception:
        driver.quit()
