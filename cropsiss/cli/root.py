# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
import pathlib
import logging
import logging.handlers
import typing as t

import click
import click_log
import jinja2

from cropsiss import exceptions, google, platforms, __version__


logger = logging.getLogger("cropsiss")
click_log.basic_config(logger)


APPNAME = "cropsiss"
APPDIR = pathlib.Path(click.get_app_dir(APPNAME, roaming=False))
LOGDIR = APPDIR / "logs"
TEMPLATESDIR = APPDIR / "templates"


class System:
    _gmail_api: google.GmailAPI
    _jinja_env: jinja2.Environment
    developer_form = "https://forms.gle/h2L6KVqM6yJyNqwC8"

    def __init__(
        self,
        gmail_api: google.GmailAPI,
    ) -> None:
        self._gmail_api = gmail_api
        self._jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                [
                    TEMPLATESDIR,
                    pathlib.Path(__file__).parents[1] / "templates"
                ]
            )
        )

    def notify_success(
        self,
        mail_to: str,
        platform: platforms.AbstractPlatform,
        item_id: str, *,
        cropsiss_id: str = ""
    ) -> None:
        filename = "notify_success.html"
        subject = "【Cropsiss】出品取り消し"
        template = self._jinja_env.get_template(filename)
        body = template.render(
            user=mail_to,
            cropsiss_id=cropsiss_id,
            platform_name=platform.name,
            item_id=item_id,
            selling_page_url=platform.get_selling_page_url(item_id),
            developer=self.developer_form
        )
        self._gmail_api.send_email(mail_to, subject, body)

    def notify_fail(
        self,
        mail_to: str,
        platform: platforms.AbstractPlatform,
        item_id: str, *,
        cropsiss_id: str = ""
    ) -> None:
        filename = "notify_fail.html"
        subject = "【Cropsiss】出品取り消し(エラー)"
        template = self._jinja_env.get_template(filename)
        body = template.render(
            user=mail_to,
            cropsiss_id=cropsiss_id,
            platform_name=platform.name,
            item_id=item_id,
            selling_page_url=platform.get_selling_page_url(item_id),
            developer=self.developer_form
        )
        self._gmail_api.send_email(mail_to, subject, body)


class RootGroup(click.Group):

    def invoke(self, ctx: click.Context) -> t.Any:
        try:
            return super().invoke(ctx)
        except exceptions.ConfigFileNotFoundError:  # pragma: no cover
            exit("The config file not found. Run `cropsiss config init`.")
        except exceptions.ConfigInsufficientError as err:  # pragma: no cover
            exit(f"The required fields of config are not sufficient.\n{err}")
        except exceptions.GoogleCredentialsInvalidError:  # pragma: no cover
            exit("No credentials. Run `cropsiss login`.")


@click.group(
    name="cropsiss",
    cls=RootGroup,
    help="Enable to sell items simultaneously over platforms"
)
@click_log.simple_verbosity_option(logger)  # type: ignore
@click.version_option(__version__)
def main() -> None:
    APPDIR.mkdir(parents=True, exist_ok=True)
    LOGDIR.mkdir(exist_ok=True)
    init_logger(logger)


def init_logger(logger: logging.Logger) -> None:
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)8s - %(message)s"
    )
    error_file_handler = logging.handlers.RotatingFileHandler(
        LOGDIR / "err.log",
        mode="a",
        maxBytes=int(1e10),
        backupCount=3
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    debug_file_handler = logging.handlers.RotatingFileHandler(
        LOGDIR / "debug.log",
        mode="a",
        maxBytes=int(1e10),
        backupCount=10
    )
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(formatter)
    logger.addHandler(error_file_handler)
    logger.addHandler(debug_file_handler)
