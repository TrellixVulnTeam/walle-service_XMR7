# Copyright (c) 2015 VMware. All rights reserved

from flask import Flask
from flask.ext import restful
from flask import request, g, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate

from pyvcloud.vcloudsession import VCS
from cloudify_rest_client.client import CloudifyClient

from score_api_server.common import cfg
from score_api_server.common import util
from score_api_server.common import org_limit
from score_api_server.resources import resources
from urlparse import urlparse


app = Flask(__name__)
api = restful.Api(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

CONF = cfg.CONF
app.config['SQLALCHEMY_DATABASE_URI'] = CONF.server.db_uri
util.setup_logging_for_app(app)
logger = util.setup_logging(__name__)
app.url_map.strict_slashes = False
ALLOWED_URLS = ['vchs.vmware.com']

# note: assume vcs.organization.id is unique across the service


@app.before_request
def check_authorization():
    logger.debug("Request headers %s", str(request.headers))
    if _can_skip_auth(request.path):
        return
    vcloud_token = request.headers.get('x-vcloud-authorization')
    vcloud_org_url = request.headers.get('x-vcloud-org-url', '')
    vcloud_version = request.headers.get('x-vcloud-version')
    if (vcloud_org_url and vcloud_token and vcloud_version):
        return check_authorization_vcloud(
            vcloud_org_url, vcloud_token, vcloud_version
        )

    openstack_authorization = request.headers.get('x-openstack-authorization')
    openstack_keystore = request.headers.get("x-openstack-keystore-url")
    if (openstack_keystore and openstack_authorization):
        return check_authorization_openstack(
            openstack_authorization, openstack_keystore
        )
    logger.error("Unauthorized. Aborting.")
    return make_response("Unauthorized.", 401)

def check_authorization_openstack(openstack_authorization, openstack_keystore):
    pass
    # return make_response("Unauthorized by OpenStack.", 401)

def check_authorization_vcloud(vcloud_org_url, vcloud_token, vcloud_version):
    if not _is_valid_url(vcloud_org_url):
        logger.error("Unauthorized. Invalid 'vcloud_org_url'. Aborting.")
        return make_response("Unauthorized:"
                             " 'vcloud_org_url' value not allowed", 401)
    vcs = VCS(vcloud_org_url, None, None, None,
              vcloud_org_url, vcloud_org_url,
              version=vcloud_version)
    result = vcs.login(token=vcloud_token)
    if result:
        logger.info("Organization authorized successfully.")
        g.org_id = vcs.organization.id[vcs.organization.id.rfind(':') + 1:]
        g.token = vcloud_token
        g.org_url = vcloud_org_url
        logger.info("Org-ID: %s.", g.org_id)
        if not org_limit.check_org_id(g.org_id):
            logger.error("Unauthorized. Aborting authorization "
                         "for Org-ID: %s.", g.org_id)
            return make_response("Unauthorized.", 401)

        g.current_org_id_limits = org_limit.get_org_id_limits(g.org_id)
        if g.current_org_id_limits:
            logger.info("Org-ID limits entity: %s",
                        g.current_org_id_limits.to_dict())
            logger.info("Limits for Org-ID:%s were found.", g.org_id)
            g.cc = CloudifyClient(host=g.current_org_id_limits.cloudify_host,
                                  port=g.current_org_id_limits.cloudify_port)
        else:
            logger.error("No limits were defined for Org-ID: %s", g.org_id)
            return make_response("Limits for Org-ID: %s were not defined. "
                                 "Please contact administrator."
                                 % g.org_id, 403)
    else:
        logger.error(str(vcs.response.status_code))
        return make_response(str(vcs.response.reason),
                             vcs.response.status_code)


def _can_skip_auth(path):
    name = path.split('/')[1].lower()
    if name == 'api':
        logger.info("Skipping authorizations with request headers,"
                    " show api specification.")
        return True
    elif name == 'login':
        logger.info("Skipping authorizations with request headers,"
                    " using user:password authorization.")
        return True
    return False


def _is_valid_url(vcloud_org_url):
    org_url = urlparse(vcloud_org_url)
    hostname = org_url.hostname
    for url in ALLOWED_URLS:
        if hostname and hostname.endswith(url):
            return True
    return False

resources.setup_resources(api)


def main():
    host, port, workers = (CONF.server.host,
                           CONF.server.port,
                           CONF.server.workers)
    app.logger_name = "score_api_server"
    app._logger_name = "score_api_server"
    app._logger = util.setup_logging(__name__)
    try:
        app.run(
            host=host,
            port=port,
            processes=workers,
            debug=(True if CONF.logging.level ==
                   "DEBUG" else False)
        )
    except Exception as e:
        print(str(e))

if __name__ == '__main__':
    main()
