from typing import Generic, TypeVar, Optional, List, Dict
from pydantic import BaseModel
from pydantic.generics import GenericModel
from pathlib import Path


class RouterModel(BaseModel):
    id: str
    entryPoints: List[str] = ["default-headers"]
    rule: str
    middlewares: List[str]
    tls: dict = {}
    service: str


class LoadBalancerModel(BaseModel):
    servers: List[dict] = [{"url": ""}]
    passHostHeader: bool = False


class ServiceModel(BaseModel):
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


class DomainAttributesModel(BaseModel):
    router: RouterModel = None
    service: ServiceModel = None
    endpoint: str
    server: str


AttributesModelType = TypeVar('AttributesModelType')


class ResourceModel(GenericModel, Generic[AttributesModelType]):
    id: str
    type: str                   
    attributes: AttributesModelType   # an attributes object representing some of the resource’s data.
    meta: Dict[str, str] = {}


class ResponseErrorModel(BaseModel):
    id: str                    # a unique identifier for this particular occurrence of the problem.
    status: str = ""           # the HTTP status code applicable to this problem, expressed as a string value.
    code: str = ""             # an application-specific error code, expressed as a string value.
    title: str = ""            # a short, human-readable summary of the problem that SHOULD NOT change from occurrence to occurrence of the problem.
    detail: str = ""           # a human-readable explanation specific to this occurrence of the problem.
    meta: Dict[str, str] = {}  # a meta object containing non-standard meta-information about the error.


class ResponseModel(BaseModel):
    data: Optional[List[ResourceModel]]
    error: Optional[List[ResponseErrorModel]]
    meta: Optional[Dict[str, str]]


class SystemConfigModel(BaseModel):
    yml_path: Path
    fqdn: str = "example.com"
    domains: List[ResourceModel] = []
