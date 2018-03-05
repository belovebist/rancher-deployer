from rancher.resource.base import Resource
from rancher.resource.api import API
from rancher.resource.project import Project

class Cluster(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.projectApi = API(url="{}/{}".format(self.selfUrl, "projects"))
        self.stackApi   = API(url=self.links["stacks"])
        self.serviceApi = API(url=self.links["services"])

    def getProjects(self, **kwargs):
        """ Get projects """
        projects = self.projectApi.get(**kwargs)
        projects = list(map(lambda proj: Project(**proj), projects))
        return projects

    def getProject(self, **kwargs):
        """ Get single project """
        projects = self.getProjects(**kwargs)
        return projects[0] if projects else None