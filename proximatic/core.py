import os
import yaml
import requests
from pathlib import Path
from jinja2 import Environment, PackageLoader
from tabulate import tabulate
from .models import (SystemConfigModel, DomainAttributesModel, ResponseModel,
                    ResponseErrorModel, ResourceModel, RouterModel, ServiceModel,
                    MiddleWaresModel, LoadBalancerModel, DomainExportModel)

class Proximatic:
    """The proximatic core engine."""

    def __init__(
        self, yml_path: str = '/data/traefik/conf', fqdn: str = None
    ):
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
        files = self.system.yml_path.glob('**/*.yml')
        for filename in files:
            with open(filename, "r") as yml_stream:
                config = yaml.safe_load(yml_stream)
                if 'http' in config and 'services' in config['http']:
                    router_id = list(config['http']['routers'].keys())[0]
                    service_id = config['http']['routers'][router_id]['service']

                    loadbalancer = LoadBalancerModel(
                            servers = config['http']['services'][service_id]['loadBalancer']['servers']
                        )

                    service = ServiceModel(
                        id=service_id,
                        loadBalancer=loadbalancer
                        )

                    router = RouterModel(
                            id=router_id,
                            entryPoints=config['http']['routers'][router_id]['entryPoints'],
                            rule=config['http']['routers'][router_id]['rule'],
                            middlewares=config['http']['routers'][router_id]['middlewares'],
                            service=service_id
                            )

                    attributes = DomainAttributesModel(
                        router=router,
                        service=service,
                        endpoint=router.rule.split("`")[1],
                        server=service.loadBalancer.servers[0]['url']
                    )
                    
                    domain = ResourceModel(
                        id=router_id,
                        type="domain",
                        attributes=attributes
                    )

                    self.system.domains.append(domain)
        return self.system

    def set_fqdn(self, fqdn: str):
        self.system.fqdn = fqdn
        # @todo Decide if this should also rewrite the fqdn in all yml?

    def get_fqdn(self):
        return self.system.fqdn

    def domain_list(self, id: str=None) -> ResponseModel:
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

    def domain_fetch(self, id: str) -> ResourceModel:
        fetch = [domain for domain in self.system.domains if domain.id == id]
        domain = fetch[0]
        return domain

    def domain_export(self, domain: ResourceModel) -> ResponseModel:
        response = ResponseModel()
        if domain.type != "domain":
            error = ResponseErrorModel(
                id="Invalid type.",
                detail="We need a better error system."
            )
            response.error.append(error)
            return response
        file_path = self.system.yml_path.joinpath(domain.id + ".yml")
        export = DomainExportModel()
        export.http['routers'][domain.id] = domain.attributes.router
        export.http['services'][domain.id] = domain.attributes.service
        with open(file_path, "wt") as fh:
            yaml.dump(export.dict(), fh)
        return ResponseModel()
