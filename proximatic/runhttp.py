import os
import typer
import uvicorn
from .restapi import app as app


def http():
    """
    Starts uvicorn serving the FastAPI app() defined in restapi.py on localhost port 8000.
    For local development only! Production deployment should use the containerized stack.
    """

    if is_docker():
        typer.echo(
            """
        You appear to be running proximatic-http from a Docker container. 
        Make sure this is not your production container. 
        Type Y to launch uvicorn on localhost:8000.
        """
        )
    # Launch a web browser on localhost open to the api endpoint.
    # @see https://typer.tiangolo.com/tutorial/launch/

    typer.echo("Launching web browser to api docs:")
    typer.launch("http://127.0.0.1:8000/docs")

    # Run unvicorn server bound to port 8000 on localhost.
    # @see https://fastapi.tiangolo.com/#example
    # @see https://www.uvicorn.org/deployment/

    uvicorn.run(
        "proximatic.runhttp:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # For development. Watches for file changes and reloads the server hot.
        log_level="debug",
    )


def is_docker():
    path = "/proc/self/cgroup"
    return (
        os.path.exists("/.dockerenv")
        or os.path.isfile(path)
        and any("docker" in line for line in open(path))
    )
