"""
Utility methods
"""
import collections
from copy import deepcopy

def updateRecursive(d, u):
    if not isinstance(d, collections.Mapping):
        return deepcopy(u)

    r = deepcopy(d)
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r[k] = updateRecursive(r.get(k, {}), v)
        elif isinstance(v, list):
            r[k] = r.get(k, []) + v
        else:
            r[k] = v
    return r





def test():
    import pprint
    d = dict(x=dict(y=2, z=1, k=23))
    u = dict(x=dict(y=1,z=2), p=1, q=dict(r=dict(k=4),d=2))
    pprint.pprint(d)
    pprint.pprint(u)
    pprint.pprint(updateRecursive(d, u))



if __name__ == "__main__":
    test()
