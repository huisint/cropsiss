# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
from __future__ import annotations
import os
import dataclasses
import typing as t

import click
import dataclasses_json

from cropsiss import exceptions
from cropsiss.cli import root


CONFIG_FILE = root.APPDIR / "config.json"


@dataclasses_json.dataclass_json()
@dataclasses.dataclass()
class Config:
    spreadsheet_id: str = ""        # required
    client_id: str = ""             # optional
    client_secret: str = ""         # optional

    @property
    def required_fields(self) -> list[str]:
        return [
            "spreadsheet_id"
        ]

    @classmethod
    def load(
        cls,
        filename: str | os.PathLike[str],
        check_required: bool = True
    ) -> Config:
        if not os.path.exists(filename):
            raise exceptions.ConfigFileNotFoundError()
        with open(filename) as f:
            cfg = cls.from_json(f.read())
        if check_required:
            for field in cfg.required_fields:
                if not bool(cfg.__getattribute__(field)):
                    raise exceptions.ConfigInsufficientError(f"{field} is empty")
        return cfg

    def save(self, filename: str | os.PathLike[str]) -> None:
        with open(filename, "w") as f:
            f.write(self.to_json(indent=2))

    def to_json(self, *args: t.Any, **kwargs: t.Any) -> str:
        """Convert to JSON text"""

    @classmethod
    def from_json(cls, *args: t.Any, **kwargs: t.Any) -> Config:
        """Create a Config instance from JSON text"""


config_file_option = click.option(
    "--config-file",
    type=click.types.Path(dir_okay=False),
    default=str(CONFIG_FILE),
    help="Path to config file"
)


@root.main.group(
    name="config",
    help="Configure the application"
)
def main() -> None:
    pass


@main.command(
    name="new",
    help="Create a new configuration file"
)
@click.option(
    "--spreadsheet-id",
    type=str,
    required=True,
    prompt="Google Spreadsheet ID(required)",
    help="The ID of a Google SpreadSheet"
)
@click.option(
    "--client-id",
    type=str,
    default=Config.client_id,
    prompt="Client ID(optional)",
    help="The client ID of a GCP project"
)
@click.option(
    "--client-secret",
    type=str,
    default=Config.client_secret,
    prompt="Client Secret(optional)",
    help="The client secret of a GCP project"
)
@config_file_option
def create_new_config(
    spreadsheet_id: str,
    client_id: str,
    client_secret: str,
    config_file: str
) -> None:
    cfg = Config(
        spreadsheet_id=spreadsheet_id,
        client_id=client_id,
        client_secret=client_secret,
    )
    cfg.save(config_file)
    click.echo("Created a new config file")


@main.command(
    name="show",
    help="Show the current configuration"
)
@config_file_option
@click.option(
    "--json",
    is_flag=True,
    help="Output as JSON text"
)
def show_config(
    config_file: str,
    json: bool
) -> None:
    cfg = Config.load(config_file, check_required=False)
    if json:
        click.echo(cfg.to_json(indent=2))
    else:
        click.echo("\n".join(f"{key}={val}" for key, val in cfg.__dict__.items()))


@main.command(
    name="update",
    help="Update the configuration"
)
@click.option(
    "--field", "-f",
    type=click.types.Choice(list(Config.__dict__.keys())),
    required=True,
    help="The field name of the configuration"
)
@click.option(
    "--value", "-v",
    type=str,
    required=True,
    help="The value of the field"
)
@config_file_option
def update_config(
    field: str,
    value: str,
    config_file: str
) -> None:
    cfg = Config.load(config_file, check_required=False)
    cfg.__setattr__(field, value)
    cfg.save(config_file)
