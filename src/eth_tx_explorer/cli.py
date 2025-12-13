# src/eth_tx_explorer/cli.py
import click

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """eth-tx-explorer: minimal CLI stub."""
    pass

@cli.command()
def hello() -> None:
    """Sanity check command."""
    click.echo("eth-tx-explorer: hello!")

@cli.command()
@click.argument("tx_hash", required=False)
@click.option("--block", type=int, default=None, help="Block number to inspect")
def inspect(tx_hash: str | None, block: int | None) -> None:
    """
    Placeholder command.

    Examples:
      - Inspect a tx:     inspect 0xabc...
      - Inspect a block:  inspect --block 123456
    """
    if tx_hash and block is not None:
        raise click.UsageError("Provide either TX_HASH or --block, not both.")

    if block is not None:
        click.echo(f"[stub] would inspect block: {block}")
        return

    if tx_hash:
        click.echo(f"[stub] would inspect tx: {tx_hash}")
        return

    raise click.UsageError("Provide TX_HASH or --block.")

