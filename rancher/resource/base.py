import sys
import time
import logging
from rancher.resource.api import API

log = logging.getLogger(__name__)

class Resource:
    def __init__(self, *args, **kwargs):
        self._info = kwargs
        self.selfUrl = self.links.get("self")
        self.baseUrl = self.selfUrl.rstrip("/{}".format(self.id))
        self.api     = API(url=self.baseUrl)

    def __getattribute__(self, name):
        try:
            value = object.__getattribute__(self, name)
        except AttributeError:
            value = self._info.get(name)
        return value

    def _waitFor(self, condition, timeout=None):
        """ Wait for timeout until the given condition (key-value pairs) match the object's info """
        if timeout is not None:
            assert isinstance(timeout, int), "Timeout should be a valid number of seconds!"
        for t in range(0, timeout, 1):
            time.sleep(1)
            reloaded = self.reload()
            if reloaded:
                log.warning("Current: [{}], Expected: [{}]".format(
                    ",".join(map(lambda key: "{}={}".format(key, getattr(reloaded, key)), condition)),
                    ",".join(map(lambda key: "{}={}".format(key, condition[key]), condition))
                    ))

                if all(map(lambda key: condition[key] == getattr(reloaded, key), condition)):
                    self.__init__(**reloaded._info)
                    return self
            else:
                log.error("{}={} does not exist.".format(self.type, self.name))
                sys.exit(1)
        else:
            log.error("TIMEOUT ({}): Unable to complete within timeout.".format(timeout))

    def reload(self):
        """ Reload service data """
        if not self.links.get("self"):
            res = self.api.getOne(id=self.id)
            return self.__class__(**res) if res else None
        else:
            resp = self.api.request.get(self.links.get("self"))
            if resp.ok:
                return self.__class__(**resp.json())

    def drop(self):
        """ Drop this resource """
        if not self.links.get("remove"):
            res = self.api.remove(id=self.id)
            return self.__class__(**res) if res else None
        else:
            resp = self.api.request.delete(self.links["remove"])
            if resp.ok:
                return self.__class__(**resp.json())

    def update(self, **kwargs):
        """ Update this resource """
        updateStrategy = kwargs
        if not self.links.get("update"):
            res = self.api.update(id=self.id, updateStrategy=updateStrategy)
            return self.__class__(**res) if res else None
        else:
            resp = self.api.request.put(self.links["update"], json=updateStrategy)
            if resp.ok:
                return self.__class__(**resp.json())

    def restart(self):
        """ Restart this resource """
        if not self.actions.get("restart"):
            res = self.api.restart(self.id)
            return self.__class__(**res) if res else None
        else:
            resp = self.api.request.post(self.actions["restart"])
            if resp.ok:
                return self.__class__(**resp.json())

    def activate(self):
        """ Activate this resource """
        if not self.actions.get("activate"):
            res = self.api.activate(self.id)
            return self.__class__(**res) if res else None
        else:
            resp = self.api.request.post(self.actions["activate"])
            if resp.ok:
                return self.__class__(**resp.json())

    def deactivate(self):
        """ Deactivate this resource """
        if not self.actions.get("deactivate"):
            res = self.api.deactivate(self.id)
            return self.__class__(**res) if res else None
        else:
            resp = self.api.request.post(self.actions["deactivate"])
            if resp.ok:
                return self.__class__(**resp.json())

    def pause(self):
        """ Pause this resource """
        if not self.actions.get("pause"):
            res = self.api.pause(self.id)
            return self.__class__(**res) if res else None
        else:
            resp = self.api.request.post(self.actions["pause"])
            if resp.ok:
                return self.__class__(**resp.json())

    def rollback(self):
        """ Rollback this resource """
        if not self.actions.get("rollback"):
            res = self.api.rollback(self.id)
            return self.__class__(**res) if res else None
        else:
            resp = self.api.request.post(self.actions["rollback"])
            if resp.ok:
                return self.__class__(**resp.json())

    def upgrade(self, upgradeStrategy):
        """ Upgrade this resource """
        if not self.actions.get("upgrade"):
            res = self.api.upgrade(self.id, upgradeStrategy=upgradeStrategy)
            return self.__class__(**res) if res else None
        else:
            resp = self.api.request.post(self.actions["upgrade"], json=upgradeStrategy)
            if resp.ok:
                return self.__class__(**resp.json())