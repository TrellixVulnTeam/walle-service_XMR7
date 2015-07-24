# Copyright (c) 2015 VMware. All rights reserved


class FakeBlueprint(dict):
    def __init__(self, obj_id, obj_blueprint_id, obj_deployment_id):
        self['id'] = obj_id
        self['blueprint_id'] = obj_blueprint_id
        self['deployment_id'] = obj_deployment_id

    @property
    def id(self):
        return self.get('id')

    @property
    def deployment_id(self):
        return self.get('deployment_id')

    @property
    def blueprint_id(self):
        return self.get('blueprint_id')


class FakeDeployment(dict):
    def __init__(self, data):
        self.update(data)

    @property
    def id(self):
        return self.get('id')

    @property
    def deployment_id(self):
        return self.get('deployment_id')

    @property
    def blueprint_id(self):
        return self.get('blueprint_id')
