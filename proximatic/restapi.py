import os
from fastapi import FastAPI, status
from fastapi.openapi.utils import get_openapi
from proximatic import Proximatic, __version__


app = FastAPI()

proximatic = Proximatic(fqdn=os.getenv("PROXIMATIC_FQDN"))


@app.get("/")
def read_root():
    """Endpoint returning basic information."""

    return {"Proximatic REST API": __version__}


@app.get("/provider/list")
def provider_list():
    """Endpoint that returns a list of configured providers."""

    response = proximatic.provider_list()

    return response

def proximatic_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Proximatic REST API",
        version=__version__,
        description="Proximatic OpenAPI schema",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://i.pinimg.com/474x/ea/e2/07/eae2071d69a1089f82ec60a5be6037c0.jpg"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = proximatic_openapi
