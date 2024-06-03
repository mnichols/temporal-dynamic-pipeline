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
from clients.lookup import COMPONENT_PROGRESS

ERR_GENERAL = 'GENERAL'


class PipelineActions:
    def __init__(self) -> None:
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

        ok = False if not res.body else res.body.get('ok')
        message = '' if not res.body else res.body.get('message')
        return ValidateComponentResponse(
            id=req.id,
            api_form=req.api_form,
            ok=bool(ok),
            message=str(message),
        )

    @activity.defn
    async def get_status(self, req: GetComponentStatusRequest) -> GetComponentStatusResponse:
        client = get_pipeline_client(req.api_form)
        res = await client.status(Request(
            id=req.id,
        ))

        print(f'got back {req.id} with status {res.status_code} from status call {res.body}')
        res.body = {} if not res.body else res.body

        if res.status_code == 200:
            # underlying service supports: BUILDING, SUCCESS, ERROR
            if res.body.get('status') == COMPONENT_STATUS_BUILDING:
                raise ApplicationError(
                    non_retryable=False,
                    type=COMPONENT_STATUS_BUILDING,
                    message=COMPONENT_STATUS_BUILDING,
                )
            return GetComponentStatusResponse(
                api_form=req.api_form,
                id=req.id,
                status=str(res.body.get('status'))
            )
        if res.status_code == 404:
            raise ApplicationError(
                non_retryable=True,
                type=COMPONENT_STATUS_NOT_FOUND,
                message=COMPONENT_STATUS_NOT_FOUND,
            )

        raise ApplicationError(
            non_retryable=True,
            type=ERR_GENERAL,
            message=str(res.body.get('error')),  # assume we have some error spec we
        )

    @activity.defn
    async def deploy(self, req: DeployComponentRequest) -> DeployComponentResponse:
        client = get_pipeline_client(req.api_form)
        res = await client.get_transforms(Request(
            id = req.id,
        ))
        transforms = {} if not res.body else res.body

        # this could just as easily be a local activity that produces
        # values that we pass into this activity.
        # however if I want to change these mappings from the environment
        # the history would still use the old copies
        for src_api_form,outputs in req.component_outputs.items():
            # get the mapping scoped to this component api_form
            scoped = transforms.get(src_api_form, {})
            for k, output_value in outputs.items():
                # here we swap the key configured for the transform
                key = scoped.get(k, k)
                req.input[key] = output_value

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
            output=res.body or {},
        )

    # this activity is for debug purposes only to get
    # access to the current component progress.
    # see the `deployed` key for actual parameters used to deploy each component
    @activity.defn
    async def get_component_progress(self) -> {}:
        return COMPONENT_PROGRESS