#coding:utf-8

class Servers(object):
    def __init__(self):
        self.called_with = []
        self.servers = {}

    def find(self, name):
        self.called_with.append(name)
        return self.servers[name]


class Flavors(object):
    def __init__(self):
        self.called_with = []
        self.flavors = {}

    def get(self, flavor_id):
        self.called_with.append(flavor_id)
        return self.flavors[flavor_id]


class Volumes(object):
    def __init__(self):
        self.called_with = []
        self.volumes = {}

    def get_server_volumes(self, instance_id):
        self.called_with.append(instance_id)
        return self.volumes[instance_id]


class CloudServers(object):
    servers = Servers()
    flavors = Flavors()
    volumes = Volumes()


class CloudBlockStorage(object):
    def __init__(self):
        self.called_with = []
        self.volumes = {}

    def get(self, volume_id):
        self.called_with.append(volume_id)
        return self.volumes[volume_id]


class MockPyrax(object):
    cloudservers = CloudServers()
    cloud_blockstorage = CloudBlockStorage()


class MockServer(object):
    def __init__(self, instance_id, flavor_id):
        self.id = instance_id
        self.flavor = {"id": flavor_id}

class MockFlavor(object):
    def __init__(self, human_id):
        self.human_id = human_id


class MockIncompleteVolume(object):
    def __init__(self, id):
        self.id = id

class MockActualVolume(object):
    def __init__(self, size, attachments):
        self.size = size
        self.attachments = attachments
