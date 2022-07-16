# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
from unittest import TestCase, mock

import cropsiss
from cropsiss import google, platforms

from cropsiss.cli import root


class TestSystem_notify_success(TestCase):

    def setUp(self) -> None:
        self.filename = "notify_success.html"
        self.subject = "【Cropsiss】出品取り消し"
        self.gmail_api_mock = mock.Mock(spec_set=google.GmailAPI)
        self.system = root.System(self.gmail_api_mock)

    def _test(
        self,
        mail_to: str = "",
        platform: platforms.AbstractPlatform = cropsiss.PLATFORMS[0],
        item_id: str = "",
        cropsiss_id: str = ""
    ) -> None:
        self.gmail_api_mock.reset_mock()
        self.system.notify_success(
            mail_to=mail_to,
            platform=platform,
            item_id=item_id,
            cropsiss_id=cropsiss_id
        )
        body = self.system._jinja_env.get_template(self.filename).render(
            user=mail_to,
            cropsiss_id=cropsiss_id,
            platform_name=platform.name,
            item_id=item_id,
            selling_page_url=platform.get_selling_page_url(item_id),
            developer=self.system.developer_form
        )
        self.gmail_api_mock.send_email.assert_called_once_with(mail_to, self.subject, body)

    def test_mail_to(self) -> None:
        mail_to_list = [f"foo{i}@example.com" for i in range(3)]
        for mail_to in mail_to_list:
            with self.subTest(mail_to=mail_to):
                self._test(mail_to=mail_to)

    def test_platform(self) -> None:
        for platform in cropsiss.PLATFORMS:
            with self.subTest(platform_name=platform.name):
                self._test(platform=platform)

    def test_item_id(self) -> None:
        item_ids = [f"item_id{i}" for i in range(3)]
        for item_id in item_ids:
            with self.subTest(item_id=item_id):
                self._test(item_id=item_id)

    def test_cropsiss_id(self) -> None:
        cropsiss_ids = [f"cropsiss_id{i}" for i in range(3)]
        for cropsiss_id in cropsiss_ids:
            with self.subTest(cropsiss_id=cropsiss_id):
                self._test(cropsiss_id=cropsiss_id)


class TestSystem_notify_fail(TestCase):

    def setUp(self) -> None:
        self.filename = "notify_fail.html"
        self.subject = "【Cropsiss】出品取り消し(エラー)"
        self.gmail_api_mock = mock.Mock(spec_set=google.GmailAPI)
        self.system = root.System(self.gmail_api_mock)

    def _test(
        self,
        mail_to: str = "",
        platform: platforms.AbstractPlatform = cropsiss.PLATFORMS[0],
        item_id: str = "",
        cropsiss_id: str = ""
    ) -> None:
        self.gmail_api_mock.reset_mock()
        self.system.notify_fail(
            mail_to=mail_to,
            platform=platform,
            item_id=item_id,
            cropsiss_id=cropsiss_id
        )
        body = self.system._jinja_env.get_template(self.filename).render(
            user=mail_to,
            cropsiss_id=cropsiss_id,
            platform_name=platform.name,
            item_id=item_id,
            selling_page_url=platform.get_selling_page_url(item_id),
            developer=self.system.developer_form
        )
        self.gmail_api_mock.send_email.assert_called_once_with(mail_to, self.subject, body)

    def test_mail_to(self) -> None:
        mail_to_list = [f"foo{i}@example.com" for i in range(3)]
        for mail_to in mail_to_list:
            with self.subTest(mail_to=mail_to):
                self._test(mail_to=mail_to)

    def test_platform(self) -> None:
        for platform in cropsiss.PLATFORMS:
            with self.subTest(platform_name=platform.name):
                self._test(platform=platform)

    def test_item_id(self) -> None:
        item_ids = [f"item_id{i}" for i in range(3)]
        for item_id in item_ids:
            with self.subTest(item_id=item_id):
                self._test(item_id=item_id)

    def test_cropsiss_id(self) -> None:
        cropsiss_ids = [f"cropsiss_id{i}" for i in range(3)]
        for cropsiss_id in cropsiss_ids:
            with self.subTest(cropsiss_id=cropsiss_id):
                self._test(cropsiss_id=cropsiss_id)
