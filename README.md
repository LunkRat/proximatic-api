# Proximatic

Python API for managing Proximatic configuration files.

When installed, the `proximatic` command provides a CLI for managing Proximatic configuration.

This Python package provides the core for the Proximatic system.

## Installation

```bash
pip install proximatic
```

## Usage

### Command Line Interface (CLI)

Open a Terminal and type:

```bash
proximatic
```

Use `proximatic --help` for available commands and options.

### Python API programmatic interface

```python
from proximatic import Proximatic
proximatic = Proximatic(yml_dir='/path/to/your/proximatic/data', fqdn='yourdomain.org')
```

### JSON REST API interface

You can try out the (experimental) REST API by typing the command:

```bash
proximatic-http
```

## License

The MIT License (MIT)

## Author

Link Swanson (LunkRat)