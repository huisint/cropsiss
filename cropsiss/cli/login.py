# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
import os

import click

from cropsiss import exceptions
from cropsiss.cli import root, config
from cropsiss import google


CREDENTIALS_FILE = root.APPDIR / "credentials.json"


def credentials_callback(
    ctx: click.Context,
    param: click.Option,
    filename: str
) -> google.Credentials:
    try:
        return google.Credentials.from_file(filename)
    except (ValueError, FileNotFoundError):
        raise exceptions.GoogleCredentialsInvalidError()


credentials_option = click.option(
    "--credentials",
    type=click.types.Path(dir_okay=False),
    default=str(CREDENTIALS_FILE),
    callback=credentials_callback,
    help="Path to credentials file"
)


@root.main.command(
    name="login",
    help="Get a new credentials for Google API"
)
@config.config_file_option
@click.option(
    "--no-local-server",
    is_flag=True,
    help="Do not run a local server for the authorization flow"
)
def login(
    config_file: str,
    no_local_server: bool
) -> None:
    cfg = config.Config.load(config_file)
    try:
        creds = google.Credentials.from_file(CREDENTIALS_FILE)
    except (FileNotFoundError, ValueError):
        creds = google.Credentials.new(
            client_id=cfg.client_id,
            client_secret=cfg.client_secret,
            run_local_server=not no_local_server
        )
    creds.save(CREDENTIALS_FILE)
    click.echo("Login succeeded")


@root.main.command(
    name="logout",
    help="Delete the current credentials for Google API"
)
def logout() -> None:
    if os.path.exists(CREDENTIALS_FILE):
        os.unlink(CREDENTIALS_FILE)
    click.echo("Logout succeeded")
