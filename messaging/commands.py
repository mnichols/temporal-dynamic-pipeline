from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ValidateComponentRequest:
    id: str
    api_form: str
    input: Dict[str, Any]


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
    input: Dict[str, Any]


@dataclass
class DeployComponentResponse:
    id: str
    api_form: str
    ok: bool
    message: str
