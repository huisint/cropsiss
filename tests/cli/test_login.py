# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
from unittest import TestCase, mock

import click
from click import testing

from cropsiss import exceptions
from cropsiss.cli import root, login, config


RUNNER = testing.CliRunner()
CONFIG = config.Config(client_id="clientId", client_secret="clientSecret")
LOAD_CONFIG_PATCHER = mock.patch("cropsiss.cli.config.Config.load", return_value=CONFIG)


def setUpModule() -> None:
    LOAD_CONFIG_PATCHER.start()


def tearDownModule() -> None:
    LOAD_CONFIG_PATCHER.stop()


@mock.patch("cropsiss.google.credentials.Credentials.from_file")
class Test_credentials_callback(TestCase):

    def setUp(self) -> None:
        self.filename = "credentials.json"

    def test(self, from_file_mock: mock.Mock) -> None:
        self.assertEqual(
            login.credentials_callback(
                mock.Mock(spec_set=click.Context),
                mock.Mock(spec_set=click.Option),
                self.filename
            ),
            from_file_mock.return_value
        )
        from_file_mock.assert_called_once_with(self.filename)

    def test_value_error(self, from_file_mock: mock.Mock) -> None:
        from_file_mock.side_effect = ValueError()
        with self.assertRaises(exceptions.GoogleCredentialsInvalidError):
            login.credentials_callback(
                mock.Mock(spec_set=click.Context),
                mock.Mock(spec_set=click.Option),
                self.filename
            )
        from_file_mock.assert_called_once_with(self.filename)

    def test_file_not_found_error(self, from_file_mock: mock.Mock) -> None:
        from_file_mock.side_effect = FileNotFoundError()
        with self.assertRaises(exceptions.GoogleCredentialsInvalidError):
            login.credentials_callback(
                mock.Mock(spec_set=click.Context),
                mock.Mock(spec_set=click.Option),
                self.filename
            )
        from_file_mock.assert_called_once_with(self.filename)


@mock.patch("cropsiss.google.credentials.Credentials.new")
@mock.patch("cropsiss.google.credentials.Credentials.from_file")
class Test_login(TestCase):

    def test_credentials_file_exists(
        self,
        from_file_mock: mock.Mock,
        new_mock: mock.Mock,
    ) -> None:
        result = RUNNER.invoke(root.main, [str(login.login.name)], catch_exceptions=False)
        self.assertEqual(result.output, "Login succeeded\n")
        self.assertEqual(result.exit_code, 0)
        from_file_mock.assert_called_once_with(login.CREDENTIALS_FILE)
        new_mock.assert_not_called()

    def test_credentials_file_does_not_exist(
        self,
        from_file_mock: mock.Mock,
        new_mock: mock.Mock
    ) -> None:
        from_file_mock.side_effect = FileNotFoundError()
        result = RUNNER.invoke(root.main, [str(login.login.name)], catch_exceptions=False)
        self.assertEqual(result.output, "Login succeeded\n")
        self.assertEqual(result.exit_code, 0)
        from_file_mock.assert_called_once_with(login.CREDENTIALS_FILE)
        new_mock.assert_called_once_with(
            client_id=CONFIG.client_id,
            client_secret=CONFIG.client_secret,
            run_local_server=True
        )

    def test_credentials_file_is_invalid(
        self,
        from_file_mock: mock.Mock,
        new_mock: mock.Mock
    ) -> None:
        from_file_mock.side_effect = ValueError()
        result = RUNNER.invoke(root.main, [str(login.login.name)], catch_exceptions=False)
        self.assertEqual(result.output, "Login succeeded\n")
        self.assertEqual(result.exit_code, 0)
        from_file_mock.assert_called_once_with(login.CREDENTIALS_FILE)
        new_mock.assert_called_once_with(
            client_id=CONFIG.client_id,
            client_secret=CONFIG.client_secret,
            run_local_server=True
        )

    def test_no_local_server(
        self,
        from_file_mock: mock.Mock,
        new_mock: mock.Mock
    ) -> None:
        from_file_mock.side_effect = ValueError()
        result = RUNNER.invoke(root.main, [str(login.login.name), "--no-local-server"], catch_exceptions=False)
        self.assertEqual(result.output, "Login succeeded\n")
        self.assertEqual(result.exit_code, 0)
        from_file_mock.assert_called_once_with(login.CREDENTIALS_FILE)
        new_mock.assert_called_once_with(
            client_id=CONFIG.client_id,
            client_secret=CONFIG.client_secret,
            run_local_server=False
        )


@mock.patch("os.unlink")
class Test_logout(TestCase):

    @mock.patch("os.path.exists", return_value=True)
    def test_credentials_file_exista(
        self,
        exists_mock: mock.Mock,
        unlink_mock: mock.Mock
    ) -> None:
        result = RUNNER.invoke(root.main, [str(login.logout.name)], catch_exceptions=False)
        self.assertEqual(result.output, "Logout succeeded\n")
        self.assertEqual(result.exit_code, 0)
        exists_mock.assert_called_with(login.CREDENTIALS_FILE)
        unlink_mock.assert_called_once_with(login.CREDENTIALS_FILE)

    @mock.patch("os.path.exists", return_value=False)
    def test_credentials_file_does_not_exist(
        self,
        exists_mock: mock.Mock,
        unlink_mock: mock.Mock
    ) -> None:
        result = RUNNER.invoke(root.main, [str(login.logout.name)], catch_exceptions=False)
        self.assertEqual(result.output, "Logout succeeded\n")
        self.assertEqual(result.exit_code, 0)
        exists_mock.assert_called_with(login.CREDENTIALS_FILE)
        unlink_mock.assert_not_called()
