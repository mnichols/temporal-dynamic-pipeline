from dataclasses import dataclass
from typing import Optional

from messaging.values import COMPONENT_STATUS_SUCCESS


@dataclass
class ComponentConfig:
    api_form: str
    url: str


@dataclass
class Request:
    id: str
    body: Optional[{}] = None


@dataclass
class Response:
    url: str
    status_code: int
    headers: Optional[{}]=None
    body: Optional[{}] = None


# This represents the HTTP Client used to interact with the infra API
# we can easily mock or stub this out to test it out
class PipelineClient:
    def __init__(self, cfg: ComponentConfig):
        self.cfg = cfg

    async def validate(self, req: Request) -> Response:
        return Response(url=self.cfg.url, body=req.body, headers={id: req.id}, status_code=200)

    async def deploy(self, req: Request) -> Response:
        return Response(url=self.cfg.url, body=req.body, headers={id: req.id}, status_code=202)

    async def status(self, req: Request) -> Response:
        body = {
            'status': COMPONENT_STATUS_SUCCESS,
        }
        return Response(url=self.cfg.url, body=body, headers={id: req.id}, status_code=200)

    async def output(self, req: Request) -> Response:
        return Response(url=self.cfg.url, body=req.body, headers={id: req.id}, status_code=200)
