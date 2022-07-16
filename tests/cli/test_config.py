# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
from unittest import TestCase, mock
import os
import pathlib

from click import testing

from cropsiss import exceptions
from cropsiss.cli import config, root


CONFIG_FILE = pathlib.Path("tests/config.json")

RUNNER = testing.CliRunner()


def tearDownModule() -> None:
    CONFIG_FILE.unlink(missing_ok=True)


class TestConfig_load(TestCase):

    def setUp(self) -> None:
        self.cfg = config.Config(
            spreadsheet_id="spreadsheetId",
            client_id="clientid",
            client_secret="cilentsecret"
        )
        self.cfg.save(CONFIG_FILE)

    def tearDown(self) -> None:
        if os.path.exists(CONFIG_FILE):
            os.unlink(CONFIG_FILE)

    def test_config_file_exists(self) -> None:
        cfg = config.Config.load(CONFIG_FILE)
        for field in cfg.__dataclass_fields__:
            with self.subTest(field=field):
                self.assertEqual(cfg.__getattribute__(field), self.cfg.__getattribute__(field))

    def test_config_file_does_not_exist(self) -> None:
        unexist_path = pathlib.Path("unexist.json")
        self.assertFalse(unexist_path.exists())
        with self.assertRaises(exceptions.ConfigFileNotFoundError):
            config.Config.load(unexist_path)

    def test_check_required_True(self) -> None:
        cfg = config.Config.load(CONFIG_FILE, check_required=True)
        for field in self.cfg.required_fields:
            cfg.__setattr__(field, "")
            cfg.save(CONFIG_FILE)
            with self.subTest(field=field):
                with self.assertRaises(exceptions.ConfigInsufficientError):
                    config.Config.load(CONFIG_FILE, check_required=True)

    def test_check_required_False(self) -> None:
        cfg = config.Config.load(CONFIG_FILE, check_required=True)
        for field in self.cfg.required_fields:
            cfg.__setattr__(field, "")
            cfg.save(CONFIG_FILE)
            with self.subTest(field=field):
                try:
                    config.Config.load(CONFIG_FILE, check_required=False)
                except exceptions.ConfigInsufficientError:
                    self.fail("ConfigInsufficientError is raised")


class Test_create_new_config(TestCase):

    def setUp(self) -> None:
        self.cfg = config.Config(
            spreadsheet_id="spreadsheetId",
        )
        self.saved_message = "Created a new config file"

    def tearDown(self) -> None:
        with open(CONFIG_FILE) as f:
            cfg = config.Config.from_json(f.read())
        self.assertEqual(cfg, self.cfg)

    def test_minimum_options(self) -> None:
        result = RUNNER.invoke(
            root.main,
            [
                str(config.main.name),
                str(config.create_new_config.name),
                "--spreadsheet-id",
                self.cfg.spreadsheet_id,
                "--config-file",
                str(CONFIG_FILE)
            ],
            catch_exceptions=False
        )
        self.assertEqual(
            result.output,
            "Client ID(optional) []: \n"
            + "Client Secret(optional) []: \n"
            + f"{self.saved_message}\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_option_client_id(self) -> None:
        self.cfg.client_id = "clientId"
        result = RUNNER.invoke(
            root.main,
            [
                str(config.main.name),
                str(config.create_new_config.name),
                "--spreadsheet-id",
                self.cfg.spreadsheet_id,
                "--client-id",
                self.cfg.client_id,
                "--config-file",
                str(CONFIG_FILE),
            ],
            catch_exceptions=False
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            "Client Secret(optional) []: \n"
            + f"{self.saved_message}\n",
        )

    def test_option_client_secret(self) -> None:
        self.cfg.client_secret = "clientSecret"
        result = RUNNER.invoke(
            root.main,
            [
                str(config.main.name),
                str(config.create_new_config.name),
                "--spreadsheet-id",
                self.cfg.spreadsheet_id,
                "--client-secret",
                self.cfg.client_secret,
                "--config-file",
                str(CONFIG_FILE)
            ],
            catch_exceptions=False
        )
        self.assertEqual(
            result.output,
            "Client ID(optional) []: \n"
            + f"{self.saved_message}\n",
        )
        self.assertEqual(result.exit_code, 0)


class Test_show_config(TestCase):

    def setUp(self) -> None:
        self.cfg = config.Config(
            spreadsheet_id="spreadsheetId",
            client_id="clientid",
            client_secret="cilentsecret",
        )

    def test(self) -> None:
        with mock.patch("cropsiss.cli.config.Config.load", return_value=self.cfg) as m:
            result = RUNNER.invoke(
                root.main,
                [str(config.main.name), str(config.show_config.name)],
                catch_exceptions=False
            )
        self.assertEqual(result.output, "".join(f"{key}={val}\n" for key, val in self.cfg.__dict__.items()))
        self.assertEqual(result.exit_code, 0)
        m.assert_called_once_with(str(config.CONFIG_FILE), check_required=False)

    def test_json(self) -> None:
        with mock.patch("cropsiss.cli.config.Config.load", return_value=self.cfg) as m:
            result = RUNNER.invoke(root.main, [str(config.main.name), str(config.show_config.name), "--json"])
        self.assertEqual(result.output, self.cfg.to_json(indent=2) + "\n")
        self.assertEqual(result.exit_code, 0)
        m.assert_called_once_with(str(config.CONFIG_FILE), check_required=False)


class Test_update_config(TestCase):

    def setUp(self) -> None:
        self.cfg = config.Config(
            spreadsheet_id="spreadsheetId",
        )
        self.cfg.save(CONFIG_FILE)

    def test_field(self) -> None:
        updated_value = "updated"
        for field in self.cfg.__dataclass_fields__:
            self.setUp()
            with self.subTest(field=field):
                result = RUNNER.invoke(
                    root.main,
                    [
                        str(config.main.name),
                        str(config.update_config.name),
                        "--field", field,
                        "--value", updated_value,
                        "--config-file",
                        str(CONFIG_FILE)
                    ],
                    catch_exceptions=False
                )
                self.assertEqual(result.output, "")
                self.assertEqual(result.exit_code, 0)
                with open(CONFIG_FILE) as f:
                    cfg = config.Config.from_json(f.read())
                self.cfg.__setattr__(field, updated_value)
                self.assertEqual(cfg, self.cfg)
