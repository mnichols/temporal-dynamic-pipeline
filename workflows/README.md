# ci-poc



## ValidateInput Workflow spec

#### Input parameters specification

**root**

* `requester_name` <string>
* `requester_mail`: <string>
* `business_service`: <string>
* `num_components`: <int>
* `components`: [<component>]

**component**

* `status`: <string>
* `name`: <string>
* `order`: <int>
* `input`: <{depends:OnComponent}>
* `output`: <dict>
* `api_form`: <string>

1. For each item in `components`, validate each `input` field based on the `api_form` key.
   1. Place result into `dict` keyed by the `api_form`
2. Validation results:
   1. If any validation fails, **RETURN**. fail the workflow with validation results for upstream handling
   2. If all succeed, 
      1. **START** `DeployComponents` workflow
         1. Include the ValidationWorkflowID to verify inside
         2. Return the `array` (by `order`) of results produced by these input args: 
      2. **RETURN** the WorkflowID of the DeployComponents workflow

## DeployComponents Workflow spec

#### Input parameters spec

**root**

* `validation_workflow_id`: <string>
* `requester_name` <string>
* `requester_mail`: <string>
* `business_service`: <string>
* `num_components`: <int>
* `components`: [<component>]

**component**

* `status`: [string]
* `name`: [string]
* `order`: [int]
* `input`: [{depends:OnComponent}]
* `output`: [dict]
* `api_form`: [string]
  * used to call the correct function 

For each `component` in the `components` list:
    1. look up transformed outputs based on `api_form` key
    1. return output
    2. map output transformation based on other components' `api_form` keys to dict

call their APIs to deploy the component.

Each components' output would be subject to Transformers based on the 
Component types being requested. 