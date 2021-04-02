import os
import glob
import yaml
import requests
from jinja2 import Environment, PackageLoader
from tabulate import tabulate

class Proximatic:
    def __init__(
        self, yml_dir: str = "/data/traefik/conf/", proximatic_fqdn: str = None
    ):
        self.yml_dir = yml_dir

        if proximatic_fqdn:
            self.proximatic_fqdn = proximatic_fqdn
        elif os.getenv("PROXIMATIC_FQDN"):
            self.proximatic_fqdn = os.getenv("PROXIMATIC_FQDN")
        else:
            self.proximatic_fqdn = "example.com"

    def set_fqdn(self, fqdn: str):
        self.proximatic_fqdn = fqdn

    def get_fqdn(self):
        return self.proximatic_fqdn

    def domain_list(self):
        response = {"domains": []}
        files = glob.glob(self.yml_dir + "*.yml")
        for filename in files:
            with open(filename, "r") as yml_stream:
                config = yaml.safe_load(yml_stream)
                for service, values in config["http"]["services"].items():
                    response["domains"].append(
                        {service: values["loadBalancer"]["servers"][0]["url"]}
                    )
        return response

    def domain_fetch(self, subdomain: str) -> dict:
        yml_file_path = self.yml_dir + subdomain + ".yml"
        response = {"result": "success"}
        if os.path.exists(yml_file_path):
            with open(yml_file_path, "r") as yml_stream:
                config = yaml.safe_load(yml_stream)
                for service, values in config["http"]["services"].items():
                    response["item"] = {
                        "Name": service,
                        "Entrypoint": f"{service}.{self.proximatic_fqdn}",
                        "URL": values["loadBalancer"]["servers"][0]["url"],
                    }
        else:
            response["result"] = "File not found"
        return response

    def domain_add(self, subdomain: str, url: str):
        # Check the URL for validity by visiting it and
        # expecting a 200 response code from its server.
        try:
            result = requests.get(url).status_code
            if result != 200:
                return {
                    "Error": "Invalid URL"
                }  # @todo define some reusable error response payloads.
        except Exception as e:
            return {"error": "Invalid URL", "msg": str(e)}

        # Load Jinja2 template engine.
        env = Environment(loader=PackageLoader("proximatic", "templates"))
        template = env.get_template("domain.j2.yml")
        # Use template to generate a string of YAML containing valid Traefik config.
        yml_string = template.render(
            subdomain=subdomain,
            proximatic_fqdn=self.proximatic_fqdn,
            url=url,
        )
        # Write the YAML to a .yml file named after the subdomain.
        yml_file_path = self.yml_dir + subdomain + ".yml"
        yml_file = open(yml_file_path, "wt")
        lines_written = yml_file.write(yml_string)
        yml_file.close()
        fetch = self.domain_fetch(subdomain)
        if 'item' in fetch:
            response = {"result": "success", "item": fetch['item']}
        return response

    def domain_delete(self, subdomain: str):
        yml_file_path = self.yml_dir + subdomain + ".yml"
        response = {
            "result": "success",
            "subdomain": subdomain,
        }
        if os.path.exists(yml_file_path):
            os.remove(yml_file_path)
        else:
            response["result"] = "File not found"
        return response
