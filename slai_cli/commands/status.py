"""slai status — show system status."""

import click
from rich.panel import Panel
from slai_cli.api import SLAIClient, AuthError, APIError
from slai_cli.output import get_console, is_json, print_json
from slai_cli.exit_codes import EXIT_AUTH, EXIT_GENERAL


@click.command()
@click.pass_context
def status(ctx):
    """Show SLAI system status and recent activity."""
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
        loads = client.list_loads(params={"limit": 5})
        shipments = client.list_shipments(params={"limit": 5})
        metrics = client.get_portfolio_metrics()
    except APIError as e:
        if json_mode:
            print_json({"error": str(e)})
        else:
            click.echo(f"✗ {e}", err=True)
        raise SystemExit(EXIT_GENERAL)

    if json_mode:
        print_json({
            "loads": loads[:5] if loads else [],
            "shipments": shipments[:5] if shipments else [],
            "metrics": metrics,
        })
        return

    console = get_console(ctx)

    # Loads summary
    if loads:
        click.echo(f"\nLoads ({len(loads)} recent):")
        for load in loads[:5]:
            click.echo(f"  • {load.get('name', 'Unknown')} — {load.get('status', 'unknown')}")

    # Shipments summary
    if shipments:
        click.echo(f"\nShipments ({len(shipments)} recent):")
        for s in shipments[:5]:
            click.echo(f"  • {s.get('id', '?')} — {s.get('status', 'unknown')}")

    # Portfolio metrics
    if metrics:
        click.echo(f"\nPortfolio Metrics:")
        click.echo(f"  Total Loads: {metrics.get('total_loads', 'N/A')}")
        click.echo(f"  Active Shipments: {metrics.get('active_shipments', 'N/A')}")
