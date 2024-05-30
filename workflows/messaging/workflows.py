from dataclasses import dataclass
from typing import Optional


@dataclass
class Component:
    status: str  # not needed
    name: str
    order: int  # deprecated
    input: {}
    output: {}
    api_form: str  # key
    id: Optional[str] = ''


@dataclass
class DeployRequest:
    requester_name: str
    requester_mail: str
    ci: str  # what is this
    num_components: int
    components: [Component]
    common_values: {}


@dataclass
class ValidateDeploymentResponse:
    validation: {}
    inputs: {}
