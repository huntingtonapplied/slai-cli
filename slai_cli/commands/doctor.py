"""slai doctor — diagnose connection and configuration issues."""

import click
import socket
from slai_cli.config import load_config, get_api_url, get_api_key
from slai_cli.output import get_console


@click.command()
@click.pass_context
def doctor(ctx):
    """Diagnose connection and configuration issues."""
    json_mode = is_json(ctx)
    console = get_console(ctx)

    config = load_config()
    api_url = get_api_url()
    api_key = get_api_key()

    if json_mode:
        import json
        click.echo(json.dumps({
            "config_exists": bool(config),
            "api_url": api_url,
            "api_key_set": bool(api_key),
            "checks": _run_checks(api_url, api_key),
        }, indent=2))
        return

    console.print("[bold]SLAI CLI Diagnostics[/bold]")
    click.echo()

    # Config check
    if config:
        console.print("✓ Config file exists")
    else:
        console.print("✗ No config file found (~/.slai/config.yaml)")

    # API key check
    if api_key:
        console.print(f"✓ API key is set ({api_key[:8]}...)")
    else:
        console.print("✗ No API key set. Run: slai login")

    # API URL check
    console.print(f"  API URL: {api_url}")

    # Connection check
    checks = _run_checks(api_url, api_key)
    for check in checks:
        status = "✓" if check["ok"] else "✗"
        console.print(f"{status} {check['name']}: {check.get('detail', '')}")


def _run_checks(api_url, api_key):
    checks = []

    # TCP connectivity
    try:
        host = api_url.replace("http://", "").replace("https://", "").split("/")[0]
        host, _, port = host.partition(":")
        port = int(port) if port else (443 if api_url.startswith("https") else 80)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((host, port))
        sock.close()
        checks.append({"name": "TCP connect", "ok": True})
    except Exception as e:
        checks.append({"name": "TCP connect", "ok": False, "detail": str(e)})

    # HTTP check
    import httpx
    try:
        resp = httpx.get(f"{api_url}/health", timeout=5)
        checks.append({"name": "HTTP GET /health", "ok": resp.status_code < 500})
    except Exception as e:
        checks.append({"name": "HTTP GET /health", "ok": False, "detail": str(e)})

    return checks
