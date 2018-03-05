from rancher.resource.base import Resource
from rancher.resource.api import API

from rancher.resource.service import Service
from rancher.utils import utils

from . import template
import sys

class Stack(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.serviceApi = API(url=self.links.get("services"))

    def getServices(self, **kwargs):
        """ Get all services """
        allServices = self.serviceApi.get(**kwargs)
        services = filter(lambda service: service.get("id") in self.serviceIds, allServices)
        services = list(map(lambda service: Service(**service), services))
        return services

    def getService(self, **kwargs):
        """ Get single service """
        services = self.getServices(**kwargs)
        return services[0] if services else None

    def addService(self, serviceParams, timeout=None, rollback=False):
        """ Add a service """
        serviceTemplate = template.create("service")

        # Update the template with provided parameters
        serviceTemplate = utils.updateRecursive(serviceTemplate, serviceParams)

        # Set the project id and stack id
        serviceTemplate["launchConfig"]["accountId"] = self.accountId
        serviceTemplate["stackId"] = self.id

        serviceInfo = self.serviceApi.add(serviceTemplate)
        if serviceInfo:
            service = Service(**serviceInfo)
            if service and timeout:
                srv = service._waitFor(dict(state="active"), timeout=timeout)
                if not srv and rollback:
                    service.remove(timeout)
                    sys.exit(1)

            return service
