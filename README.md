# SLAI CLI

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![Status](https://img.shields.io/badge/status-active-success.svg)](#)

**SLAI CLI** (`slai`) is the terminal client for SmartLoad AI (SLAI). Inspect and manage freight loads, shipments, and portfolio metrics from your shell, and script them into CI.

It is a thin client (`click` + `httpx` + `rich`) that talks to the SLAI backend API. Authenticate once, then list and fetch loads and shipments, pull portfolio metrics, check system status, and pipe results as JSON/YAML/CSV into your pipelines.

## Install

```bash
curl -fsSL https://downloads.smartloadai.com/cli/install.sh | bash
```

From source (a clone of this repo):
```bash
pip install -e .
```

There is no PyPI package: the `slai-cli` name on PyPI belongs to an unrelated project, so do not install it from PyPI.

Standalone binary:
```bash
./install.sh --version <version>
```

## Authentication

The CLI needs an API key and the URL of the SLAI API it talks to.

```bash
slai login                 # interactive
slai login --key $SLAI_API_KEY   # non-interactive (CI)
```

Config is stored at `~/.slai/config.yaml`:
```yaml
api_key: your-api-key
api_url: http://localhost:8020   # local backend; production points at the hosted SLAI API
```

Or use environment variables:
- `SLAI_API_KEY`
- `SLAI_API_URL`
- `SLAI_DOWNLOADS_BASE_URL` (default `https://downloads.smartloadai.com`) sets the binary downloads base
- `SLAI_NO_UPDATE_CHECK=1` disables update checks

## Commands

| Command | Description |
|---|---|
| `slai login` | Authenticate with SLAI |
| `slai loads list` | List freight loads |
| `slai loads get <id>` | Get load details |
| `slai loads delete <id>` | Delete a load |
| `slai shipments list` | List shipments |
| `slai shipments get <id>` | Get shipment details |
| `slai metrics portfolio` | View portfolio metrics |
| `slai status` | Show system status |
| `slai doctor` | Diagnose connection issues |
| `slai completion bash` | Generate shell completion |

## Usage

```bash
slai login
slai loads list
slai shipments get <id>
slai metrics portfolio
slai status
```

### Output formats

```bash
slai loads list --output json    # JSON
slai loads list --output yaml    # YAML
slai loads list --csv            # CSV
slai loads list --quiet          # IDs only
```

### CI mode

```bash
slai login --key $SLAI_API_KEY
slai loads list --ci
```

## Documentation & resources

- Hosted product: [smartloadai.com](https://smartloadai.com)

## License

This project is licensed under the MIT License.
