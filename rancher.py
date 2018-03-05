#!/usr/bin/env python3
import logging
from rancher.rancher_api import RancherAPI
import pprint
import click
import os, sys, re
os.environ["LANG"] = os.environ["LC_ALL"] = "en_US.UTF-8"


log = logging.getLogger(__name__)


def filterParameters(params):
    """ Filters out all the empty parameters """
    return dict(filter(lambda param: param[1] is not None, params.items()))


class Rancher:
    def _rancher(ctx, **params):
        logging.basicConfig(
            level=getattr(logging, params.pop("log_level")),
            format="%(asctime)s [%(levelname)s]: %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        params = dict(
            rancherUrl=params.get("url"),
            apiVersion=params.get("api_version"),
            accessKey=params.get("access_key"),
            secretKey=params.get("secret_key")
        )

        ctx.obj["rancherParams"] = params
        global api
        api = RancherAPI(**params)

    @click.group()
    @click.option("--url", envvar="RANCHER_URL", help="Rancher URL")
    @click.option("--api-version", envvar="RANCHER_API_VERSION", help="Rancher API Version")
    @click.option("--project", envvar="RANCHER_ENVIRONMENT", help="Rancher project name")
    @click.option("--access-key", envvar="RANCHER_ACCESS_KEY", help="Rancher Project access key")
    @click.option("--secret-key", envvar="RANCHER_SECRET_KEY", help="Rancher Project secret key")
    # Set log level
    @click.option("--log-debug", "log_level", flag_value="DEBUG", help="Set log-level to DEBUG")
    @click.option("--log-info", "log_level", flag_value="INFO", help="Set log-level to INFO")
    @click.option("--log-warn", "log_level", flag_value="WARN", default=True, help="Set log-level to WARN")
    # Pass the context to store global parameters
    @click.pass_context
    def rancher(ctx, **params):
        # Validate the parameters
        if params.get("url") is None:
            log.error("Must either provide --url or set RANCHER_URL environment variable to rancher host")
            ctx.abort()
        if params.get("api_version") is None:
            log.error("Must either provide --api-version or set RANCHER_API_VERSION environment variable to rancher api version")
            ctx.abort()
        if params.get("access_key") is None:
            log.error("Must either provide --access-key or set RANCHER_ACCESS_KEY environment variable to rancher access key")
            ctx.abort()
        if params.get("secret_key") is None:
            log.error("Must either provide --access-key or set RANCHER_SECRET_KEY environment variable to rancher secret key")
            ctx.abort()

        Rancher._rancher(ctx, **params)


class Cluster:

    @Rancher.rancher.group()
    @click.option("--name", help="Cluster name")
    @click.pass_context
    def cluster(ctx, **params):
        """ Command to monitor and manage cluster """
        Cluster._cluster(ctx, **params)

    def _cluster(ctx, **params):
        params = filterParameters(params)
        ctx.obj["clusterParams"] = params
        ctx.obj["cluster"] = api.cluster(**params)

    @cluster.command()
    @click.option("--detail", is_flag=True, help="Show detailed info")
    @click.pass_context
    def get(ctx, **params):
        """ Get the clusters that match given parameters """
        Cluster._get(ctx, **params)

    def _get(ctx, **params):
        if ctx.obj.get("clusterParams").get("name"):
            cluster = ctx.obj.get("cluster")
            if cluster:
                info = cluster._info if params.get("detail") else {"name": cluster.name, "id": cluster.id}
                pprint.pprint(info)
        else:
            clusters = api.clusters()
            if clusters:
                info = list(map(
                    lambda cluster: cluster._info if params.get("detail") else {"id": cluster.id, "name": cluster.name},
                    clusters))
                pprint.pprint(info)


class Service:

    @Rancher.rancher.group()
    @click.option("--cluster", help="Cluster where the service resides")
    @click.option("--project", help="Project where the service resides")
    @click.option("--stack", help="Stack where the service resides")
    @click.option("--name", help="Service for update/upgrade")
    @click.pass_context
    def service(ctx, **params):
        Service._service(ctx, **params)

    def _service(ctx, **params):
        params = filterParameters(params)
        ctx.obj["serviceParams"] = params
        if params.get("project"):
            project = api.project(name=params.get("project"))
            ctx.obj["project"] = project
            if project and params.get("stack"):
                stack = project.getStack(name=params.get("stack"))
                ctx.obj["stack"] = stack
                if stack and params.get("name"):
                    service = stack.getService(name=params.get("name"))
                    ctx.obj["service"] = service


    @service.command()
    @click.option("--detail", is_flag=True, help="Get one of the matching results")
    @click.pass_context
    def get(ctx, **params):
        """ Get the services that match given parameters """
        Service._get(ctx, **params)

    def _get(ctx, **params):
        if ctx.obj.get("serviceParams").get("name"):
            service = ctx.obj.get("service")

            if service:
                info = service._info if params.get("detail") else {"id": service.id,
                                                                   "name": service.name,
                                                                   "stack": service.stackId,
                                                                   "env": service.accountId,
                                                                   "cluster": service.clusterId,
                                                                   "resClass": service.__class__}
                pprint.pprint(info)
        else:
            if ctx.obj.get("serviceParams").get("stack"):
                stack = ctx.obj.get("stack")
                if not stack:
                    log.error("No such stack {}!".format(ctx.obj.get("serviceParams").get("stack")))
                    ctx.abort()
                services = stack.getServices()
            elif ctx.obj.get("serviceParams").get("project"):
                project = ctx.obj.get("project")
                if not project:
                    log.error("No such project {}!".format(ctx.obj.get("serviceParams").get("stack")))
                    ctx.abort()
                services = project.getServices()
            else:
                services = api.services()

            if services:
                info = list(map(
                    lambda service: service._info if params.get("detail") else {"id": service.id,
                                                                                "name": service.name,
                                                                                "stack": service.stackId,
                                                                                "env": service.accountId,
                                                                                "cluster": service.clusterId,
                                                                                "resClass": service.__class__},
                    services))
                pprint.pprint(info)

    @service.command()
    @click.option("--name", required=True, help="Name of the service to create")
    @click.option("--image", required=True, help="Image to use for the service containers")
#    @click.option("--scale", default=1, help="Initial scale of the service")
    @click.option("--timeout", default=180, type=click.IntRange(5, 1000), help="Timeout for the create job")
    @click.option("--rollback-on-timeout", is_flag=True,
                  help="Rollback if create is not finished within given timeout")
    # launchConfig parameters
    @click.option("--label", "-l", multiple=True, help="Service Labels")
    @click.option("--volume", "-v", multiple=True, help="Volume path to mount from host to container")
    @click.option("--environment", "-e", multiple=True, help="Environment variables")
    @click.pass_context
    def create(ctx, **params):
        """ Create a new service """
        Service._create(ctx, **params)

    def _create(ctx, **params):
        project_name = ctx.obj.get("serviceParams").get("project")
        if project_name is None:
            log.error("Service requires --project to deploy on!")
            ctx.abort()
        project = ctx.obj.get("project")
        if project is None:
            log.error("Project {} does not exist. Aborting!".format(project_name))
            ctx.abort()

        stack_name = ctx.obj.get("serviceParams").get("stack")
        if project_name is None:
            log.error("Service requires --stack to deploy on!")
            ctx.abort()
        stack = ctx.obj.get("stack")
        if stack is None:
            log.error("Stack {} does not exist. Aborting!".format(stack_name))
            ctx.abort()

        timeout = params.get("timeout")
        rollbackOnTimeout = params.get("rollback_on_timeout")

        launchConfig = dict()
        launchConfig["image"] = params.get("image")
        launchConfig["dataVolumes"] = params.get("volume") or None
        launchConfig["labels"] = Service._getLabels(params.get("label")) or None
        launchConfig["environment"] = Service._getEnvVariables(params.get("environment")) or None

        createParams = {
            "name": params.get("name"),
            "launchConfig": launchConfig
        }

        service = stack.addService(createParams, timeout=timeout, rollback=rollbackOnTimeout)
        if service:
            log.warning("Service {}/{} created successfully.".format(stack_name, service.name))
        else:
            log.error("Cannot create service {}. Service already exists!".format(params.get("name")))
            ctx.abort()

        return service


    @service.command()
    @click.pass_context
    def remove(ctx):
        """ Remove existing service """
        Service._remove(ctx)

    def _remove(ctx):
        if not ctx.obj.get("serviceParams").get("name"):
            log.error("Must provide a service --name to remove!")
            ctx.abort()
        service = ctx.obj.get("service")
        if not service:
            log.error("Service with spec 'project={},stack={},name={}' does not exist!"
                      .format(ctx.obj.get("serviceParams").get("project"),
                              ctx.obj.get("serviceParams").get("stack"),
                              ctx.obj.get("serviceParams").get("name")))
            ctx.abort()
        service.remove(timeout=60)


    @service.command()
    # These are all the update parameters
    @click.option("--name", required=False, help="Name to update with")
    @click.option("--description", required=False, help="Description to update with")
    # @click.option("--lbconfig", required=False, help="Load Balancer config")
    # @click.option("--metadata", required=False, help="Metadata to update with")
    @click.option("--scale", required=False, help="Scale to update with")
    @click.option("--scalepolicy", required=False, help="Scale Policy (json) to update the old service with")
    @click.option("--selectorcontainer", required=False, help="Selector Container to update the old service with")
    @click.option("--selectorlink", required=False, help="Selector Link to update the old service with")
    @click.option("--timeout", default=180, type=click.IntRange(5, 1000), help="Timeout for the update job")
    @click.pass_context
    def update(ctx, **params):
        """ Update existing service """
        Service._update(ctx, **params)

    def _update(ctx, **params):
        params = {
            "name": params.get("name"),
            "description": params.get("description"),
            "metadata": params.get("metadata"),
            "scale": params.get("scale"),
            "lbConfig": params.get("lbconfig"),
            "scalePolicy": params.get("scalepolicy"),
            "selectorContainer": params.get("selectorcontainer"),
            "selectorLink": params.get("selectorlink")
        }
        params = filterParameters(params)

        if not ctx.obj.get("serviceParams").get("name"):
            log.error("Must provide a service --name to update!")
            ctx.abort()
        service = ctx.obj.get("service")
        if not service:
            log.error("Service with spec 'project={},stack={},name={}' does not exist!"
                      .format(ctx.obj.get("serviceParams").get("project"),
                              ctx.obj.get("serviceParams").get("stack"),
                              ctx.obj.get("serviceParams").get("name")))
            ctx.abort()

        service.update(params, timeout=params.get("timeout"))


    @service.command(context_settings=dict(token_normalize_func=lambda x: x))
    @click.option("--batchsize", default=1, type=click.IntRange(1, 5), help="Size of batch of containers to upgrade")
    @click.option("--intervalmillis", default=2000, help="Interval Millis")
    @click.option("--startfirst", is_flag=True, help="Start the new container before removing old one; "
                                                     "Should not be used if the container use conflicting resources like host ports")
    @click.option("--timeout", default=180, type=click.IntRange(5, 1000), help="Timeout for the upgrade job")
    @click.option("--rollback-on-timeout", is_flag=True, help="Rollback if upgrade is not finished within given timeout")
    @click.option("--create", is_flag=True, help="Create the service if it does not exist")
    # launchConfig parameters
    @click.option("--image", help="Image to upgrade the service with")
    @click.option("--label", "-l", multiple=True, help="Service Labels")
    @click.option("--volume", "-v", multiple=True, help="Volume path to mount from host to container")
    @click.option("--environment", "-e", multiple=True, help="Environment variables")
    # @click.option("--privileged", is_flag=True, help="Run the service containers in privileged mode")
    @click.pass_context
    def upgrade(ctx, **params):
        Service._upgrade(ctx, **params)

    def _getEnvVariables(envVars):
        if not envVars:
            return None
        try:
            envVars = dict(map(lambda e: e.split("=", 1), envVars))
        except:
            log.error("Environment variables should be provided as VARIABLE_NAME=value. But given is {}.".format(envVars))
            sys.exit(1)
        return envVars

    def _getLabels(labels):
        defaultLabels = {
            "io.rancher.container.pull_image": "always"
        }
        if not labels:
            return defaultLabels

        try:
            labels = dict(map(lambda l: l.split("=", 1), labels))
        except:
            log.error("Labels should be provided as lable_name=value. But given is {}.".format(labels))
            sys.exit(1)

        keyMap = {
            "pull_image": "io.rancher.container.pull_image",
            "host_label": "io.rancher.scheduler.affinity:host_label"
        }
        labels = dict(filter(lambda l: l[0] in keyMap, labels.items()))

        labels = dict(map(lambda i: (keyMap[i[0]], i[1]), labels.items()))
        defaultLabels.update(labels)
        return defaultLabels


    def _upgrade(ctx, **params):
        params = filterParameters(params)

        serviceName = ctx.obj.get("serviceParams").get("name")
        if not serviceName:
            log.error("Must provide a service --name to upgrade!")
            ctx.abort()

        service = ctx.obj.get("service")

        if not service:
            if params.get("create"):
                log.info("Service with spec 'project={},stack={},name={}' does not exist!"
                          .format(ctx.obj.get("serviceParams").get("project"),
                                  ctx.obj.get("serviceParams").get("stack"),
                                  ctx.obj.get("serviceParams").get("name")))
                log.info("Creating service '{}'".format(serviceName))
                service = Service._create(ctx, **dict(name=serviceName, scale=1, image=params.get("image"),
                                                      volume=params.get("volume"), label=params.get("label"),
                                                      environment=params.get("environment")))

            else:
                log.error("Service with spec 'project={},stack={},name={}' does not exist!"
                          .format(ctx.obj.get("serviceParams").get("project"),
                                  ctx.obj.get("serviceParams").get("stack"),
                                  ctx.obj.get("serviceParams").get("name")))
                ctx.abort()
        else:

            # params = filterParameters(params)
            launchConfig = dict()
            launchConfig["image"] = params.get("image")
            launchConfig["dataVolumes"] = params.get("volume") or None
            launchConfig["labels"] = Service._getLabels(params.get("label")) or None
            launchConfig["environment"] = Service._getEnvVariables(params.get("environment")) or None

            inServiceStrategy = {
                "batchSize": params.get("batchsize"),
                "intervalMillis": params.get("intervalmillis"),
                "startFirst": params.get("startfirst"),
                "launchConfig": launchConfig
            }

            # Before we upgrade, pull the image on the hosts in this environment
            try:
                import subprocess
                rancherParams = ctx.obj["rancherParams"]
                serviceParams = ctx.obj["serviceParams"]
                for i in range(10):
                    cmd = ["rancher_cli", "--url", "{rancherUrl}/{apiVersion}".format(**rancherParams),
                           "--env", serviceParams["project"], "--access-key", rancherParams["accessKey"],
                           "--secret-key", rancherParams["secretKey"], "pull", params.get("image")]
                    try:
                        subprocess.check_call(cmd)
                        break
                    except subprocess.CalledProcessError:
                        log.warning("Error while pulling image! Trying again...")
                        continue
                # command = "rancher_cli --url {rancherUrl}/{apiVersion} --env {env} --access-key {accessKey}" \
                #           " --secret-key {secretKey} pull {image}".format(env=ctx.obj["serviceParams"].get("project"),
                #                                 image=params.get("image"), **ctx.obj["rancherParams"])
                # os.system(command)
            except Exception as e:
                log.error("Exception: {}".format(e))

            service.upgrade(inServiceStrategy, timeout=params.get("timeout"), rollback=params.get("rollback_on_timeout"))

        return service

    @service.command()
    @click.pass_context
    def clean(ctx, **params):
        """ Clean the unhealthy containers in the service """
        project_name = ctx.obj.get("serviceParams").get("project")
        if project_name is None:
            log.error("Service requires --project where the service belongs!")
            ctx.abort()
        project = ctx.obj.get("project")
        if project is None:
            log.error("Project {} does not exist. Aborting!".format(project_name))
            ctx.abort()

        stack_name = ctx.obj.get("serviceParams").get("stack")
        if project_name is None:
            log.error("Service requires --stack where the service belongs!")
            ctx.abort()
        stack = ctx.obj.get("stack")
        if stack is None:
            log.error("Stack {} does not exist. Aborting!".format(stack_name))
            ctx.abort()
        service = stack.getService(**params)
        if service is None:
            log.error("Service {} does not exist. Aborting!".format(params.get("name")))
            ctx.abort()
        cleanedService = service.clean(**params)
        if cleanedService:
            log.warning("Service {}/{} updated successfully.".format(stack_name, service.name))
        else:
            log.error("Cannot update service {}!".format(params.get("name")))


class LoadBalancer:
    @Rancher.rancher.group()
    @click.option("--cluster", help="Cluster where the service resides")
    @click.option("--project", help="Project where the service resides")
    @click.option("--stack", help="Stack where the service resides")
    @click.option("--name", help="Service for update/upgrade")
    @click.pass_context
    def loadbalancer(ctx, **params):
        Service._service(ctx, **params)


    @loadbalancer.command()
    @click.option("--hostname", required=True, help="Hostname/Domain-name")
    @click.option("--path", required=True, default="/", help="Path or endpoint address")
    @click.option("--priority", default=1, type=click.INT, help="Priority level")
    @click.option("--protocol", default="http", type=click.Choice(["http", "tcp", "https"]), help="Protocol to use: http/https/tcp")
    @click.option("--service", required=True, help="Name of service to forward the traffic to")
    @click.option("--stack", required=True, help="Name of stack where the service resides")
    @click.option("--sourceport", required=True, type=click.IntRange(50,65535), help="Source port to listen to")
    @click.option("--targetport", required=True, type=click.IntRange(50,65535), help="Destination port to direct the traffic to")
    @click.option("--rewrite", help="Rewrite the path")
    @click.option("--custom", multiple=True, help="A line of custom haproxy config")
    @click.option("--reload", is_flag=True, help="Restart the loadbalancer")
    @click.pass_context
    def updateportrule(ctx, **params):
        lb = ctx.obj.get("service")
        if lb is None:
            log.error("Loadbalancer with spec={} does not exist!".format(ctx.obj.get("serviceParams")))
            ctx.abort()

        if lb.type != "loadBalancerService":
            log.error("Service {} is not a loadBalancerService!".format(lb.name))
            ctx.abort()

        stack = ctx.obj.get("project").getStack(name=params.get("stack"))
        if stack is None:
            log.error("Stack '{}' does not exist in project '{}'".format(params.get("stack"), ctx.obj.get("project").name))
            ctx.abort()

        service = stack.getService(name=params.get("service"))
        if service is None:
            log.error("Service '{}' does not exist in project '{}', stack '{}'".format(params.get("service"),
                                                                                       ctx.obj.get("project").name,
                                                                                       stack.name))
            ctx.abort()

        # backendName = "back_{}_{}_{}_end_{}_{}".format(params.get("sourceport"), service.name, params.get("targetport"),
        #                                                re.sub("[/*.]", "", params.get("hostname")),
        #                                                re.sub("[/*.]", "", params.get("path")))

        portRule = {
            "hostname": params.get("hostname"),
            "path": params.get("path"),
            "priority": params.get("priority"),
            "protocol": params.get("protocol"),
            "serviceId": service.id,
            "sourcePort": params.get("sourceport"),
            "targetPort": params.get("targetport")
        }
        portRule["backendName"] = "{}_{}_{}_{}".format(portRule["sourcePort"], service.name,
                                                       portRule["targetPort"], portRule["protocol"])

        if not LoadBalancer._validatePortRule(portRule):
            ctx.abort()
        lb.updatePortRule(portRule, customConfig=params.get("custom"), timeout=60)
        if params.get("reload"):
            lb.restart()


    @loadbalancer.command()
    @click.option("--hostname", required=True, help="Hostname/Domain-name")
    @click.option("--path", required=True, help="Path or endpoint address")
    @click.option("--sourceport", required=True, type=click.IntRange(50, 65535), help="Source port to listen to")
    @click.option("--targetport", required=True, type=click.IntRange(50, 65535), help="Destination port to direct the traffic to")
    @click.pass_context
    def removeportrule(ctx, **params):
        lb = ctx.obj.get("service")
        if lb is None:
            log.error("Loadbalancer with spec={} does not exist!".format(ctx.obj.get("serviceParams")))
            ctx.abort()

        if lb.type != "loadBalancerService":
            log.error("Service {} is not a loadBalancerService!".format(lb.name))
            ctx.abort()

        portRule = {
            "hostname": params.get("hostname"),
            "path": params.get("path"),
            "sourcePort": params.get("sourceport"),
            "targetPort": params.get("targetport")
        }
        if not LoadBalancer._validatePortRule(portRule):
            ctx.abort()
        lb.removePortRule(portRule, timeout=60)


    def _validatePortRule(portRule):
        hostname = portRule.get("hostname")
        if hostname.strip() == "":
            log.error("Invalid --hostname: '{}'".format(hostname))
            return False

        if ":" in hostname or "/" in hostname:
            log.error("Invalid --hostname: '{}'. "
                      "Hostname should either be "
                      "1. full domain like: sub.mydomain.com "
                      "2. wildcard domain like: *.mydomain.com. "
                      "Name should not contain prefixes like 'http://', 'https://' "
                      "and paths like: /a/index".format(hostname))
            return False
        if not portRule.get("path").startswith("/"):
            log.error("Invalid --path: '{}'".format(portRule.get("path")))
            return False
        return True


if __name__ == "__main__":
    r = Rancher.rancher(obj={})
