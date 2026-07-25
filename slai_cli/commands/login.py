"""slai login — authenticate and store API key."""

import click
from rich.panel import Panel
from slai_cli.config import save_config, load_config, get_api_url
from slai_cli.api import SLAIClient, APIError
from slai_cli.output import get_console
from slai_cli.exit_codes import EXIT_VALIDATION


@click.command()
@click.option("--key", default=None, help="Your SLAI API key (skips wizard)")
@click.option("--url", default=None, help="API URL (default: http://localhost:8001)")
@click.pass_context
def login(ctx, key: str, url: str):
    """Authenticate with the SLAI platform.

    \b
    Examples:
        slai login                     # interactive wizard
        slai login --key slai_abc123  # non-interactive
    """
    console = get_console(ctx)
    ci_mode = ctx.obj.get("ci", False) if ctx.obj else False

    if not key and ci_mode:
        click.echo("✗ --key is required in CI mode: slai login --key <key>", err=True)
        raise SystemExit(EXIT_VALIDATION)

    if not key:
        click.echo()
        click.echo("  Welcome to SLAI!")
        click.echo()
        click.echo("  To get your API key:")
        click.echo("    1. Go to your SLAI instance /account")
        click.echo("    2. Click the Developer tab")
        click.echo("    3. Copy your API key")
        click.echo()
        key = click.prompt("  API Key", hide_input=True)
        if not url:
            use_custom = click.confirm("  Use a custom API URL?", default=False)
            if use_custom:
                url = click.prompt("  API URL", default="http://localhost:8001")

    key = key.strip()
    config = load_config()
    config["api_key"] = key
    if url:
        config["api_url"] = url.strip()
    save_config(config)

    api_url = url or get_api_url()
    click.echo(f"✓ API key saved to ~/.slai/config.yaml")
    click.echo(f"  API URL: {api_url}")

    try:
        client = SLAIClient(api_key=key, api_url=api_url)
        load_list = client.list_loads()
        console.print(Panel(
            f"✓ Authenticated — {len(load_list)} load(s) found\n\n"
            "  [dim]slai loads list[/dim]         list your loads\n"
            "  [dim]slai shipments list[/dim]    list your shipments\n"
            "  [dim]slai metrics portfolio[/dim]  view portfolio metrics",
            title="Connected",
            border_style="green",
            expand=False,
        ))
    except Exception as e:
        click.echo(f"⚠ Key saved but verification failed: {e}", err=True)
        click.echo("  Check your key and try again: slai login", err=True)
