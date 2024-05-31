from clients.pipeline import ComponentConfig, PipelineClient

API_FORMS = [
    'foo',
    'bar',
    'moo',
    'mar'
]

COMPONENT_PROGRESS = {}
def get_component_config(api_form: str) -> ComponentConfig:
    return ComponentConfig(api_form, url='https:ci.{}.com'.format(api_form))


def get_pipeline_client(api_form: str) -> PipelineClient:

    return PipelineClient(get_component_config(api_form), component_progress=COMPONENT_PROGRESS)
