from dataclasses import dataclass

@dataclass
class GetComponentStatusRequest:
    id: str
    api_form: str


@dataclass
class GetComponentStatusResponse:
    id: str
    api_form: str
    status: str


@dataclass
class GetComponentOutputRequest:
    id: str
    api_form: str


@dataclass
class GetComponentOutputResponse:
    id: str
    api_form: str
    output: {}
