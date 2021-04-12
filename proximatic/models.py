from typing import Optional, List, Dict
from pydantic import BaseModel
from pathlib import Path


class ResourceAttributesModel(BaseModel):
    router_rule: str = None
    middlewares: list = None
    service_url: str = None


class ResourceModel(BaseModel):
    """Models any resource in the Proximatic().system resources stores.
    The attributes parameter accepts any pydantic model, allowing flexible
    data schemas depending on the resource type."""

    resource_id: str # = Field(..., alias='id')
    type: str
    attributes: ResourceAttributesModel = (
        None  # an attributes object representing some of the resource’s data.
    )
    meta: Dict[str, str] = None


class ResponseErrorModel(BaseModel):
    """Models all errors attached to responses generated by Proximatic()."""

    error_id: str = None # Field(..., alias='id')  # a unique identifier for this particular occurrence of the problem.
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


class DynamicProviderModel(BaseModel):

    http: Dict[str, dict] = {"routers": {}, "services": {}, "middlewares": {}}
    tls: Dict[str, dict] = None
    udp: Dict[str, dict] = None


class SystemConfigModel(BaseModel):
    """Models the entire Proximatic().system configuration store."""

    yml_path: Path
    fqdn: str = "example.org"
    provider: DynamicProviderModel = DynamicProviderModel()


class routerModel(BaseModel):
    """Models a router resource."""

    entryPoints: List[str] = ["web-secure"]
    middlewares: List[str] = []
    service: str
    rule: str
    priority: int = None
    tls: dict = {"certResolver": "letsencrypt"}
    # options: foobar
    # certResolver: foobar
    # domains:
    # - main: foobar
    #   sans:
    #   - foobar
    #   - foobar
    # - main: foobar
    #   sans:
    #   - foobar
    #   - foobar


# Services models (not yet utilized):


class loadBalancerOptionsModel(BaseModel):
    sticky: dict = None
    # cookie: dict
    #     name: str
    #     secure: bool
    #     httpOnly: bool
    #     sameSite: str
    servers: List[dict] = [{"url": ""}]
    healthCheck: dict = None
    # scheme: str
    # path: str
    # port: int
    # interval: str
    # timeout: str
    # hostname: str
    # followRedirects: bool
    # headers:
    #     name0: str
    #     name1: str
    passHostHeader: bool = False
    responseForwarding: dict = None
    # flushInterval: str
    serversTransport: str = None


class mirroringOptionsModel(BaseModel):
    service: str
    maxBodySize: int
    mirrors: List[dict]
    # - name: foobar
    #   percent: 42
    # - name: foobar
    #   percent: 42


class weightedOptionsModel(BaseModel):
    services: List[dict]
    # - name: foobar
    #   weight: 42
    # - name: foobar
    #   weight: 42
    sticky: dict
    #   cookie:
    #     name: foobar
    #     secure: true
    #     httpOnly: true
    #     sameSite: foobar


# Middleware models (not yet utilized):


class addPrefixOptionsModel(BaseModel):
    prefix: str


class basicAuthOptionsModel(BaseModel):
    users: List[str] = None
    usersFile: str = None
    realm: str = None
    removeHeader: bool = None
    headerField: str = None


class bufferingOptionsModel(BaseModel):
    maxRequestBodyBytes: int
    memRequestBodyBytes: int
    maxResponseBodyBytes: int
    memResponseBodyBytes: int
    retryExpression: str


class chainModel:
    middlewares: List[str]


class circuitBreakerModel(BaseModel):
    expression: str


class compressOptionsModel(BaseModel):
    excludedContentTypes: List[str]


class contentTypeModel(BaseModel):
    autoDetect: bool


class digestAuthOptionsModel(BaseModel):
    users: List[str]
    usersFile: str
    removeHeader: bool
    realm: str
    headerField: str


class errorsOptionsModel(BaseModel):
    status: List[str]
    service: str
    query: str


class forwardAuthOptionsModel(BaseModel):
    address: str
    # !! dict type ##
    tls: dict
    trustForwardHeader: bool
    authResponseHeaders: List[str]
    authResponseHeadersRegex: str
    authRequestHeaders: List[str]


class headersOptionsModel(BaseModel):
    customRequestHeaders: Dict[str, str] = None
    customResponseHeaders: Dict[str, str] = None
    accessControlAllowCredentials: bool = None
    accessControlAllowHeaders: List[str] = None
    accessControlAllowMethods: List[str] = None
    accessControlAllowOrigin: str = None
    accessControlAllowOriginList: List[str] = None
    accessControlAllowOriginListRegex: List[str] = None
    accessControlExposeHeaders: List[str] = None
    accessControlMaxAge: int = None
    addVaryHeader: bool = None
    allowedHosts: List[str] = None
    hostsProxyHeaders: List[str] = None
    sslRedirect: bool = True
    sslTemporaryRedirect: bool = None
    sslHost: str = None
    sslProxyHeaders: Dict[str, str] = None
    sslForceHost: bool = None
    stsSeconds: int = None
    stsIncludeSubdomains: bool = True
    stsPreload: bool = True
    forceSTSHeader: bool = True
    frameDeny: bool = True
    customFrameOptionsValue: str = None
    contentTypeNosniff: bool = True
    browserXssFilter: bool = True
    customBrowserXSSValue: str = None
    contentSecurityPolicy: str = None
    publicKey: str = None
    referrerPolicy: str = None
    featurePolicy: str = None
    isDevelopment: bool = None


class ipWhiteListOptionsModel(BaseModel):
    sourceRange: List[str]
    ## dict type!!
    ipStrategy: dict = None
    #   depth: int
    #   excludedIPs: List[str] # could probably do type validation with ip/cdir types


class inFlightReqModel(BaseModel):
    amount: int
    ## dict type!!
    sourceCriterion: dict


class rateLimitOptionsModel(BaseModel):
    average: int
    period: int
    burst: int
    ## dict type!!
    sourceCriterion: dict
    # ipStrategy:
    #   depth: int
    #   excludedIPs:
    #   - str
    #   - str
    # requestHeaderName: str
    # requestHost: bool


class redirectRegexOptionsModel(BaseModel):
    regex: str
    replacement: str
    permanent: bool


class redirectSchemeOptionsModel(BaseModel):
    scheme: str
    port: str
    permanent: bool


class replacePathOptionsModel(BaseModel):
    path: str


class replacePathRegexOptionsModel(BaseModel):
    regex: str
    replacement: str


class retryOptionsModel(BaseModel):
    attempts: int
    initialInterval: int


class stripPrefixOptionsModel(BaseModel):
    prefixes: List[str]
    forceSlash: bool


class stripPrefixRegexOptionsModel(BaseModel):
    regex: List[str]


service_models = {"loadBalancer": loadBalancerOptionsModel}
middleware_models = {
    "headers": headersOptionsModel,
    "ipWhiteList": ipWhiteListOptionsModel,
    "basicAuth": basicAuthOptionsModel,
}
