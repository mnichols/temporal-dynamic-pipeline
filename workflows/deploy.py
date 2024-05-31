
from dataclasses import dataclass
from datetime import timedelta
from typing import Dict, Any, List

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError

from messaging.commands import ValidateComponentRequest, DeployComponentRequest
from messaging.queries import GetComponentStatusRequest, GetComponentOutputRequest
from messaging.values import COMPONENT_STATUS_SUCCESS, COMPONENT_STATUS_NOT_FOUND, \
    COMPONENT_STATUS_ERROR, COMPONENT_STATUS_UNKNOWN
from messaging.workflows import DeployRequest, ValidateDeploymentResponse
from workflows.activities import PipelineActions, Foo


# with workflow.unsafe.imports_passed_through():
#     from activities import PipelineActions


@dataclass
class ComponentState:
    api_form: str
    status: str
    id: str
    output: Dict[str, Any]
    input: Dict[str, Any]


@dataclass
class DeployState:
    components: List[ComponentState]


@workflow.defn
class ValidateDeployment:
    @workflow.run
    async def run(self, params: DeployRequest) -> ValidateDeploymentResponse:
        state = ValidateDeploymentResponse(
            validation={},
            inputs={},
        )

        # ensure component ids first
        for idx, component in enumerate(params.components):
            # poor man's component id generator
            if not component.id:
                component.id = await workflow.execute_local_activity_method(
                    PipelineActions.get_id,
                    component.api_form,
                    start_to_close_timeout=timedelta(seconds=10),
                )

        for component in params.components:
            state.inputs[component.api_form] = component.input
            #  TODO accumulate validation results
            out = await workflow.execute_activity_method(
                PipelineActions.validate,
                ValidateComponentRequest(
                    id=component.id or '',
                    api_form=component.api_form,
                    input=component.input,
                ),
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(maximum_attempts=10),
            )
            state.validation[component.api_form] = out
        return state


@workflow.defn
class Deploy:
    # this uses recursion over a infrequent polling mechanism via Temporal's retry policy (@ 30 secs interval)
    # if `NOT_FOUND` error type is returned it will make the change (deploy)
    # other errors bubble all the way up
    async def deploy_component(self, params: DeployRequest, deploy_state: DeployState,
                               component_state: ComponentState) -> ComponentState:

        if component_state.status in [COMPONENT_STATUS_SUCCESS, COMPONENT_STATUS_ERROR]:
            # this assumes success or error yields an output
            component_state.output = (await workflow.execute_activity_method(
                PipelineActions.get_output,
                GetComponentOutputRequest(
                    id=component_state.id,
                    api_form=component_state.api_form,
                ),
                start_to_close_timeout=timedelta(seconds=10),
            )).output
            return component_state
        try:
            # this will infrequently poll the status due to activity non_retryable failure distinction
            component_state.status = (await workflow.execute_activity_method(
                PipelineActions.get_status,
                GetComponentStatusRequest(
                    id=component_state.id,
                    api_form=component_state.api_form,
                ),
                start_to_close_timeout=timedelta(10),
                retry_policy=RetryPolicy(
                    backoff_coefficient=1.0,
                    # poll every 30 seconds
                    initial_interval=timedelta(seconds=30),
                )
            )).status
            return await self.deploy_component(params, deploy_state, component_state)

        except ApplicationError as err:
            if err.type == COMPONENT_STATUS_NOT_FOUND:
                # TODO perform transform here
                deployment = await workflow.execute_activity_method(
                    PipelineActions.deploy,
                    DeployComponentRequest(
                        id=component_state.id,
                        api_form=component_state.api_form,
                        input=component_state.input,
                    ),
                    start_to_close_timeout=timedelta(seconds=10),
                )
                # recursive call to exit
                # we probably want to limit the number of times we are willing to do this recursion
                # alternately this same function could be turned into a child_workflow :)
                return await self.deploy_component(params, deploy_state, component_state)
            # a general error much have come up while checking status or trying the deployment so just let bubble up
            raise err

    @workflow.run
    async def run(self, params: DeployRequest) -> None:
        # ensure component ids first
        for idx, component in enumerate(params.components):
            # poor man's component id generator
            if not component.id:
                component.id = await workflow.execute_local_activity_method(
                    PipelineActions.get_id,
                    component.api_form,
                    start_to_close_timeout=timedelta(10)
                )
        # we could pass a `skip_validation` flag here
        # alternately, we could pass a `validation` results input
        # finally, could have the deployment continue after validation in Detached mode

        state = DeployState(components=[])
        state.components = list(map(lambda c: ComponentState(
            api_form=c.api_form,
            status=COMPONENT_STATUS_UNKNOWN,
            id=c.id or '',
            output={},
            input=c.input,
        ), params.components))

        for index, com in enumerate(state.components):
            state.components[index] = await self.deploy_component(params, state, com)
