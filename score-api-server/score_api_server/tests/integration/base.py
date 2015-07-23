# Copyright (c) 2015 VMware. All rights reserved

import os
import tempfile
import testtools
import urllib
import shutil
import tarfile
import yaml

from os.path import expanduser

from flask.ext.migrate import upgrade
import git
from pyvcloud.vcloudair import VCA
from pyvcloud.vcloudsession import VCS

from score_api_server.cli import app
from score_api_server.db import models
from score_api_server.tests.fakes import exceptions
from score_api_server.tests.fakes import vcloud_air_client
from score_api_server.tests.fakes import cloudify_manager

RUN_INTEGRATION_TESTS = 'RunIntegrationTests'


class BaseScoreAPIClient(testtools.TestCase):

    def setUp(self):
        super(BaseScoreAPIClient, self).setUp()

    def tearDown(self):
        super(BaseScoreAPIClient, self).tearDown()

    def execute_get_request_with_route(self, route):
        pass

    def execute_delete_request_with_route(self, route):
        pass

    def execute_put_request_with_route(self, route,
                                       params=None,
                                       data=None):
        pass

    def execute_post_request_with_route(self, route,
                                        params=None,
                                        data=None):
        pass

    def try_auth(self, headers=None):
        pass

    def make_upload_blueprint(self):
        # TODO(???) make blueprint path configurable
        blueprint_filename = "vcloud-postgresql-blueprint.yaml"
        current_dir = os.path.dirname(os.path.realpath(__file__))
        blueprints_dir = current_dir + '/../../../../blueprints/'
        blueprint_path = blueprints_dir + blueprint_filename
        response = self.upload_blueprint(blueprint_path, blueprint_filename)
        return response

    def upload_blueprint(self, blueprint_path, blueprint_id):
        tempdir = tempfile.mkdtemp()
        try:
            tar_path = self._tar_blueprint(blueprint_path, tempdir)
            application_file = os.path.basename(blueprint_path)
            return self._upload(
                tar_path,
                blueprint_id=blueprint_id,
                application_file_name=application_file)
        finally:
            shutil.rmtree(tempdir)

    def _tar_blueprint(self, blueprint_path, tempdir):

        blueprint_path = expanduser(blueprint_path)
        blueprint_name = os.path.basename(
            os.path.splitext(blueprint_path)[0])
        blueprint_directory = os.path.dirname(blueprint_path)

        if not blueprint_directory:
            # blueprint path only contains a file name from the local directory
            blueprint_directory = os.getcwd()
        tar_path = os.path.join(
            tempdir, '{0}.tar.gz'.format(blueprint_name))

        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(
                blueprint_directory,
                arcname=os.path.basename(blueprint_directory))

        return tar_path

    def _upload(self, tar_file,
                blueprint_id,
                application_file_name=None):
        query_params = {}
        if application_file_name is not None:
            query_params[
                'application_file_name'] = urllib.quote(
                application_file_name)
        try:
            self.execute_get_request_with_route(
                '/blueprints/{0}'.format(blueprint_id))
            self.execute_delete_request_with_route(
                '/blueprints/{0}'.format(blueprint_id))
        finally:
            with open(tar_file, 'rb') as f:
                return self.execute_put_request_with_route(
                    '/blueprints/{0}'.format(blueprint_id),
                    params=query_params,
                    data=f.read())


class RealScoreAPIClient(BaseScoreAPIClient):

    def setUp(self):
        super(BaseScoreAPIClient, self).setUp()

        current_dir = os.path.dirname(os.path.realpath(__file__))
        path_to_login_json = (current_dir +
                              '/../../../real-mode-tests-conf.yaml')
        with open(path_to_login_json, 'r') as stream:
            login_cfg = yaml.load(stream)
        self.service_version = login_cfg.get('service_version')
        cloudify_host = login_cfg.get('cloudify_host')
        cloudify_port = login_cfg.get('cloudify_port')
        deployment_limits = login_cfg.get('deployment_limits')

        # login to VCA
        self.vca = self._login_to_vca(login_cfg)

        # headers
        self.headers = {
            'x-vcloud-authorization': self.vca.vcloud_session.token,
            'x-vcloud-org-url': self.vca.vcloud_session.org_url,
            'x-vcloud-version': self.service_version,
        }

        vcloud_org_url = self.vca.vcloud_session.org_url

        self.vcs = VCS(vcloud_org_url, None, None, None,
                       vcloud_org_url, vcloud_org_url,
                       version=self.service_version)

        # login to VCS
        result = self.vcs.login(token=self.headers['x-vcloud-authorization'])
        if not result:
            raise exceptions.Forbidden()
        org_id = self.vcs.organization.id[
            self.vcs.organization.id.rfind(':') + 1:]
        self.organization = models.AllowedOrgs(org_id)
        self.model_limits = models.OrgIDToCloudifyAssociationWithLimits(
            self.organization.org_id, cloudify_host, cloudify_port,
            deployment_limits=deployment_limits)

        self.addCleanup(self.vca.logout)

    def _login_to_vca(self, login_json):
        request_json = login_json
        if request_json:
            user = request_json.get('user')
            password = request_json.get('password')
            service_type = request_json.get('service_type', 'subscription')
            host = request_json.get('host', 'https://vchs.vmware.com')
            org_name = request_json.get('org_name')
            service = request_json.get('service')
            vca = self._login_user_to_service(user, host,
                                              password, service_type,
                                              self.service_version,
                                              service, org_name)
            return vca

    def _login_user_to_service(self, user, host, password, service_type,
                               service_version, service, org_name):
        vca = VCA(host, user, service_type, service_version)
        result = vca.login(password=password)
        if result:
            if service_type == 'subscription':
                if not service:
                    if org_name:
                        service = org_name
                    else:
                        services = vca.services.get_Service()
                        if not services:
                            return None
                        service = services[0].serviceId
                if not org_name:
                    org_name = vca.get_vdc_references(service)[0].name
                result = vca.login_to_org(service, org_name)
            if result:
                return vca
        return

    def try_auth(self, headers=None):
        if not headers:
            self.vca.logout()
            return self.client.get('/', headers=headers)
        self.model_limits.delete()
        return self.client.get('/', headers=self.headers)

    def execute_get_request_with_route(self, route):
        return self.client.get(route, headers=self.headers)

    def execute_delete_request_with_route(self, route):
        return self.client.delete(route, headers=self.headers)

    def execute_put_request_with_route(self, route, params=None, data=None):
        return self.client.put(route, headers=self.headers,
                               query_string=params, data=data)

    def execute_post_request_with_route(self, route, params=None, data=None):
        return self.client.post(route, headers=self.headers,
                                query_string=params, data=data)


class FakeScoreAPIClient(BaseScoreAPIClient):

    def setUp(self):
        # monkey-patching VCS class to
        # disable vCloud Air logging
        self.safe_vcs = app.VCS
        app.VCS = vcloud_air_client.VCS

        # monkey-patching Cloudify ReST client with
        # fake implementation of it
        self.safe_cfy = app.CloudifyClient
        app.CloudifyClient = cloudify_manager.CloudifyClient

        self.safe_login = vcloud_air_client.VCS.login
        self.headers = {
            "x-vcloud-authorization": "True",
            "x-vcloud-org-url": "URL",
            "x-vcloud-version": "some_version"
        }
        super(FakeScoreAPIClient, self).setUp()

    def do_common_setup(self):

        def login(self, **kwargs):
            self.organization = self.Org()
            models.OrgIDToCloudifyAssociationWithLimits(
                self.organization.id,
                "127.0.0.1",
                "80",
                deployment_limits=-1,
            )
            return self

        vcloud_air_client.VCS.login = login

    def try_auth(self, headers=None):
        return self.client.get('/', headers=headers)

    def execute_get_request_with_route(self, route):
        self.do_common_setup()
        return self.client.get(route, headers=self.headers)

    def execute_delete_request_with_route(self, route):
        self.do_common_setup()
        return self.client.delete(route, headers=self.headers)

    def execute_put_request_with_route(self, route,
                                       params=None, data=None):
        self.do_common_setup()
        return self.client.put(route,
                               headers=self.headers,
                               query_string=params,
                               data=data)

    def execute_post_request_with_route(self, route,
                                        params=None, data=None):
        self.do_common_setup()
        return self.client.post(route,
                                headers=self.headers,
                                query_string=params,
                                data=data)

    def tearDown(self):
        app.VCS = self.safe_vcs
        app.CloudifyClient = self.safe_cfy
        vcloud_air_client.VCS.login = self.safe_login
        super(FakeScoreAPIClient, self).tearDown()


def _lookup_mode_value(message):
    found_string = filter(lambda x: RUN_INTEGRATION_TESTS in x,
                          message.split('\n'))[0]
    return found_string.split(' ')[1]


def _checking_mode():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    git_dir = current_dir + '/../../../..'
    git_repo = git.repo.Repo(git_dir)
    message = git_repo.commit().message
    if (RUN_INTEGRATION_TESTS in message and
            _lookup_mode_value(message) == 'True'):
        return True
    return False


def printing_message_which_base_class(base_class):
    message_which_base_class = 'Running tests with %s' % base_class.__name__
    print('-' * len(message_which_base_class))
    print(message_which_base_class)
    print('-' * len(message_which_base_class))


def get_base_class():
    test_mode = _checking_mode()
    base_class = (FakeScoreAPIClient
                  if test_mode is not True
                  else RealScoreAPIClient)
    printing_message_which_base_class(base_class)
    return base_class


class IntegrationBaseTestCase(get_base_class()):

    def setUp(self):
        app.app.config['TESTING'] = True
        self.client = app.app.test_client()

        self.db_fd, self.db_fpath = tempfile.mkstemp()
        app.app.config['SQLALCHEMY_DATABASE_URI'] = (
            "sqlite:///%s.db" % self.db_fpath)

        current_dir = os.path.dirname(os.path.realpath(__file__))
        with app.app.app_context():
            migrate_dir = current_dir + '/../../../migrations/'
            upgrade(directory=migrate_dir)
            app.db.create_all()

        super(IntegrationBaseTestCase, self).setUp()

    def tearDown(self):

        for org_id in models.AllowedOrgs.list():
            org_id.delete()
        for org_id in models.OrgIDToCloudifyAssociationWithLimits.list():
            org_id.delete()

        os.close(self.db_fd)
        os.unlink(self.db_fpath)
        os.remove("%s.db" % self.db_fpath)

        super(IntegrationBaseTestCase, self).tearDown()
