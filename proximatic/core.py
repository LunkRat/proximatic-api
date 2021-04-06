import os
import yaml
import requests
from typing import List
from pathlib import Path
from .models import (
    SystemConfigModel,
    ProviderAttributesModel,
    ResponseModel,
    ResponseErrorModel,
    ResourceModel,
    RouterModel,
    ServiceModel,
    LoadBalancerModel,
    ProviderExportModel,
)


class Proximatic:
    """The proximatic core engine."""

    def __init__(self, yml_path: str = None, fqdn: str = None):
        """Bootstraps the Proximatic object with fqdn string and path to .yml files."""
        if yml_path:
            yml_path = yml_path
        elif os.getenv("PROXIMATIC_YML_PATH"):
            yml_path = os.getenv("PROXIMATIC_YML_PATH")
        else:
            yml_path = "./data"
        yml_path = Path(yml_path)
        if yml_path.exists() and yml_path.is_dir():
            if fqdn:
                fqdn = fqdn
            elif os.getenv("PROXIMATIC_FQDN"):
                fqdn = os.getenv("PROXIMATIC_FQDN")
            else:
                fqdn = "localhost"
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
                    # Create middlewares declaration as dictionary:
                    middlewares = {}
                    for name, configuration in config["http"]["middlewares"].items():
                        middlewares[name] = configuration
                    # Create our provider attributes instance from our model
                    # and attach our data.
                    attributes = ProviderAttributesModel(
                        router=router,
                        service=service,
                        middlewares=middlewares,
                        endpoint=router.rule.split("`")[1],
                        server=service.loadBalancer.servers[0]["url"],
                    )

                    provider = ResourceModel(
                        id=router_id, type="provider", attributes=attributes
                    )

                    self.system.providers.append(provider)
        return self.system

    def set_fqdn(self, fqdn: str):
        self.system.fqdn = fqdn
        # @todo Decide if this should also rewrite the fqdn in all yml?

    def get_fqdn(self):
        return self.system.fqdn

    def provider_list(self, id: str = None) -> ResponseModel:
        """
        Returns a ResponseModel containing all Provider resources
        discovered in the active config.
        """
        response = ResponseModel()
        resources = []
        if id:
            providers = [provider for provider in self.system.providers if provider.id == id]
        else:
            providers = self.system.providers
        try:
            for provider in providers:
                resources.append(provider)
            response.data = resources
        except Exception as e:
            response.error = [ResponseErrorModel(id="changeme", detail=str(e))]
        return response

    def provider_fetch(self, id: str) -> List[ResourceModel]:
        self.load_config()
        return next((item for item in self.system.providers if item.id == id), None)

    def provider_export(self, provider: ResourceModel) -> ResponseModel:
        """File dump function that takes a provider resource model instance and writes it
        to a proxy configuration .yml file.
        """

        response = ResponseModel()
        if provider.type != "provider":
            error = ResponseErrorModel(
                id="Invalid type.", detail="We need a better error system."
            )
            response.error.append(error)
            return response
        export = ProviderExportModel()
        export.http["routers"][provider.id] = provider.attributes.router.dict(
            exclude={"id"}
        )
        export.http["services"][provider.id] = provider.attributes.service.dict()
        export.http["middlewares"] = provider.attributes.middlewares
        file_path = self.system.yml_path.joinpath(provider.id + ".yml")
        with open(file_path, "wt") as yml_stream:
            yaml.dump(export.dict(), yml_stream)
        return ResponseModel()

    def provider_create(self, id: str, server: str) -> ResponseModel:
        response = ResponseModel()
        fetched_provider = self.provider_fetch(id)
        if fetched_provider:
            response.error = [
                ResponseErrorModel(id="changeme", detail="Provider already exists.")
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
        service = ServiceModel(
            loadBalancer=LoadBalancerModel(servers=[{"url": server}])
        )
        # Set the default headers middleware for this provider.
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
        router = RouterModel(
            id=id,
            rule=f"Host(`{endpoint}`)",
            service=id,
            middlewares = [f"{id}-headers"]
        )
        attributes = ProviderAttributesModel(
            router=router,
            middlewares=middlewares,
            service=service,
            endpoint=endpoint,
            server=server,
        )
        provider = ResourceModel(id=id, type="provider", attributes=attributes)
        self.provider_export(provider)
        self.load_config()
        fetched_provider = self.provider_fetch(id)
        if fetched_provider:
            response.data = [provider]
        else:
            response.error = [
                ResponseErrorModel(id="changeme", detail="Provider not created.")
            ]
        return response

    def provider_delete(self, id: str) -> ResponseModel:
        provider = self.provider_fetch(id)
        if provider and provider.id == id:
            files = self.system.yml_path.rglob(f"{provider.id}.yml")
            for path in files:
                path.unlink()
            return ResponseModel(meta={"result": "deleted"})
        else:
            return ResponseModel(meta={"result": "not found"})
