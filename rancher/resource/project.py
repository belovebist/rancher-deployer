from rancher.resource.base import Resource
from rancher.resource.api import API

from rancher.resource.stack import Stack
from rancher.resource.service import Service

from . import template

class Project(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.stackApi = API(url=self.links.get("stacks"))
        self.serviceApi = API(url=self.links.get("services"))

    def getStacks(self, **kwargs):
        """ Get stacks """
        stacks = self.stackApi.get(**kwargs)
        stacks = list(map(lambda stack: Stack(**stack), stacks))
        return stacks

    def getStack(self, **kwargs):
        """ Get single stack """
        stacks = self.getStacks(**kwargs)
        return stacks[0] if stacks else None

    def getServices(self, **kwargs):
        """ Get all services """
        allServices = self.serviceApi.get(**kwargs)
        services = filter(lambda service: service.get("accountId") == self.id, allServices)
        services = list(map(lambda service: Service(**service), services))
        return services

    def getService(self, **kwargs):
        """ Get single service """
        services = self.getServices(**kwargs)
        return services[0] if services else None

    def addStack(self, **kwargs):
        """ Add stack """
        stackTemplate = template.create("stack")
        stackTemplate.update(kwargs)
        stack = self.stackApi.add(stackTemplate)
        if stack:
            return Stack(**stack)
