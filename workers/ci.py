import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from workflows.deploy import Deploy
from workflows.activities import validate


async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="ci",
        workflows=[Deploy],
        activities=[validate],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
