from rancher.utils.request import Request


class API:
    """
    This class includes all the basic methods like fetching resources, adding resource, removing resource and
    fallback functions for various actions such as activate, deactivate, update, upgrade, etc.
    """
    def __init__(self, url, auth=None):
        self._auth    = auth
        self._headers = {"Content-Type": "application/json", "Accept": "application/json"}
        self.request  = Request(auth=self._auth, headers=self._headers)
        self.url      = url

    def _filterNoneValuedArgs(self, kwargs):
        """ Filters out the invalid arguments """
        return dict(filter(lambda kwarg: kwarg[1] is not None, kwargs.items()))

    def get(self, **kwargs):
        params = self._filterNoneValuedArgs(kwargs)
        data = []
        if "id" in params:
            query = "/{}".format(params["id"])
            resp = self.request.get("{}{}".format(self.url, query))
            if resp.ok:
                data = [resp.json()]
        else:
            resp = self.request.get(self.request.encode(self.url, **params))
            if resp.ok:
                data = resp.json()["data"]

        # Filter the results to return only those matching the initial parameters in kwargs
        data = filter(
            lambda d: all(
                map(lambda key: kwargs[key] == d.get(key),
                    kwargs)),
            data)
        data = list(data)
        return data

    def getOne(self, **kwargs):
        data = self.get(**kwargs)
        return data[0] if data else None

    def add(self, template):
        """ Add new resource based on the template """
        resp = self.request.post(self.url, json=template)
        if resp.ok:
            return resp.json()

    def remove(self, id):
        """ Remove a resource based on it's id """
        query = "/{}".format(id)
        resp = self.request.delete("{}{}".format(self.url, query))
        if resp.ok:
            return resp.json()

    def update(self, id, updateStrategy):
        """ Update a resource based on it's id """
        query = "/{}".format(id)
        resp = self.request.put("{}{}".format(self.url, query), json=updateStrategy)
        if resp.ok:
            return resp.json()

    def activate(self, id):
        """ Activate a resource based on it's id """
        query = "/{}?{}".format(id, "action=activate")
        resp = self.request.post("{}{}".format(self.url, query))
        if resp.ok:
            return resp.json()

    def deactivate(self, id):
        """ Deactivate a resource based on it's id """
        query = "/{}?{}".format(id, "action=deactivate")
        resp = self.request.post("{}{}".format(self.url, query))
        if resp.ok:
            return resp.json()

    def pause(self, id):
        """ Pause a resource based on it's id """
        query = "/{}?{}".format(id, "action=pause")
        resp = self.request.post("{}{}".format(self.url, query))
        if resp.ok:
            return resp.json()

    def restart(self, id):
        """ Restart a resource based on it's id """
        query = "/{}?{}".format(id, "action=restart")
        resp = self.request.post("{}{}".format(self.url, query))
        if resp.ok:
            return resp.json()

    def rollback(self, id):
        """ Rollback a resource based on it's id """
        query = "/{}?{}".format(id, "action=rollback")
        resp = self.request.post("{}{}".format(self.url, query))
        if resp.ok:
            return resp.json()

    def upgrade(self, id, upgradeStrategy):
        """ Upgrade a resource based on it's id """
        query = "/{}?{}".format(id, "action=upgrade")
        resp = self.request.post("{}{}".format(self.url, query), json=upgradeStrategy)
        if resp.ok:
            return resp.json()


if __name__ == "__main__":
    pass