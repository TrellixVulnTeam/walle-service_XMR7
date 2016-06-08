# Copyright (c) 2016 VMware. All rights reserved
import time
import md5
from flask import make_response, g
from score_api_server.resources import responses
from flask.ext import restful
from score_api_server.common import util
from flask_restful_swagger import swagger


logger = util.setup_logging(__name__)


class LoginScore(restful.Resource):
    @swagger.operation(
        responseClass=responses.LoginScore,
        nickname="login_score",
        notes="Returns information for authorization in Score.",
        parameters=[{'name': 'user',
                     'description': 'User login.',
                     'required': True,
                     'allowMultiple': False,
                     'dataType': 'string',
                     'paramType': 'body'},
                    {'name': 'password',
                     'description': 'User password.',
                     'required': True,
                     'allowMultiple': False,
                     'dataType': 'string',
                     'paramType': 'body'}],
        consumes=['application/json']
    )
    @util.validate_json(
        {"type": "object",
         "properties": {
             "user": {"type": "string", "minLength": 1},
             "password": {"type": "string", "minLength": 1}
         },
         "required": ["user", "password"]}
    )
    def post(self, json):
        logger.debug("Entering Login.get method.")
        user = json.get('user')
        password = json.get('password')
        score_logined = False
        from score_api_server.db.models import ScoreAdministrators
        admin = ScoreAdministrators.find_by(name=user)
        if admin and admin.password == password:
            expire_time = _get_expire_time()
            g.token = _generate_token(password, expire_time)
            admin.update(token=g.token, expire=expire_time)
            score_logined = True
        else:
            logger.error("Login failed")
        if score_logined:
            reply = {
                'x-score-authorization': g.token,
            }
            return reply
        return make_response("Unauthorized. Recheck credentials.", 401)


def _get_expire_time():
    now = time.time()
    expire_sec = 30 * 60
    return now + expire_sec


def _generate_token(password, timestamp):
    return md5.new(password + str(timestamp)).hexdigest()
