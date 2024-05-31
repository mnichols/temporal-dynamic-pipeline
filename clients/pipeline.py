from dataclasses import dataclass
from typing import Optional, Any, Dict

from messaging.values import COMPONENT_STATUS_SUCCESS, COMPONENT_STATUS_NOT_FOUND, COMPONENT_STATUS_BUILDING


@dataclass
class ComponentConfig:
    api_form: str
    url: str


@dataclass
class Request:
    id: str
    body: Optional[Dict[str, Any]] = None


@dataclass
class Response:
    url: str
    status_code: int
    headers: Optional[Dict[str, Any]]=None
    body: Optional[Dict[str, Any]] = None


# This represents the HTTP Client used to interact with the infra API
# we can easily mock or stub this out to test it out
class PipelineClient:
    def __init__(self, cfg: ComponentConfig, component_progress: {}):
        self.component_progress = component_progress
        self.cfg = cfg

    async def validate(self, req: Request) -> Response:
        return Response(url=self.cfg.url, body=req.body, headers={'id': req.id}, status_code=200)

    async def deploy(self, req: Request) -> Response:
        self.component_progress[req.id] = {
            'deployed': req.body,
            'status_checks': 0,
        }
        print(f'placed the component {req.id} into {self.component_progress}')
        return Response(url=self.cfg.url, body=req.body, headers={'id': req.id}, status_code=202)

    async def status(self, req: Request) -> Response:
        print(f'checking component progress {req.id} from {self.component_progress}')
        if not self.component_progress.get(req.id):
            return Response(url=self.cfg.url, body={'error': COMPONENT_STATUS_NOT_FOUND},headers={'id': req.id}, status_code=404)

        if self.component_progress.get(req.id).get('status_checks') > 5:
            return Response(url=self.cfg.url, body={'status': COMPONENT_STATUS_SUCCESS}, headers={'id': req.id}, status_code=200)
        self.component_progress.get(req.id)['status_checks'] += 1
        return Response(url=self.cfg.url, body={'status': COMPONENT_STATUS_BUILDING}, headers={'id': req.id}, status_code=200)

    async def output(self, req: Request) -> Response:
        return Response(url=self.cfg.url, body=req.body, headers={'id': req.id}, status_code=200)
