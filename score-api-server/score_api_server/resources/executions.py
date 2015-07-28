# Copyright (c) 2015 VMware. All rights reserved

from flask import request, g
from flask.ext import restful
from flask.ext.restful import reqparse
from flask_restful_swagger import swagger

from cloudify_rest_client import exceptions

from score_api_server.common import util
from score_api_server.resources import responses
from score_api_server.resources import requests_schema

logger = util.setup_logging(__name__)
parser = reqparse.RequestParser()
parser.add_argument('deployment_id', type=str, help='Deployment ID')


class Executions(restful.Resource):

    @swagger.operation(
        responseClass='List[{0}]'.format(responses.Execution.__name__),
        nickname="list",
        notes="Returns a list of executions for the optionally provided "
              "deployment id.",
        parameters=[{'name': 'deployment_id',
                     'description': 'Deployment ID',
                     'required': False,
                     'allowMultiple': False,
                     'dataType': 'string',
                     'defaultValue': None,
                     'paramType': 'query'}]
    )
    def get(self):
        def _add_prefix_to_deployment(deployment_id):
            if deployment_id:
                deployment_id = util.add_org_prefix(deployment_id)
                logger.info("Listing all executions for deployment %s .",
                            deployment_id)
            else:
                logger.info("Listing all executions")
            return deployment_id

        logger.debug("Entering Execution.get method.")
        parsed = parser.parse_args()
        try:
            deployment_id = _add_prefix_to_deployment(parsed['deployment_id'])
            executions = g.cc.executions.list(deployment_id=deployment_id)
            filtered = [util.remove_org_prefix(e) for e in executions
                        if g.org_id in e['deployment_id']]
            return filtered
        except exceptions.CloudifyClientError as e:
            return util.make_response_from_exception(e)


class ExecutionsId(restful.Resource):

    @swagger.operation(
        responseClass=responses.Execution,
        nickname="getById",
        notes="Returns the execution state by its id.",
        parameters=[{'name': 'execution_id',
                     'description': 'Execution ID',
                     'required': False,
                     'allowMultiple': False,
                     'dataType': 'string',
                     'defaultValue': None,
                     'paramType': 'path'}]
    )
    def get(self, execution_id=None):
        logger.debug("Entering ExecutionsId.get method.")
        try:
            logger.info(
                "Seeking for executions by execution %s.",
                execution_id)
            result = g.cc.executions.get(execution_id)
            logger.debug("Done. Exiting ExecutionsId.get method.")
            return util.remove_org_prefix(result)
        except exceptions.CloudifyClientError as e:
            logger.error(str(e))
            return util.make_response_from_exception(e)

    @swagger.operation(
        responseClass=responses.Execution,
        nickname="startExecution",
        notes="Started a new execution of the given deployment and "
              "workflow ids.",
        parameters=[{'name': 'deployment_id',
                     'description': 'Deployment id',
                     'required': True,
                     'allowMultiple': False,
                     'dataType': 'string',
                     'paramType': 'query'},
                    {'name': 'workflow_id',
                     'description': 'Workflow id',
                     'required': True,
                     'allowMultiple': False,
                     'dataType': requests_schema.ExecutionRequest.__name__,
                     'paramType': 'query'},
                    {'name': 'parameters',
                     'description': 'Parameters for execution',
                     'required': False,
                     'allowMultiple': False,
                     'dataType': requests_schema.ExecutionRequest.__name__,
                     'paramType': 'body'},
                    {'name': 'allow_custom_parameters',
                     'description': 'Custom parameters',
                     'required': False,
                     'allowMultiple': False,
                     'dataType': requests_schema.ExecutionRequest.__name__,
                     'paramType': 'body'},
                    {'name': 'force',
                     'description': 'Execution start force',
                     'required': False,
                     'allowMultiple': False,
                     'defaultValue': False,
                     'dataType': requests_schema.ExecutionRequest.__name__,
                     'paramType': 'body'}],
        consumes=[
            "application/json"
        ]
    )
    def post(self):
        logger.debug("Entering Execution.post method.")
        deployment_id = util.add_org_prefix(request.json.get('deployment_id'))
        try:
            workflow_id = request.json.get('workflow_id')
            logger.info("Looking for deployment %s .", deployment_id)
            g.cc.deployments.get(deployment_id)
            logger.info("Staring workflow %s for deployment %s.",
                        workflow_id, deployment_id)
            result = g.cc.executions.start(deployment_id, workflow_id)
            logger.debug("Done. Exiting Executions.post method.")
            return util.remove_org_prefix(result)
        except (exceptions.CloudifyClientError,
                exceptions.DeploymentEnvironmentCreationInProgressError,
                exceptions.DeploymentEnvironmentCreationPendingError) as e:
            # should we wait for deployment environment creation workflow?
            logger.error(str(e))
            response_code = (
                403 if isinstance(e, (
                    exceptions.DeploymentEnvironmentCreationInProgressError,
                    exceptions.DeploymentEnvironmentCreationPendingError))
                else e.status_code)
            return util.make_response_from_exception(e, response_code)

    @swagger.operation(
        responseClass=responses.Execution,
        nickname="modify_state",
        notes="Modifies a running execution state (currently, only cancel"
              " and force-cancel are supported)",
        parameters=[{'name': 'body',
                     'description': 'json with an action key. '
                                    'Legal values for action are: [cancel,'
                                    ' force-cancel]',
                     'required': True,
                     'allowMultiple': False,
                     'dataType': requests_schema.ModifyExecutionRequest.__name__,  # NOQA
                     'paramType': 'body'}],
        consumes=[
            "application/json"
        ]
    )
    def put(self):
        logger.debug("Entering Execution.put method.")
        execution_id = request.json.get('execution_id')
        try:
            force = request.json.get('force')
            self.get(execution_id=execution_id)
            result = g.cc.executions.cancel(execution_id, force)
            logger.debug("Done. Exiting Executions.put method.")
            return util.remove_org_prefix(result)
        except exceptions.CloudifyClientError as e:
            logger.error(str(e))
            return util.make_response_from_exception(e)
