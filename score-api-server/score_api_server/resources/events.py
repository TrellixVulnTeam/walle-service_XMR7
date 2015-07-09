# Copyright (c) 2015 VMware. All rights reserved

from flask.ext import restful
from flask import request, g, make_response
from flask.ext.restful import reqparse
from flask_restful_swagger import swagger

from score_api_server.common import util

from cloudify_rest_client import exceptions

logger = util.setup_logging(__name__)
parser = reqparse.RequestParser()


class Events(restful.Resource):

    @swagger.operation(
        nickname='events',
        notes='Returns a list of events.',
        parameters=[{'name': 'execution_id',
                     'description': 'Execution ID',
                     'required': True,
                     'allowMultiple': False,
                     'dataType': 'string',
                     'paramType': 'query'},
                    {'name': 'from_event',
                     'description': 'Index of event',
                     'required': False,
                     'allowMultiple': False,
                     'dataType': 'string',
                     'defaultValue': '0',
                     'paramType': 'query'},
                    {'name': 'batch_size',
                     'description': 'Batch size',
                     'required': False,
                     'allowMultiple': False,
                     'dataType': 'string',
                     'defaultValue': '100',
                     'paramType': 'query'},
                    {'name': 'include_logs',
                     'description': 'Include logs',
                     'required': False,
                     'allowMultiple': False,
                     'dataType': 'boolean',
                     'defaultValue': False,
                     'paramType': 'query'}],
        consumes=['application/json']
    )
    def get(self):
        logger.debug("Entering Events.get method.")
        try:
            request_json = request.json
            logger.info("Seeking for events by execution-id: %s",
                        request_json.get('execution_id'))
            result = g.cc.events.get(request_json.get('execution_id'),
                                     request_json.get('from'),
                                     request_json.get('size'),
                                     request_json.get('include_logs'))
            logger.debug("Done. Exiting Events.get method.")
            if len(result) == 2:
                r = result[0]
                r.append(result[1])
                return r
            else:
                return []
        except exceptions.CloudifyClientError as e:
            logger.error(str(e))
            return make_response(str(e), e.status_code)
