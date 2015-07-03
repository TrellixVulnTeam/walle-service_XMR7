# Copyright (c) 2015 VMware. All rights reserved

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from score_api_server.cli import app
from score_api_server.db import models
from score_api_server.common import print_utils


db = app.db
flask_app = app.app

migrate = Migrate(flask_app, db)
manager = Manager(flask_app)


OrgIDCommands = Manager(usage="Performs action related to Org-IDs")
OrgIDLimitsCommands = Manager(usage="Performs action related to Org-ID limits")


@OrgIDCommands.option("--org-id", dest="org_id",
                      help="Adds Org-IDs to Score DB")
@OrgIDCommands.option("--info", dest="info",
                      help="Adds Org-IDs to Score DB")
@OrgIDCommands.option("--db-uri", dest="db_uri", default=None)
def add(org_id, db_uri=None, info=None):
    """Adds Org-ID."""
    if db_uri:
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    if not org_id:
        print("ERROR: Org-ID is required")
    else:
        org = models.AllowedOrgs(org_id, info=info)
        print_utils.print_dict(org.to_dict())


@OrgIDCommands.option("--org-id", dest="org_id",
                      help="Deletes Org-ID from Score DB")
@OrgIDCommands.option("--db-uri", dest="db_uri", default=None)
def delete(org_id, db_uri=None):
    """Deletes Org-ID."""
    if db_uri:
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    if not org_id:
        print("ERROR: Org-ID is required")
    else:
        org = models.AllowedOrgs.find_by(org_id)
        if org:
            org.delete()
            print("OK")
        else:
            print("ERROR: Org-ID not found")


@OrgIDCommands.option("--db-uri", dest="db_uri", default=None)
def list(db_uri=None):
    """Lists Org-IDs."""

    if db_uri:
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    org_ids = models.AllowedOrgs.list()
    print_utils.print_list(org_ids, ["id", "org_id",
                                     "info", "created_at"])


@OrgIDLimitsCommands.option("--org-id", dest="org_id")
@OrgIDLimitsCommands.option("--cloudify-host", dest="cloudify_host")
@OrgIDLimitsCommands.option("--cloudify-port", dest="cloudify_port")
@OrgIDLimitsCommands.option("--deployment-limits",
                            dest="deployment_limits", default=0)
@OrgIDLimitsCommands.option("--db-uri", dest="db_uri", default=None)
def create(org_id, cloudify_host, cloudify_port,
           deployment_limits, db_uri=None):
    """Creates deployment limits pinned to specific
       Org-ID and specific Cloudify Manager
    """
    if db_uri:
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    if not cloudify_host or not cloudify_port:
        print("ERROR: Cloudify host and port are required.")
        return
    else:
        if not models.AllowedOrgs.find_by(org_id=org_id):
            print("ERROR: No such Org-ID.")
            return
        limit = models.OrgIDToCloudifyAssociationWithLimits(
            org_id,
            cloudify_host,
            cloudify_port,
            deployment_limits,
        )
        print_utils.print_dict(limit.to_dict())


@OrgIDLimitsCommands.option("--db-uri", dest="db_uri", default=None)
def list(db_uri=None):
    """Lists all Org-ID limits."""

    if db_uri:
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    limits = models.OrgIDToCloudifyAssociationWithLimits.list()
    print_utils.print_list(limits, ["id", "org_id", "cloudify_host",
                                    "cloudify_port", "deployment_limits",
                                    "number_of_deployments",
                                    "created_at", "updated_at"])


@OrgIDLimitsCommands.option("--id", dest="id")
@OrgIDLimitsCommands.option("--org-id", dest="org_id")
@OrgIDLimitsCommands.option("--cloudify-host", dest="cloudify_host")
@OrgIDLimitsCommands.option("--cloudify-port", dest="cloudify_port")
@OrgIDLimitsCommands.option("--deployment-limits", dest="deployment_limits")
@OrgIDLimitsCommands.option("--number-of-deployments",
                            dest="number_of_deployments")
@OrgIDLimitsCommands.option("--db-uri", dest="db_uri", default=None)
def update(**kwargs):
    """Updates Org-ID limits with given keys by its ID."""
    db_uri = kwargs.get("db_uri")
    update_kwargs = {}
    if db_uri:
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    limit_id = kwargs["id"]

    keys = ["org_id", "cloudify_host", "cloudify_port",
            "deployment_limits", "number_of_deployments"]

    for key in keys:
        if kwargs.get(key):
            update_kwargs.update({key: kwargs.get(key)})

    if (not models.AllowedOrgs.find_by(org_id=kwargs.get("org_id"))
            and not limit_id):
        print("ERROR: ID or existing Org-ID required.")
        return

    limit = models.OrgIDToCloudifyAssociationWithLimits.find_by(
        id=limit_id)
    if not limit:
        print("No such Org-ID limit entity.")
    else:
        limit.update(**update_kwargs)
        updated_limit = (
            models.OrgIDToCloudifyAssociationWithLimits.find_by(
                id=limit_id))
        print_utils.print_dict(updated_limit.to_dict())


@OrgIDLimitsCommands.option("--id", dest="id")
@OrgIDLimitsCommands.option("--db-uri", dest="db_uri", default=None)
def delete(**kwargs):
    """Deletes Org-ID limit by its ID."""
    db_uri = kwargs.get("db_uri")
    if db_uri:
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    limit = models.OrgIDToCloudifyAssociationWithLimits.find_by(
        id=kwargs.get("id"))
    if not limit:
        print("ERROR: No such Org-ID limit entity.")
        return
    else:
        limit.delete()
        print("OK")


manager.add_command('org-ids', OrgIDCommands)
manager.add_command('org-id-limits', OrgIDLimitsCommands)
manager.add_command('db', MigrateCommand)


def main():
    manager.run()

if __name__ == '__main__':
    main()
