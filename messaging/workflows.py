from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class Component:
    status: str  # not needed
    name: str
    order: int  # deprecated
    input: Dict[str, Any]
    output: Dict[str, Any]
    api_form: str  # key
    id: Optional[str] = ''


@dataclass
class DeployRequest:
    requester_name: str
    requester_mail: str
    ci: str  # what is this
    num_components: int
    components: List[Component]
    common_values: Dict[str, Any]


@dataclass
class ValidateDeploymentResponse:
    validation: Dict[str, Any]
    inputs: Dict[str, Any]
