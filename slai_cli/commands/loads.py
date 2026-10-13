"""slai loads — manage supply chain loads."""

import click
from rich.table import Table
from slai_cli.api import SLAIClient, AuthError, APIError
from slai_cli.output import get_console, is_json, print_json
from slai_cli.exit_codes import EXIT_AUTH, EXIT_GENERAL


@click.group()
@click.pass_context
def loads(ctx):
    """Manage supply chain loads."""
    pass


@loads.command("list")
@click.option("--limit", "-n", default=20, show_default=True, help="Max results to return")
@click.option("--status", "-s", default=None, help="Filter by status")
@click.option("--quiet", "-q", is_flag=True, help="Print only load IDs")
@click.option("--csv", "csv_mode", is_flag=True, help="Output as CSV")
@click.pass_context
def loads_list(ctx, limit, status, quiet, csv_mode):
    """List loads."""
    json_mode = is_json(ctx)
    structured = is_json(ctx)

    try:
        client = SLAIClient()
    except AuthError as e:
        if structured:
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
        load_list = client.list_loads(params=params)
    except APIError as e:
        if structured:
            print_json({"error": str(e)})
        else:
            click.echo(f"✗ {e}", err=True)
        raise SystemExit(EXIT_GENERAL)

    if structured:
        print_json(load_list)
        return

    if not load_list:
        click.echo("No loads found.")
        return

    if quiet:
        for l in load_list:
            click.echo(l.get("id", ""))
        return

    if csv_mode:
        click.echo("id,name,status,created_at")
        for l in load_list:
            name = (l.get("name") or "").replace(",", ";")
            click.echo(f"{l.get('id', '')},{name},{l.get('status', '')},{l.get('created_at', '')}")
        return

    console = get_console(ctx)
    table = Table(show_edge=False, pad_edge=False, box=None)
    table.add_column("Name", style="cyan", min_width=20)
    table.add_column("Status", min_width=12)
    table.add_column("Created", style="dim")

    for l in load_list:
        name = (l.get("name") or "Untitled")[:36]
        status_val = l.get("status", "unknown")
        created = l.get("created_at", "")[:10] if l.get("created_at") else ""
        table.add_row(name, status_val, created)

    console.print(table)


@loads.command("get")
@click.argument("load_id")
@click.pass_context
def loads_get(ctx, load_id):
    """Get details of a specific load."""
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
        load = client.get_load(load_id)
    except APIError as e:
        if json_mode:
            print_json({"error": str(e)})
        else:
            click.echo(f"✗ {e}", err=True)
        raise SystemExit(EXIT_GENERAL)

    if json_mode:
        print_json(load)
        return

    console = get_console(ctx)
    console.print(f"[bold]{load.get('name', 'Unknown')}[/bold]")
    console.print(f"  ID: {load.get('id', '')}")
    console.print(f"  Status: {load.get('status', '')}")
    console.print(f"  Created: {load.get('created_at', '')}")


@loads.command("delete")
@click.argument("load_id")
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmation prompt")
@click.pass_context
def loads_delete(ctx, load_id, yes):
    """Delete a load."""
    json_mode = is_json(ctx)
    ci_mode = ctx.obj.get("ci", False) if ctx.obj else False

    if not yes and not ci_mode:
        click.confirm(f"Delete load {load_id}? This cannot be undone.", abort=True)

    try:
        client = SLAIClient()
    except AuthError as e:
        if json_mode:
            print_json({"error": str(e)})
        else:
            click.echo(f"✗ {e}", err=True)
        raise SystemExit(EXIT_AUTH)

    try:
        client.delete_load(load_id)
    except APIError as e:
        if json_mode:
            print_json({"error": str(e)})
        else:
            click.echo(f"✗ {e}", err=True)
        raise SystemExit(EXIT_GENERAL)

    if json_mode:
        print_json({"deleted": load_id})
    else:
        click.echo(f"✓ Deleted load {load_id}")
