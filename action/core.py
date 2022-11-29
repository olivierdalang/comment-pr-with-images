from abc import ABC, abstractmethod
from os import environ
from sys import exit
from typing import Any

from helpers import print_message
from requests import Response, Session


class Validator(ABC):
    def __set_name__(self, _, name):
        self.private_name = "_" + name

    def __get__(self, obj, *args, **kwargs):
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, self.private_name, value)

    @property
    def pretty_name(self) -> str:
        return f"'{self.private_name[1:]}'"

    @abstractmethod
    def validate(self, value):
        raise NotImplementedError

    @staticmethod
    def compose(*validators):
        def inner(*args, **kwargs):
            for f in validators:
                f(*args, **kwargs)

        return inner


class NoEmpty(Validator):
    def validate(self, value):
        if len(value) == 0 or (isinstance(value, str) and not value.strip()):
            raise ValueError(
                f"{self.pretty_name} found empty, while only non-empty lists or strings are valid."
            )


class ProperBool(Validator):
    def validate(self, value):
        if isinstance(value, bool):
            return

        if not isinstance(value, str):
            raise ValueError(f"{self.pretty_name} must be string or bool!")

        if not value.lower() in ["true", "false"]:
            raise ValueError(
                f"'{self.private_name[1:]}' must be either 'false' or 'true'."
            )


class ImgurConfig:
    upload_imgur = NoEmpty()

    def __init__(self, upload_imgur: str):
        self.upload_imgur = upload_imgur


class GhConfig:
    ref = NoEmpty()
    repo = NoEmpty()
    event_name = NoEmpty()
    run_id = NoEmpty()
    sha = NoEmpty()
    upload_to_branch = NoEmpty()
    pr_event = NoEmpty()
    supported_events = NoEmpty()

    def __init__(
        self,
        *,
        ref: str,
        repo: str,
        event_name: str,
        run_id: str,
        sha: str,
        pr_event: str,
        supported_events: list[str],
        upload_to_branch: str | None = None,
    ):
        self.ref = ref
        self.repo = repo
        self.event_name = event_name
        self.run_id = run_id
        self.sha = sha
        self.pr_event = pr_event
        self.supported_events = supported_events

        if upload_to_branch:
            self.upload_to_branch = upload_to_branch


class Config:
    images = NoEmpty()
    custom_attachment_msg = NoEmpty()
    edit_previous_comment = ProperBool()

    def __init__(self):
        self.images = [
            s.lstrip().rstrip() for s in environ["INPUT_IMAGES"].strip().split(",")
        ]
        self.custom_attachment_msg = environ.get(
            "INPUT_CUSTOM_ATTACHMENT_MSG", "Captures from the latest commit"
        )
        self.edit_previous_comment = environ.get("INPUT_EDIT_PREVIOUS_COMMENT", True)
        gh_required = {
            "ref": environ["GITHUB_REF"].split("/")[-1],
            "repo": environ["GITHUB_REPOSITORY"],
            "event_name": environ["GITHUB_EVENT_NAME"],
            "run_id": environ["GITHUB_RUN_ID"],
            "sha": environ["GITHUB_SHA"],
            "pr_event": "pull_request",
            "supported_events": ["pull_request"],
        }

        # If the workflow was not triggered by a pull request
        # exit the script with code 1.
        if gh_required["event_name"] not in gh_required["supported_events"]:
            print_message(
                f"This action only works for {gh_required['supported_events']} event(s)",
                message_type="error",
            )
            exit(1)

        self.upload_to = environ.get("INPUT_UPLOAD_TO", "github_branch")

        if self.upload_to == "imgur":
            self.imgur_config = ImgurConfig(self.upload_to)
            self.gh_config = GhConfig(**gh_required)
        else:
            gh_merged = {**gh_required, **{"upload_to_branch": self.upload_to}}
            self.gh_config = GhConfig(**gh_merged)


class Req:
    client = Session()
    gh_api_url = "https://api.github.com"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "authorization": f"Bearer { environ['INPUT_GITHUB_TOKEN']}",
    }

    @staticmethod
    def get(url: str) -> Response:
        return Req.client.get(url, headers=Req.headers)

    @staticmethod
    def post(url: str, data: str | dict[str, Any], **kwargs) -> Response:
        return Req.client.post(url, headers=Req.headers, json={"body": data}, **kwargs)

    @staticmethod
    def patch(url: str, data: str | dict[str, Any], **kwargs) -> Response:
        return Req.client.patch(url, headers=Req.headers, json={"body": data}, **kwargs)
