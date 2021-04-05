import os
import yaml
import requests
from typing import List
from pathlib import Path
from .models import (
    SystemConfigModel,
    DomainAttributesModel,
    ResponseModel,
    ResponseErrorModel,
    ResourceModel,
    RouterModel,
    ServiceModel,
    LoadBalancerModel,
    DomainExportModel,
)


class Proximatic:
    """The proximatic core engine."""

    def __init__(self, yml_path: str = "/data/traefik/conf", fqdn: str = None):
        """Bootstraps the Proximatic object with fqdn string and path to .yml files."""
        if yml_path:
            yml_path = Path(yml_path)
            if yml_path.exists() and yml_path.is_dir():
                if fqdn:
                    fqdn = fqdn
                elif os.getenv("PROXIMATIC_FQDN"):
                    fqdn = os.getenv("PROXIMATIC_FQDN")
                else:
                    fqdn = "example.com"
                self.system = SystemConfigModel(yml_path=yml_path, fqdn=fqdn)
                self.load_config()
            else:
                raise Exception()

    def load_config(self) -> SystemConfigModel:
        """ETL function that reads all configuration in yml_path and loads resources into Proximatic()."""

        files = self.system.yml_path.glob("**/*.yml")
        for filename in files:
            with open(filename, "r") as yml_stream:
                # Load our yml file as dict.
                config = yaml.safe_load(yml_stream)
                # Extract the values into pydantic models.
                if "http" in config and "services" in config["http"]:
                    router_id = list(config["http"]["routers"].keys())[0]
                    # We want the service that the router references.
                    service_id = config["http"]["routers"][router_id]["service"]
                    # Create our load balancer instance from our model.
                    loadbalancer = LoadBalancerModel(
                        servers=config["http"]["services"][service_id]["loadBalancer"][
                            "servers"
                        ]
                    )
                    # Create our service instance from our model and attach our loadbalancer.
                    service = ServiceModel(id=service_id, loadBalancer=loadbalancer)
                    # Create our router instance from our model.
                    router = RouterModel(
                        id=router_id,
                        entryPoints=config["http"]["routers"][router_id]["entryPoints"],
                        rule=config["http"]["routers"][router_id]["rule"],
                        middlewares=config["http"]["routers"][router_id]["middlewares"],
                        service=service_id,
                    )
                    # Create middleware instances from our model:
                    middlewares = {}
                    for name, configuration in config["http"]["middlewares"].items():
                        middlewares[name] = configuration
                    # Create our domain attributes instance from our model
                    # and attach our data.
                    attributes = DomainAttributesModel(
                        router=router,
                        service=service,
                        middlewares=middlewares,
                        endpoint=router.rule.split("`")[1],
                        server=service.loadBalancer.servers[0]["url"],
                    )

                    domain = ResourceModel(
                        id=router_id, type="domain", attributes=attributes
                    )

                    self.system.domains.append(domain)
        return self.system

    def set_fqdn(self, fqdn: str):
        self.system.fqdn = fqdn
        # @todo Decide if this should also rewrite the fqdn in all yml?

    def get_fqdn(self):
        return self.system.fqdn

    def domain_list(self, id: str = None) -> ResponseModel:
        """
        Returns a ResponseModel containing all Domain resources
        discovered in the active config.
        """
        response = ResponseModel()
        resources = []
        if id:
            domains = [domain for domain in self.system.domains if domain.id == id]
        else:
            domains = self.system.domains
        try:
            for domain in domains:
                resources.append(domain)
            response.data = resources
        except Exception as e:
            response.error = [ResponseErrorModel(id="changeme", detail=str(e))]
        return response

    def domain_fetch(self, id: str) -> List[ResourceModel]:
        self.load_config()
        return next((item for item in self.system.domains if item.id == id), None)

    def domain_export(self, domain: ResourceModel) -> ResponseModel:
        """File dump function that takes a domain resource model instance and writes it
        to a proxy configuration .yml file.
        """

        response = ResponseModel()
        if domain.type != "domain":
            error = ResponseErrorModel(
                id="Invalid type.", detail="We need a better error system."
            )
            response.error.append(error)
            return response
        export = DomainExportModel()
        export.http["routers"][domain.id] = domain.attributes.router.dict(
            exclude={"id"}
        )
        export.http["services"][domain.id] = domain.attributes.service.dict()
        export.http["middlewares"] = domain.attributes.middlewares
        file_path = self.system.yml_path.joinpath(domain.id + ".yml")
        with open(file_path, "wt") as yml_stream:
            yaml.dump(export.dict(), yml_stream)
        return ResponseModel()

    def domain_create(self, id: str, server: str) -> ResponseModel:
        response = ResponseModel()
        fetched_domain = self.domain_fetch(id)
        if fetched_domain:
            response.error = [
                ResponseErrorModel(id="changeme", detail="Domain already exists.")
            ]
            return response
        # Check the URL for validity by visiting it and
        # expecting a 200 response code from its server.
        try:
            result = requests.get(server).status_code
            if result != 200:
                response.error = [
                    ResponseErrorModel(
                        id="changeme", detail="server URL not reachable."
                    )
                ]
                return response
        except Exception as e:
            response.error = [ResponseErrorModel(id="changeme", detail=str(e))]
            return response
        endpoint = f"{id}.{self.system.fqdn}"
        router = RouterModel(
            id=id,
            rule=f"Host(`{endpoint}`)",
            service=id,
        )
        service = ServiceModel(
            loadBalancer=LoadBalancerModel(servers=[{"url": server}])
        )
        # Set the default headers middleware for this domain.
        middlewares = {
            f"{id}-headers": {
                "headers": {
                    "frameDeny": True,
                    "sslRedirect": True,
                    "browserXssFilter": True,
                    "contentTypeNosniff": True,
                    "forceSTSHeader": True,
                    "stsIncludeSubdomains": True,
                    "stsPreload": True,
                }
            }
        }
        attributes = DomainAttributesModel(
            router=router,
            middlewares=middlewares,
            service=service,
            endpoint=endpoint,
            server=server,
        )
        domain = ResourceModel(id=id, type="domain", attributes=attributes)
        self.domain_export(domain)
        self.load_config()
        fetched_domain = self.domain_fetch(id)
        if fetched_domain:
            response.data = [domain]
        else:
            response.error = [
                ResponseErrorModel(id="changeme", detail="Domain not created.")
            ]
        return response

    def domain_delete(self, id: str) -> ResponseModel:
        domain = self.domain_fetch(id)
        if domain and domain.id == id:
            files = self.system.yml_path.rglob(f"{domain.id}.yml")
            for path in files:
                path.unlink()
            return ResponseModel(meta={"result": "deleted"})
        else:
            return ResponseModel(meta={"result": "not found"})
