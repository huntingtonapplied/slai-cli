"""Output helpers for SLAI CLI."""

import json
import sys

import click
from rich.console import Console


def get_console(ctx=None):
    """Get a Rich console instance."""
    return Console(stderr=False)


def is_json(ctx):
    """Check if output format is JSON."""
    if ctx and ctx.obj:
        return ctx.obj.get("output") == "json"
    return False


def is_structured(ctx):
    """Check if output format is structured (json/yaml)."""
    if ctx and ctx.obj:
        return ctx.obj.get("output") in ("json", "yaml")
    return False


def print_json(data):
    """Print data as JSON."""
    click.echo(json.dumps(data, indent=2, default=str))


def print_structured(ctx, data):
    """Print data in the requested structured format."""
    output = ctx.obj.get("output", "json") if ctx and ctx.obj else "json"
    if output == "yaml":
        import yaml
        click.echo(yaml.dump(data, default_flow_style=False))
    else:
        print_json(data)
