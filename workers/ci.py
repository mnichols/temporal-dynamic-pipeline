import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from workflows.deploy import Deploy
from workflows.activities import PipelineActions


async def main():
    client = await Client.connect("localhost:7233")
    activities = PipelineActions()

    worker = Worker(
        client,
        task_queue="ci",
        workflows=[Deploy],
        activities=[activities.get_id,
                    activities.validate,
                    activities.get_output,
                    activities.get_status,
                    activities.deploy,
                    activities.get_component_progress,
                    ],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
