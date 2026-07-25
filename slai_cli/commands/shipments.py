"""slai shipments — manage shipments."""

import click
from rich.table import Table
from slai_cli.api import SLAIClient, AuthError, APIError
from slai_cli.output import get_console, is_json, print_json
from slai_cli.exit_codes import EXIT_AUTH, EXIT_GENERAL


@click.group()
@click.pass_context
def shipments(ctx):
    """Manage shipments."""
    pass


@shipments.command("list")
@click.option("--limit", "-n", default=20, show_default=True, help="Max results to return")
@click.option("--status", "-s", default=None, help="Filter by status")
@click.option("--quiet", "-q", is_flag=True, help="Print only shipment IDs")
@click.pass_context
def shipments_list(ctx, limit, status, quiet):
    """List shipments."""
    json_mode = is_json(ctx)

    try:
        client = SLAIClient()
    except AuthError as e:
        if json_mode:
            print_json({"error": str(e)})
        else:
            click.echo(f"✗ {e}", err=True)
        raise SystemExit(EXIT_AUTH)

    params = {}
    if limit != 20:
        params["limit"] = limit
    if status:
        params["status"] = status

    try:
        shipment_list = client.list_shipments(params=params)
    except APIError as e:
        if json_mode:
            print_json({"error": str(e)})
        else:
            click.echo(f"✗ {e}", err=True)
        raise SystemExit(EXIT_GENERAL)

    if json_mode:
        print_json(shipment_list)
        return

    if not shipment_list:
        click.echo("No shipments found.")
        return

    if quiet:
        for s in shipment_list:
            click.echo(s.get("id", ""))
        return

    console = get_console(ctx)
    table = Table(show_edge=False, pad_edge=False, box=None)
    table.add_column("ID", style="dim", min_width=20)
    table.add_column("Status", min_width=12)
    table.add_column("Load", style="cyan")

    for s in shipment_list:
        table.add_row(
            s.get("id", "")[:8],
            s.get("status", "unknown"),
            s.get("load_name", "Unknown")[:24],
        )

    console.print(table)


@shipments.command("get")
@click.argument("shipment_id")
@click.pass_context
def shipments_get(ctx, shipment_id):
    """Get details of a specific shipment."""
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
        shipment = client.get_shipment(shipment_id)
    except APIError as e:
        if json_mode:
            print_json({"error": str(e)})
        else:
            click.echo(f"✗ {e}", err=True)
        raise SystemExit(EXIT_GENERAL)

    if json_mode:
        print_json(shipment)
        return

    console = get_console(ctx)
    console.print(f"[bold]Shipment {shipment.get('id', '')}[/bold]")
    console.print(f"  Status: {shipment.get('status', '')}")
    console.print(f"  Load ID: {shipment.get('load_id', '')}")
