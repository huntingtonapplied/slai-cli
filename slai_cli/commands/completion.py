"""Shell completion for SLAI CLI."""

import click


@click.command()
@click.argument("shell", required=False, type=click.Choice(["bash", "zsh", "fish"], case_sensitive=False))
@click.pass_context
def completion(ctx, shell):
    """Generate shell completion script.

    \b
    Examples:
        slai completion bash > ~/.bashrc
        slai completion zsh >> ~/.zshrc
        slai completion fish > ~/.config/fish/config.fish
    """
    import subprocess
    import shutil

    if shell is None:
        # Detect current shell
        shell = _detect_shell()

    if shell == "bash":
        click.echo("eval \"$(_SLAI_COMPLETE=bash_source slai)\"")
    elif shell == "zsh":
        click.echo("eval \"$(_SLAI_COMPLETE=zsh_source slai)\"")
    elif shell == "fish":
        click.echo("eval (env _SLAI_COMPLETE=fish_source slai)")


def _detect_shell():
    import os
    shell = os.path.basename(os.getenv("SHELL", ""))
    if "bash" in shell:
        return "bash"
    elif "zsh" in shell:
        return "zsh"
    elif "fish" in shell:
        return "fish"
    return "bash"  # default
