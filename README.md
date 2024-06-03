# temporal-dynamic-pipeline

## To Run

1. Start Temporal local server: `temporal server start-dev`
2. Start a Temporal Worker in one terminal
3. execute the `Deploy` workflow in another terminal

```shell
# in one terminal start the worker

poetry install
poetry run python workers/ci.py # if nothing happens it is working
```

```shell
# in another terminal start a workflow
temporal workflow start \
  --input-file /path/to/input.json \
  --task-queue ci \
  --type Deploy \
  --workflow-id x123 
```

Visit http://localhost:8233/namespaces/default/workflows

You should see your Workflow started and sequentially deploying each
component in the `components` in your file.

**NOTE**

I included the `transform` of `output` -> `input` _inside_ the 
`deploy` activity. Why? If the mapping of one fieldname to another
is volatile (changes often) then you might want to do the mapping 
inside the Activity so you can ship new mappings without breaking existing
executions.
