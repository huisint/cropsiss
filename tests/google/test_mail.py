# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
from unittest import TestCase, mock
from email.mime import text
import base64

from cropsiss.google import mail, credentials


CREDENTIALS_MOCK = mock.Mock(spec_set=credentials.Credentials)


class TestGmailAPI_properties(TestCase):

    def setUp(self) -> None:
        self.api = mail.GmailAPI(CREDENTIALS_MOCK)

    def test_service_name(self) -> None:
        self.assertEqual(self.api.service_name, "gmail")

    def test__service(self) -> None:
        with mock.patch("cropsiss.google.abstract.build_service") as build_mock:
            self.assertEqual(
                self.api._service,
                build_mock.return_value
            )
            build_mock.assert_called_once_with(self.api)


class TestGmailAPI_send_email(TestCase):

    def setUp(self) -> None:
        self.api = mail.GmailAPI(CREDENTIALS_MOCK)

    def _test(
        self,
        recipient: str = "",
        subject: str = "",
        body: str = ""
    ) -> None:
        with mock.patch("cropsiss.google.mail.GmailAPI._service") as service_mock:
            self.api.send_email(recipient, subject, body)
        message = text.MIMEText(str(body), "html")
        message["to"] = str(recipient)
        message["subject"] = str(subject)
        raw_body = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service_mock \
            .users.return_value \
            .messages.return_value \
            .send.assert_called_once_with(
                userId="me",
                body={"raw": raw_body}
            )

    def test_recipient(self) -> None:
        recipients = [f"foo{i}@example.com" for i in range(3)]
        for recipient in recipients:
            with self.subTest(recipient=recipient):
                self._test(recipient=recipient)

    def test_subject(self) -> None:
        subjects = [f"test mail {i}" for i in range(3)]
        for subject in subjects:
            with self.subTest(subject=subject):
                self._test(subject=subject)

    def test_body(self) -> None:
        bodies = [f"This is a test mail {i}" for i in range(3)]
        for body in bodies:
            with self.subTest(body=body):
                self._test(body=body)


class TestGmailAPI_search_mail(TestCase):

    def setUp(self) -> None:
        self.api = mail.GmailAPI(CREDENTIALS_MOCK)

    def _test(
        self,
        query: str = "",
        max_results: int = 100
    ) -> None:
        messages = [{"id": f"mailId{i}"} for i in range(max_results)]
        with mock.patch("cropsiss.google.mail.GmailAPI._service") as service_mock:
            service_mock \
                .users.return_value \
                .messages.return_value \
                .list.return_value \
                .execute.return_value = {
                    "messages": messages
                }
            self.assertListEqual(
                self.api.search_mail(query, max_results),
                [msg["id"] for msg in messages]
            )
        service_mock \
            .users.return_value \
            .messages.return_value \
            .list.assert_called_once_with(
                userId="me",
                q=query,
                maxResults=max_results
            )

    def test_query(self) -> None:
        queries = [f"from:foo{i}@example.com" for i in range(3)]
        for query in queries:
            with self.subTest(query=query):
                self._test(query=query)

    def test_max_result(self) -> None:
        max_resultses = [100 * i for i in range(1, 6)]
        for max_results in max_resultses:
            with self.subTest(max_result=max_results):
                self._test(max_results=max_results)


class TestGmailAPI_get_mail(TestCase):

    def setUp(self) -> None:
        self.api = mail.GmailAPI(CREDENTIALS_MOCK)

    def _test(self, mail_id: str = "") -> None:
        gmail = {"id": mail_id, "threadId": "threadId", "payload": {}}
        with mock.patch("cropsiss.google.mail.GmailAPI._service") as service_mock:
            service_mock \
                .users.return_value \
                .messages.return_value \
                .get.return_value \
                .execute.return_value = gmail
            self.assertDictEqual(self.api.get_mail(mail_id), gmail)
        service_mock \
            .users.return_value \
            .messages.return_value \
            .get.assert_called_once_with(
                userId="me",
                id=mail_id,
            )

    def test_mail_id(self) -> None:
        mail_ids = [f"mailId{i}" for i in range(3)]
        for mail_id in mail_ids:
            with self.subTest(mail_id=mail_id):
                self._test(mail_id)


class TestGmailAPI_get_labels(TestCase):
    api: mail.GmailAPI

    def setUp(self) -> None:
        self.api = mail.GmailAPI(CREDENTIALS_MOCK)

    def test(self) -> None:
        labels = [{"id": f"Label_{i}", "name": "label{i}"} for i in range(3)]
        with mock.patch("cropsiss.google.mail.GmailAPI._service") as service_mock:
            service_mock \
                .users.return_value \
                .labels.return_value \
                .list.return_value \
                .execute.return_value = {
                    "labels": labels
                }
            self.assertListEqual(self.api.get_labels(), labels)
        service_mock \
            .users.return_value \
            .labels.return_value \
            .list.assert_called_once_with(
                userId="me"
            )


class TestGmailAPI_create_label(TestCase):

    def setUp(self) -> None:
        self.api = mail.GmailAPI(CREDENTIALS_MOCK)

    def _test(self, label_name: str = "") -> None:
        label = {"id": "Label_1", "name": label_name}
        with mock.patch("cropsiss.google.mail.GmailAPI._service") as service_mock:
            service_mock \
                .users.return_value \
                .labels.return_value \
                .create.return_value \
                .execute.return_value = label
            self.assertDictEqual(self.api.create_label(label_name), label)
        service_mock \
            .users.return_value \
            .labels.return_value \
            .create.assert_called_once_with(
                userId="me",
                body={"name": label_name}
            )

    def test_label_name(self) -> None:
        label_names = [f"label{i}" for i in range(3)]
        for label_name in label_names:
            with self.subTest(label_name=label_name):
                self._test(label_name=label_name)


class TestGmailAPI_add_labels(TestCase):
    api: mail.GmailAPI

    def setUp(self) -> None:
        self.api = mail.GmailAPI(CREDENTIALS_MOCK)

    def _test(
        self,
        mail_id: str = "",
        label_ids: list[str] = []
    ) -> None:
        with mock.patch("cropsiss.google.mail.GmailAPI._service") as service_mock:
            self.api.add_labels(mail_id, label_ids)
        service_mock \
            .users.return_value \
            .messages.return_value \
            .modify.assert_called_once_with(
                userId="me",
                id=mail_id,
                body={"addLabelIds": label_ids}
            )

    def test_mail_id(self) -> None:
        mail_ids = [f"mailId{i}" for i in range(3)]
        for mail_id in mail_ids:
            with self.subTest(mail_id=mail_id):
                self._test(mail_id=mail_id)

    def test_label_ids(self) -> None:
        label_idses = [[f"Label_{i+j}" for i in range(3)] for j in range(3)]
        for label_ids in label_idses:
            with self.subTest(label_ids=label_ids):
                self._test(label_ids=label_ids)


class TestGmailAPI_remove_labels(TestCase):

    def setUp(self) -> None:
        self.api = mail.GmailAPI(CREDENTIALS_MOCK)

    def _test(
        self, mail_id: str = "",
        label_ids: list[str] = []
    ) -> None:
        with mock.patch("cropsiss.google.mail.GmailAPI._service") as service_mock:
            self.api.remove_labels(mail_id, label_ids)
        service_mock \
            .users.return_value \
            .messages.return_value \
            .modify.assert_called_once_with(
                userId="me",
                id=mail_id,
                body={"removeLabelIds": label_ids}
            )

    def test_mail_id(self) -> None:
        mail_ids = [f"mailId{i}" for i in range(3)]
        for mail_id in mail_ids:
            with self.subTest(mail_id=mail_id):
                self._test(mail_id=mail_id)

    def test_label_ids(self) -> None:
        label_idses = [[f"Label_{i+j}" for i in range(3)] for j in range(3)]
        for label_ids in label_idses:
            with self.subTest(label_ids=label_ids):
                self._test(label_ids=label_ids)
