import sys
import re
import copy

from rancher.resource.base import Resource
from rancher.utils import utils


class Service(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        if self.type == "loadBalancerService":
            self.__class__ = LoadBalancerService

    def remove(self, timeout=None):
        """ Remove this service """
        super().drop()
        if timeout:
            return self._waitFor(dict(state="removed"), timeout=timeout)
        return self

    def update(self, updateParams={}, timeout=None):
        """ Update this service """
        super().update(**updateParams)
        if timeout:
            return self._waitFor(dict(state="active"), timeout=timeout)
        return self

    def upgrade(self, inServiceStrategy, timeout=None, rollback=False):
        """ Upgrade this service """
        launchConfig = utils.updateRecursive(self.launchConfig,
                                             inServiceStrategy.get("launchConfig"))

        inServiceStrategy["launchConfig"] = launchConfig
        super().upgrade(dict(inServiceStrategy=inServiceStrategy))
        if timeout:
            service = self._waitFor(dict(state="active"), timeout=timeout)
            if not service and rollback:
                self.rollback()
                self._waitFor(dict(state="active"), timeout=timeout)
                sys.exit(1)
        return self

    def restart(self, timeout=None, rollback=False):
        """ Restart this service """
        super().restart()
        if timeout:
            self._waitFor(dict(state="active"), timeout=timeout)


    def clean(self):
        """ Clean the service by removing containers that are not active or have error """
        # containerApi = ResourceAPI(self.links.get("instances"), Container)
        # containers = containerApi.get()
        # import pprint; pprint.pprint(containers[0]._info)
        # unhealthyContainers = list(filter(lambda c: c.healthState != "healthy", containers))
        # for container in unhealthyContainers:
        #     containerApi.remove(container.id)
        pass



class LoadBalancerService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pass

    def updateCustomHAConfig(self, backendName, customConfig):
        def getBackendConfigs(config):
            backendConfigs = {}
            if config:
                backendHeaderRE = "backend .*?\n"
                backendHeaders = re.findall(backendHeaderRE, config)
                for backendHeader in reversed(backendHeaders):
                    config, backendConfig = config.split(backendHeader)
                    if backendConfig.strip():
                        backendConfigs[backendHeader.strip()] = backendConfig.strip("\n")
            return backendConfigs

        def createBackendConfig(backendConfigs):
            return "\n".join(["\n".join(item) for item in backendConfigs.items()])

        backendConfigs = getBackendConfigs(self.lbConfig.get("config"))
        backendHeader = "backend {}".format(backendName)
        backendConfigs[backendHeader] = "\n".join(customConfig) + "\n"
        backendConfigs = dict(filter(lambda x: x[1].strip(), backendConfigs.items()))

        self.lbConfig["config"] = createBackendConfig(backendConfigs)

    def updatePortRule(self, portRule, customConfig=[], timeout=None):
        lbConfig = self.lbConfig

        # Remove matching portRules by filtering them out
        lbConfig["portRules"] = list(filter(
            lambda pr: not (
                # portRule["hostname"]   == pr["hostname"] and
                # portRule["path"]       == pr["path"] and
                portRule["sourcePort"] == pr["sourcePort"] and
                portRule["serviceId"]  == pr["serviceId"] and
                portRule["targetPort"] == pr["targetPort"] and
                portRule["protocol"]   == pr["protocol"]
            ),
            lbConfig["portRules"]))

        # portRule["backendName"] = "{}_{}_{}_{}".format(portRule["sourcePort"], portRule["serviceId"],
        #                                                portRule["targetPort"], portRule["protocol"])

        lbConfig["portRules"].insert(0, portRule)

        # Sort the port rules based on the hostname and the descending path
        lbConfig["portRules"].sort(key=lambda p: (p["hostname"], p["path"]), reverse=True)

        self.updateCustomHAConfig(portRule["backendName"], customConfig)

        data = dict(lbConfig=lbConfig)

        self.update(updateParams=data, timeout=timeout)

    def removePortRule(self, portRule, timeout=None):
        lbConfig = self.lbConfig

        # Remove matching portRules by filtering them out
        lbConfig["portRules"] = list(filter(
            lambda pr: not (
                portRule["hostname"]   == pr["hostname"] and
                portRule["path"]       == pr["path"] and
                portRule["sourcePort"] == pr["sourcePort"] and
                portRule["targetPort"] == pr["targetPort"]),
            lbConfig["portRules"]))

        data = dict(lbConfig=lbConfig)
        self.update(updateParams=data, timeout=timeout)


if __name__ == "__main__":
    lb = LoadBalancerService()
    lbConfig = {
        "config": r"""
something
rubbish
backend backend_1
reqrep hello world
backend backend_2
http_rewrite what is this
backend backend_3
        """
    }
    lb.lbConfig = lbConfig
    print(lbConfig["config"])

    lb.updateCustomHAConfig("backend_1", [r"reqrep ^([^\ :]*)\ {}/(.+)     \1\ {}\2"])
    import pprint
    print(lbConfig["config"])
