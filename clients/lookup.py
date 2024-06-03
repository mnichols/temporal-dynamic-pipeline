from clients.pipeline import ComponentConfig, PipelineClient

# global mock of database, holding current state of a deployment
# key <str> is api_form, value is ComponentState
COMPONENT_PROGRESS = {}

SOURCE_2_DEST_TRANSFORMS = {
    'apache-bundle': {
        'vmware-rsoe7': {
            'url': 'fqdn',
        }
    },
    'postgre-bundle': {
        'vmware-rsoe7': {
            'url': 'fqdn'
        }
    }
}

# global lookup for transformations
# key is the DEST api_form,
# value is a dict[str, {}] where key is SRC api_form
# value value is a dict[str, str] that maps src property names to the dest property name (scoped by api_form)
def get_component_config(api_form: str) -> ComponentConfig:
    return ComponentConfig(api_form, url='https:ci.{}.com'.format(api_form))


def get_pipeline_client(api_form: str) -> PipelineClient:

    return PipelineClient(get_component_config(api_form), component_progress=COMPONENT_PROGRESS, transforms=SOURCE_2_DEST_TRANSFORMS)
