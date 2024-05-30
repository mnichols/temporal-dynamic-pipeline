from dataclasses import dataclass


@dataclass
class ValidateComponentRequest:
    id: str
    api_form: str
    input: {}


@dataclass
class ValidateComponentResponse:
    id: str
    api_form: str
    ok: bool
    message: str


@dataclass
class DeployComponentRequest:
    id: str
    api_form: str
    input: {}


@dataclass
class DeployComponentResponse:
    id: str
    api_form: str
    ok: bool
    message: str