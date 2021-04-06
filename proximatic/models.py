from typing import Generic, TypeVar, Optional, List, Dict
from pydantic import BaseModel
from pydantic.generics import GenericModel
from pathlib import Path


class RouterModel(BaseModel):
    """Models proxy router configs attached to Proximatic() provider resources."""

    id: str
    entryPoints: List[str] = ["web-secure"]
    rule: str
    middlewares: List[str] = []
    tls: dict = {
        "certResolver": "letsencrypt"
    }
    service: str


class LoadBalancerModel(BaseModel):
    """Models proxy loadBalancer settings inside of proxy service configs."""

    servers: List[dict] = [{"url": ""}]
    passHostHeader: bool = False


class ServiceModel(BaseModel):
    """Models proxy service configs attached to Proximatic() provider resources."""

    loadBalancer: LoadBalancerModel


class ProviderAttributesModel(BaseModel):
    """Models the data attributes of a Proximatic() provider resource."""

    router: RouterModel
    service: ServiceModel
    middlewares: dict
    endpoint: str
    server: str


AttributesModelType = TypeVar("AttributesModelType")

class ResourceModel(GenericModel, Generic[AttributesModelType]):
    """Models any resource in the Proximatic().system resources stores.
    The attributes parameter accepts any pydantic model, allowing flexible
    data schemas depending on the resource type."""

    id: str
    type: str
    attributes: AttributesModelType  # an attributes object representing some of the resource’s data.
    meta: Dict[str, str] = {}


class ResponseErrorModel(BaseModel):
    """Models all errors attached to responses generated by Proximatic()."""

    id: str  # a unique identifier for this particular occurrence of the problem.
    status: str = ""  # the HTTP status code applicable to this problem, expressed as a string value.
    code: str = ""  # an application-specific error code, expressed as a string value.
    title: str = ""  # a short, human-readable summary of the problem that SHOULD NOT change from occurrence to occurrence of the problem.
    detail: str = (
        ""  # a human-readable explanation specific to this occurrence of the problem.
    )
    meta: Dict[
        str, str
    ] = {}  # a meta object containing non-standard meta-information about the error.


class ResponseModel(BaseModel):
    """Models all responses generated by Proximatic()."""

    data: Optional[List[ResourceModel]]
    error: Optional[List[ResponseErrorModel]]
    meta: Optional[Dict[str, str]]


class SystemConfigModel(BaseModel):
    """Models the entire Proximatic().system configuration store."""

    yml_path: Path
    fqdn: str = "example.com"
    providers: List[ResourceModel] = []


class ProviderExportModel(BaseModel):
    """
    Models the exported YAML for provider resource file dumps.
    At export time, models are inserted into the top-level routers, services,
    and middlewares sections of the 'http' dictionary.
    """

    http: Dict[str, dict] = {"routers": {}, "services": {}, "middlewares": {}}
