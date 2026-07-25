"""slai metrics — view portfolio and system metrics."""

import click
from slai_cli.api import SLAIClient, AuthError, APIError
from slai_cli.output import get_console, is_json, print_json
from slai_cli.exit_codes import EXIT_AUTH, EXIT_GENERAL


@click.group()
@click.pass_context
def metrics(ctx):
    """View portfolio and system metrics."""
    pass


@metrics.command("portfolio")
@click.pass_context
def metrics_portfolio(ctx):
    """Get portfolio metrics."""
    json_mode = is_json(ctx)

    try:
        client = SLAIClient()
    except AuthError as e:
        if json_mode:
            print_json({"error": str(e)})
        else:
            click.echo(f"✗ {e}", err=True)
        raise SystemExit(EXIT_AUTH)

    try:
        data = client.get_portfolio_metrics()
    except APIError as e:
        if json_mode:
            print_json({"error": str(e)})
        else:
            click.echo(f"✗ {e}", err=True)
        raise SystemExit(EXIT_GENERAL)

    if json_mode:
        print_json(data)
        return

    console = get_console(ctx)
    console.print("[bold]Portfolio Metrics[/bold]")
    console.print(f"  Total Loads: {data.get('total_loads', 'N/A')}")
    console.print(f"  Active Shipments: {data.get('active_shipments', 'N/A')}")
    console.print(f"  Total Organizations: {data.get('total_organizations', 'N/A')}")
