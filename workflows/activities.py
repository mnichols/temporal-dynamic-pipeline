import random

from temporalio import activity
from temporalio.exceptions import ApplicationError

from clients.lookup import get_pipeline_client
from clients.pipeline import Request
from messaging.commands import ValidateComponentRequest, ValidateComponentResponse, DeployComponentRequest, \
    DeployComponentResponse
from messaging.queries import GetComponentStatusRequest, \
    GetComponentStatusResponse, GetComponentOutputRequest, GetComponentOutputResponse
from messaging.values import COMPONENT_STATUS_NOT_FOUND, COMPONENT_STATUS_BUILDING

ERR_GENERAL = 'GENERAL'


#_________________________________________________________________________________________________________________________
class PipelineActions:
    #_________________________________________________________________________________________________________________________
    def __init__(self):
        pass

    @activity.defn
    async def get_id(self, api_form: str) -> str:
        val = random.randint(1000, 9999)
        return '{}-{}'.format(api_form, val)

    @activity.defn
    async def validate(self, req: ValidateComponentRequest) -> ValidateComponentResponse:
        client = get_pipeline_client(req.api_form)
        res = await client.validate(Request(
            id=req.id,
            body=req.input,
        ))
        return ValidateComponentResponse(
            id=req.id,
            api_form=req.api_form,
            ok=res.body.ok,
            message=res.body.message,
        )

    @activity.defn
    async def get_status(self, req: GetComponentStatusRequest) -> GetComponentStatusResponse:
        client = get_pipeline_client(req.api_form)
        res = await client.status(Request(
            id=req.id,

        ))

        if res.status_code == 200:
            # underlying service supports: BUILDING, SUCCESS, ERROR
            if res.body.status == COMPONENT_STATUS_BUILDING:
                raise ApplicationError(
                    non_retryable=True,
                    type=COMPONENT_STATUS_BUILDING,
                    message=COMPONENT_STATUS_BUILDING,
                )
            return GetComponentStatusResponse(
                api_form=req.api_form,
                id=req.id,
                status=res.body.status
            )
        if res.status_code == 404:
            raise ApplicationError(
                non_retryable=False,
                type=COMPONENT_STATUS_NOT_FOUND,
                message=COMPONENT_STATUS_NOT_FOUND,
            )

        raise ApplicationError(
            non_retryable=True,
            type=ERR_GENERAL,
            message=res.body.error,  # assume we have some error spec we
        )

    @activity.defn
    async def deploy(self, req: DeployComponentRequest) -> DeployComponentResponse:
        client = get_pipeline_client(req.api_form)
        res = await client.deploy(Request(
            id=req.id,
            body=req.input,
        ))
        return DeployComponentResponse(
            id=req.id,
            api_form=req.api_form,
            ok=res.status_code < 299,
            message='deployed'
        )

    @activity.defn
    async def get_output(self, req: GetComponentOutputRequest) -> GetComponentOutputResponse:
        client = get_pipeline_client(req.api_form)
        res = await client.output(Request(
            id=req.id,
        ))
        return GetComponentOutputResponse(
            id=req.id,
            api_form=req.api_form,
            output=res.body,
        )
