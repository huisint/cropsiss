# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
import base64
from email.mime import text
import dataclasses
import typing as t

from cropsiss.google import abstract


@dataclasses.dataclass()
class GmailAPI(abstract.AbstractAPI):
    user_id: str = "me"
    """The user's email address."""

    def __post_init__(self) -> None:
        super().__init__(self.credentials, self.version or "v1")

    @property
    def service_name(self) -> str:
        return "gmail"

    @property
    def _service(self) -> t.Any:
        return abstract.build_service(self)

    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str
    ) -> None:
        """Send an e-mail via Gmail.

        Parameters
        ----------
        recipient : str
            Email address of the recipient.
        subject : str
            Subject of the mail.
        body : str
            Body of the mail.

        See Also
        --------
        https://developers.google.com/gmail/api/reference/rest/v1/users.messages/send
        """
        message = text.MIMEText(str(body), "html")
        message["to"] = str(recipient)
        message["subject"] = str(subject)
        raw_body = base64.urlsafe_b64encode(message.as_bytes()).decode()
        self._service.users().messages().send(
            userId="me",
            body={"raw": raw_body}
        ).execute()

    def search_mail(self, query: str = "", max_result: int = 100) -> list[str]:
        """Get Gmail IDs in the mailbox.

        Parameters
        ----------
        query : str
            The same query as the Gmail search box.
        max_result : int
            Maximum number of messages to return.

        Returns
        -------
        list[str]
            List of mail IDs.

        See Also
        --------
        https://developers.google.com/gmail/api/reference/rest/v1/users.messages/list
        """
        messages: list[t.Any] = self._service.users().messages().list(
            userId=self.user_id,
            q=str(query),
            maxResults=max_result
        ).execute().get("messages", [])
        return [message["id"] for message in messages]

    def get_mail(self, mail_id: str) -> dict[str, t.Any]:
        """Get the specified Gmail message.

        Parameters
        ----------
        credentils : google.oauth2.credentials.Credentials
            Credentials for Gmail API.
        mail_id : str
            Gmail ID.

        Returns
        -------
        dict[str, Any]
            Gmail object.

        See Also
        --------
        https://developers.google.com/gmail/api/reference/rest/v1/users.messages/get.
        """
        gmail = self._service.users().messages().get(userId="me", id=mail_id).execute()
        return {str(key): gmail[key] for key in gmail}

    def get_labels(self) -> list[dict[str, t.Any]]:
        """Get a list of all labels in the user's mailbox.

        Returns
        -------
        lits[dict[str, Any]]
            List of Label object.

        See Also
        --------
        https://developers.google.com/gmail/api/reference/rest/v1/users.labels/list
        """
        labels = self._service.users().labels().list(
            userId=self.user_id
        ).execute().get("labels")
        return [{str(key): label[key] for key in label} for label in labels]

    def create_label(self, label_name: str) -> dict[str, t.Any]:
        """Creates a new label.

        Parameters
        ----------
        label_name : str
            The display name of the label.

        Returns
        -------
        dict[str, Any]
            The created Label object.

        See Also
        --------
        https://developers.google.com/gmail/api/reference/rest/v1/users.labels/create
        """
        body = {
            "name": label_name
        }
        label = self._service.users().labels().create(
            userId=self.user_id,
            body=body
        ).execute()
        return {str(key): label[key] for key in label}

    def add_labels(self, mail_id: str, label_ids: list[str]) -> None:
        """Add the labels on the specified message.

        Parameters
        ----------
        mail_id : str
            The ID of the message to modify.
        label_ids : list[str]
            A list of IDs of labels to add to this message.

        See Also
        --------
        https://developers.google.com/gmail/api/reference/rest/v1/users.messages/modify
        """
        body = {
            "addLabelIds": label_ids
        }
        self._service.users().messages().modify(
            userId=self.user_id,
            id=mail_id,
            body=body
        ).execute()

    def remove_labels(self, mail_id: str, label_ids: list[str]) -> None:
        """Remove the labels on the specified message.

        Parameters
        ----------
        mail_id : str
            The ID of the message to modify.
        label_ids : list[str]
            A list of IDs of labels to add to this message.

        See Also
        --------
        https://developers.google.com/gmail/api/reference/rest/v1/users.messages/modify
        """
        body = {
            "removeLabelIds": label_ids
        }
        self._service.users().messages().modify(
            userId=self.user_id,
            id=mail_id,
            body=body
        ).execute()

    def __hash__(self) -> int:
        return hash((self.version, self.user_id))
