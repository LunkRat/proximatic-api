# Proximatic

Python API for managing Proximatic configuration files.

When installed, the `proximatic` command provides a CLI for managing Proximatic configuration.

This Python package provides the core for the Proximatic system. 

If you are looking for the turn-key production deployment of Proximatic, see [https://github.com/LunkRat/proximatic](https://github.com/LunkRat/proximatic).

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
proximatic = Proximatic(yml_dir='/path/to/your/proximatic/data', fqdn='example.org')
```

### JSON REST API interface

You can run the (experimental) REST API on your localhost by typing the command:

```bash
proximatic-http
```

It will try to open your browser to [http://localhost:8000](http://localhost:8000)

## License

The MIT License (MIT)

## Author

Link Swanson (LunkRat)