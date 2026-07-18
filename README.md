# SLAI CLI

CLI tool for SLAI supply chain management — interact with loads, shipments, and metrics from your terminal.

## Installation

```bash
pip install slai-cli
```

Or from source:
```bash
cd /Users/latarencebutts/ahl/SLAI/cli
pip install -e .
```

### Install Standalone Binary

```bash
./install.sh --version <version>
```

Environment:
- `SLAI_DOWNLOADS_BASE_URL` (default: `https://downloads.slai.ai`)

Disable update checks:
- `SLAI_NO_UPDATE_CHECK=1`

## Quick Start

```bash
# Authenticate
slai login

# View loads
slai loads list

# View shipments
slai shipments list

# Check metrics
slai metrics portfolio

# System status
slai status
```

## Commands

| Command | Description |
|---------|-------------|
| `slai login` | Authenticate with SLAI |
| `slai loads list` | List supply chain loads |
| `slai loads get <id>` | Get load details |
| `slai loads delete <id>` | Delete a load |
| `slai shipments list` | List shipments |
| `slai shipments get <id>` | Get shipment details |
| `slai metrics portfolio` | View portfolio metrics |
| `slai status` | Show system status |
| `slai doctor` | Diagnose connection issues |
| `slai completion bash` | Generate shell completion |

## Configuration

Config stored at `~/.slai/config.yaml`:
```yaml
api_key: your-api-key
api_url: http://localhost:8001
```

Or use environment variables:
- `SLAI_API_KEY`
- `SLAI_API_URL`

## Output Formats

```bash
slai loads list --output json    # JSON output
slai loads list --output yaml    # YAML output
slai loads list --quiet          # IDs only
slai loads list --csv           # CSV output
```

## CI Mode

```bash
slai login --key $SLAI_API_KEY
slai loads list --ci
```
