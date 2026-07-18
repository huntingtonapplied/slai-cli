"""slai api-keys — manage API keys for programmatic access."""

import click
from rich.table import Table
from slai_cli.api import SLAIClient, AuthError, APIError
from slai_cli.output import get_console, is_json, print_json
from slai_cli.exit_codes import EXIT_AUTH, EXIT_GENERAL


@click.group("api-keys")
@click.pass_context
def api_keys(ctx):
    """Manage API keys for programmatic access."""
    pass


@api_keys.command("list")
@click.pass_context
def api_keys_list(ctx):
    """List all API keys for your organization."""
    json_mode = is_json(ctx)
    console = get_console(ctx)

    try:
        client = SLAIClient()
    except AuthError as e:
        if json_mode:
            print_json({"error": str(e)})
        else:
            click.echo(f"✗ {e}", err=True)
        raise SystemExit(EXIT_AUTH)

    try:
        keys = client.list_api_keys()
    except APIError as e:
        if json_mode:
            print_json({"error": str(e)})
        else:
            click.echo(f"✗ {e}", err=True)
        raise SystemExit(EXIT_GENERAL)

    if json_mode:
        print_json(keys)
        return

    if not keys:
        click.echo("No API keys found. Create one with: slai api-keys create --name <name>")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Name")
    table.add_column("Prefix")
    table.add_column("Scopes")
    table.add_column("Status")
    table.add_column("Requests", justify="right")
    table.add_column("Last Used")

    for key in keys:
        last_used = key.get("last_used_at") or "Never"
        if last_used != "Never":
            last_used = last_used[:10]
        table.add_row(
            key.get("id", "")[:8] + "...",
            key.get("name", ""),
            key.get("key_prefix", ""),
            ", ".join(key.get("scopes", [])),
            key.get("status", ""),
            str(key.get("request_count", 0)),
            last_used,
        )

    console.print(table)


@api_keys.command("create")
@click.option("--name", "-n", required=True, help="Friendly name for the key")
@click.option(
    "--scope", "-s",
    multiple=True,
    default=("read",),
    show_default=True,
    type=click.Choice(["read", "write", "admin"]),
    help="Permission scope (can be specified multiple times)",
)
@click.option(
    "--expires-in", "-e",
    default=None,
    type=int,
    metavar="DAYS",
    help="Expiration in days (default: no expiry)",
)
@click.pass_context
def api_keys_create(ctx, name, scope, expires_in):
    """Create a new API key.

    \b
    Examples:
        slai api-keys create --name "CI Pipeline"
        slai api-keys create --name "Read-only" --scope read
        slai api-keys create --name "Admin" --scope read --scope write --scope admin
        slai api-keys create --name "Temp" --expires-in 30
    """
    json_mode = is_json(ctx)
    console = get_console(ctx)

    try:
        client = SLAIClient()
    except AuthError as e:
        if json_mode:
            print_json({"error": str(e)})
        else:
            click.echo(f"✗ {e}", err=True)
        raise SystemExit(EXIT_AUTH)

    try:
        result = client.create_api_key(
            name=name,
            scopes=list(scope),
            expires_in_days=expires_in,
        )
    except APIError as e:
        if json_mode:
            print_json({"error": str(e)})
        else:
            click.echo(f"✗ {e}", err=True)
        raise SystemExit(EXIT_GENERAL)

    if json_mode:
        print_json(result)
        return

    full_key = result.get("key", "")
    console.print(f"\n[bold green]✓ API key created[/bold green]\n")
    console.print(f"  [bold]Name:[/bold]    {result.get('name')}")
    console.print(f"  [bold]Prefix:[/bold]  {result.get('key_prefix')}")
    console.print(f"  [bold]Scopes:[/bold]  {', '.join(result.get('scopes', []))}")
    if result.get("expires_at"):
        console.print(f"  [bold]Expires:[/bold] {result['expires_at'][:10]}")
    console.print()
    console.print(f"  [bold yellow]Your API key (save this — it won't be shown again):[/bold yellow]")
    console.print(f"\n  [bold]{full_key}[/bold]\n")
    console.print("  Use it with:  slai login --key <key>")
    console.print("  Or set env:   export SLAI_API_KEY=<key>")


@api_keys.command("revoke")
@click.argument("key_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def api_keys_revoke(ctx, key_id, yes):
    """Revoke an API key by ID.

    \b
    Example:
        slai api-keys revoke abc12345-...
    """
    json_mode = is_json(ctx)

    if not yes and not json_mode:
        click.confirm(f"Revoke API key {key_id}? This cannot be undone.", abort=True)

    try:
        client = SLAIClient()
    except AuthError as e:
        if json_mode:
            print_json({"error": str(e)})
        else:
            click.echo(f"✗ {e}", err=True)
        raise SystemExit(EXIT_AUTH)

    try:
        client.revoke_api_key(key_id)
    except APIError as e:
        if json_mode:
            print_json({"error": str(e)})
        else:
            click.echo(f"✗ {e}", err=True)
        raise SystemExit(EXIT_GENERAL)

    if json_mode:
        print_json({"revoked": key_id})
    else:
        click.echo(f"✓ API key {key_id} revoked.")
