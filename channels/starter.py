import asyncio

from temporalio.client import Client

from messaging.workflows import DeployRequest, Component
from workflows.deploy import ValidateDeployment

async def main():
    client = await Client.connect("localhost:7233")
    result = await client.execute_workflow(
        ValidateDeployment.run,
        DeployRequest(
            requester_mail="",
            requester_name="",
            ci="",
            num_components=1,
            common_values={},
            components=[
                Component(
                    name="Foo",
                    api_form="foo",
                    status="PENDING",
                    order=1,
                    output={},
                    input={
                        "bonk": "beep",
                    },
                ),
            ]
        ),
        id="deploy-foo",
        task_queue="ci",
    )
    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())