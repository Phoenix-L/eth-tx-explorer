# src/eth_tx_explorer/cli.py
from datetime import datetime
from eth_tx_explorer.rpc import get_web3
import click

from eth_tx_explorer.core import (
    fetch_block_info,
    fetch_tx_info,
)

from eth_tx_explorer.formatters import (
    format_tx_info,
)

from eth_tx_explorer import __version__


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="eth-tx-explorer")
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
    
    # 1. Mutual exclusion check
    if tx_hash and block is not None:
        raise click.UsageError("Provide either TX_HASH or --block, not both.")

    w3 = get_web3()

    if block is not None:
        info = fetch_block_info(w3, block)

        click.echo(f"Block: {info['number']}")
        click.echo(f"Timestamp (UTC): {info['timestamp']}")
        click.echo(f"Transaction count: {info['tx_count']}")

    elif tx_hash:
        tx_info = fetch_tx_info(w3, tx_hash)
        click.echo(format_tx_info(tx_info))
     
    elif tx_hash is None:
        block = w3.eth.get_block("latest", full_transactions=True)
        click.echo(f"Block {block.number} has {len(block.transactions)} txs")
        
        for tx in block.transactions:
            tx_info = fetch_tx_info(w3, tx.hash.hex())
            click.echo(format_tx_info(tx_info))
            click.echo("-" * 40)       
   

    raise click.UsageError("Provide TX_HASH or --block.")
    
    return

