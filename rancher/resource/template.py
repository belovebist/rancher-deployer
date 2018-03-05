"""
Collection of all the templates for creating, updating and upgrading resources
"""
import copy

__upgradeTemplate = {

}

__createTemplates = {
    "stack": {
        "type": "stack",
        "startOnCreate": True,
        # "name": "template",
        "group": None
        # "description": "This is a stack template"
        # "environment": {},
        # "outputs": {},
        # "previousEnvironment": {},
        # "externalId": None,
        # "previousExternalId": None,
        # "dockerCompose": None,
        # "rancherCompose": None
    },
    "service": {
        # "name": "servicetemplate",
        # "description": "Service Template",
        "scale": 1,
        "scalePolicy": {
            "increment": 1,
            "max": 1,
            "min": 1
        },
        "startOnCreate": True,
        "launchConfig": {
            "accountId": None,
            "privileged": False,
            "image": "alpine:latest",
            "startOnCreate": True,
            "networkMode": "managed",
            "labels": {
                "io.rancher.container.pull_image": "always"
            },
            "logConfig": {
                "config": {},
                "driver": "",
                "type": "logConfig"
            },
            # "command": ["--pull"],
            "prePullOnUpgrade": "existing",
            "restartPolicy": {
                "name": "always",
                "type": "restartPolicy"
            },
            "stdinOpen": True,
            "stopSignal": 'SIGTERM',
            "stopTimeout": 10,
            "tty": True,
            "type": 'launchConfig'
            # "kind": "container",
            # "hostname": None,
            # "description": "Container Template",
            # "entrypoint": [],
            # "environment": {},
            # "healthCheck": {},
            # "logConfig": {},
            # "labels": {}
        }
    }
}

def create(name):
    return copy.deepcopy(__createTemplates.get(name))
