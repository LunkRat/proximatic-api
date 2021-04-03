from typing import List, Dict
from pydantic import BaseModel
from pathlib import Path

class RouterModel(BaseModel):
    id: str
    entryPoints: List[str] = ["default-headers"]
    rule: str
    middlewares: List[str]
    tls: dict = {}
    service_id: str

class LoadBalancerModel(BaseModel):
    servers: List[dict] = [{"url": ""}]
    passHostHeader: bool = False

class ServiceModel(BaseModel):
    id: str
    loadBalancer: LoadBalancerModel

class MiddleWaresModel(BaseModel):
    middlewares: dict = {
      "default-headers": {
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

class DomainModel(BaseModel):
    id: str = None
    routers: List[RouterModel] = []
    services: List[ServiceModel] = []


class SystemConfigModel(BaseModel):
    yml_path: Path
    fqdn: str = "example.com"
    domains: List[DomainModel] = []

class AttributesModel(BaseModel):
    endpoint: str
    server: str


class ResourceModel(BaseModel):
    id: str
    type: str                   
    attributes: AttributesModel   # an attributes object representing some of the resource’s data.
    meta: Dict[str, str] = {}


class ErrorsModel(BaseModel):
    id: str                    # a unique identifier for this particular occurrence of the problem.
    status: str = ""           # the HTTP status code applicable to this problem, expressed as a string value.
    code: str = ""             # an application-specific error code, expressed as a string value.
    title: str = ""           # a short, human-readable summary of the problem that SHOULD NOT change from occurrence to occurrence of the problem.
    detail: str = ""           # a human-readable explanation specific to this occurrence of the problem.
    meta: Dict[str, str] = {}   # a meta object containing non-standard meta-information about the error.


class ResponseModel(BaseModel):
    data: List[ResourceModel] = []
    errors: ErrorsModel = []
    meta: Dict[str, str] = {}
