"""
Generic api to access rancher
"""
import os
from rancher.resource.api import API
from rancher.resource.cluster import Cluster
from rancher.resource.project import Project
from rancher.resource.stack import Stack
from rancher.resource.service import Service

class RancherAPI:
    def __init__(self, rancherUrl=None, apiVersion=None, accessKey=None, secretKey=None):
        self.rancherUrl = rancherUrl or os.environ.get("RANCHER_URL")
        self.apiVersion = apiVersion or os.environ.get("RANCHER_API_VERSION")
        self.accessKey  = accessKey or os.environ.get("RANCHER_ACCESS_KEY")
        self.secretKey  = secretKey or os.environ.get("RANCHER_SECRET_KEY")
        self._auth      = (self.accessKey, self.secretKey)

    def clusters(self, **params):
        resourceApi = API("{}/{}/{}".format(self.rancherUrl, self.apiVersion, "clusters"), auth=self._auth)
        res = resourceApi.get(**params)
        return list(map(lambda r: Cluster(**r), res))

    def cluster(self, **params):
        resourceApi = API("{}/{}/{}".format(self.rancherUrl, self.apiVersion, "clusters"), auth=self._auth)
        res = resourceApi.getOne(**params)
        return Cluster(**res) if res else None

    def projects(self, **params):
        resourceApi = API("{}/{}/{}".format(self.rancherUrl, self.apiVersion, "projects"), auth=self._auth)
        res = resourceApi.get(**params)
        return list(map(lambda r: Project(**r), res))

    def project(self, **params):
        resourceApi = API("{}/{}/{}".format(self.rancherUrl, self.apiVersion, "projects"), auth=self._auth)
        res = resourceApi.getOne(**params)
        return Project(**res) if res else None

    def stacks(self, **params):
        resourceApi = API("{}/{}/{}".format(self.rancherUrl, self.apiVersion, "stacks"), auth=self._auth)
        res = resourceApi.get(**params)
        return list(map(lambda r: Stack(**r), res))

    def stack(self, **params):
        resourceApi = API("{}/{}/{}".format(self.rancherUrl, self.apiVersion, "stacks"), auth=self._auth)
        res = resourceApi.getOne(**params)
        return Stack(**res) if res else None

    def services(self, **params):
        resourceApi = API("{}/{}/{}".format(self.rancherUrl, self.apiVersion, "services"), auth=self._auth)
        res = resourceApi.get(**params)
        return list(map(lambda r: Service(**r), res))

    def service(self, **params):
        resourceApi = API("{}/{}/{}".format(self.rancherUrl, self.apiVersion, "services"), auth=self._auth)
        res = resourceApi.getOne(**params)
        return Service(**res) if res else None
