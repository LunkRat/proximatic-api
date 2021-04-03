import os
import yaml
import requests
from pathlib import Path
from jinja2 import Environment, PackageLoader
from tabulate import tabulate
from .models import (SystemConfigModel, DomainModel, ResponseModel, AttributesModel, 
                    ErrorsModel, ResourceModel, RouterModel, ServiceModel,
                    MiddleWaresModel, LoadBalancerModel)

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
                    domain = DomainModel()
                    for service, settings in config['http']['services'].items():
                        domain.id = service
                        loadbalancer = LoadBalancerModel(
                            servers = settings['loadBalancer']['servers']
                        )
                        service = ServiceModel(
                            id=service,
                            loadBalancer=loadbalancer
                            )
                        domain.services.append(service)
                    for router, settings in config['http']['routers'].items():
                        router = RouterModel(
                            id=router,
                            entryPoints=settings['entryPoints'],
                            rule=settings['rule'],
                            middlewares=settings['middlewares'],
                            service_id=settings['service']
                            )
                        domain.routers.append(router)
                    self.system.domains.append(domain)
        return self.system

    def set_fqdn(self, fqdn: str):
        self.system.fqdn = fqdn
        # @todo Decide if this should also rewrite the fqdn in all yml?

    def get_fqdn(self):
        return self.system.fqdn

    def domain_list(self, id: str=None) -> ResponseModel:
        """
        Searches the config yml directory and returns a ResponseModel
        containing all Domain resources discovered in the files.
        """
        response = ResponseModel()
        resources = []
        if id:
            domains = [domain for domain in self.system.domains if domain.id == id]
        else:
            domains = self.system.domains
        try:
            for domain in domains:
                attributes = AttributesModel(
                    endpoint=domain.routers[0].rule.split("`")[1],
                    server=domain.services[0].loadBalancer.servers[0]['url']
                    )
                resource = ResourceModel(
                    id=domain.id,
                    type='domain',
                    attributes=attributes
                    )
                resources.append(resource)
            response.data = resources
        except Exception as e:
            response.errors = ErrorsModel(id="changeme", detail=e)
        return response



    def domain_add(self, id: str, server: str):

        pass
        # Check the URL for validity by visiting it and
        # expecting a 200 response code from its server.
        # try:
        #     result = requests.get(server).status_code
        #     if result != 200:
        #         return {
        #             "Error": "Invalid URL"
        #         }  # @todo define some reusable error response payloads.
        # except Exception as e:
        #     return {"error": "Invalid URL", "msg": str(e)}

        # # Load Jinja2 template engine.
        # env = Environment(loader=PackageLoader("proximatic", "templates"))
        # template = env.get_template("domain.j2.yml")
        # # Use template to generate a string of YAML containing valid Traefik config.
        # yml_string = template.render(
        #     id=id,
        #     fqdn=self.system.fqdn,
        #     server=server,
        # )
        # # Write the YAML to a .yml file named after the id.
        # yml_file_path = self.system.yml_path + id + ".yml"
        # yml_file = open(yml_file_path, "wt")
        # lines_written = yml_file.write(yml_string)
        # yml_file.close()
        
        # return response
        