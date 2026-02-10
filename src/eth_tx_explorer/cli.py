# src/eth_tx_explorer/cli.py
import json
from datetime import datetime
from eth_tx_explorer.rpc import get_web3
import click

from eth_tx_explorer.core import (
    fetch_block_info,
    fetch_tx_info,
    print_erc20_logs,
    print_receipt_logs,
    process_block_transfers,
)

from eth_tx_explorer.formatters import (
    format_tx_info,
    format_transfer_summary,
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
     
    else:
        # No args: latest block + per-tx summaries
        block = w3.eth.get_block("latest", full_transactions=True)
        click.echo(f"Block {block.number} has {len(block.transactions)} txs")
        for tx in block.transactions:
            tx_info = fetch_tx_info(w3, tx.hash.hex())
            click.echo(format_tx_info(tx_info))
            click.echo("-" * 40)

@cli.command()
@click.argument("tx_hash")
def logs(tx_hash: str) -> None:
    """
    Show raw event logs for a transaction.

    Example:
      eth-tx-explorer logs 0xabc...
    """
    if tx_hash is None:
        raise click.UsageError("Provide TX_HASH.")
        
    w3 = get_web3()

    receipt = w3.eth.get_transaction_receipt(tx_hash)


    print_receipt_logs(receipt)


@cli.command(name="erc20-logs")
@click.argument("block_number", type=int)
def erc20_logs(block_number: int) -> None:
    """
    Print raw logs for receipts in a block that contain ERC-20 Transfer events.

    Example:
      eth-tx-explorer erc20-logs 19000000
    """
    if block_number is None:
        raise click.UsageError("Provide BLOCK_NUMBER.")

    w3 = get_web3()
    print_erc20_logs(w3, block_number)


@cli.command()
def repl() -> None:
    """
    Start an interactive Python REPL with eth-tx-explorer helpers pre-loaded.

    Provides: w3, fetch_block_info, fetch_tx_info, format_tx_info,
    print_receipt_logs, print_erc20_logs.

    Example:
      eth-tx-explorer repl
    """
    import code

    from eth_tx_explorer import repl_helper

    ns = {k: v for k, v in vars(repl_helper).items() if not k.startswith("_")}
    banner = (
        "eth-tx-explorer REPL — w3, fetch_block_info, fetch_tx_info, "
        "format_tx_info, print_receipt_logs, print_erc20_logs available.\n"
    )
    code.interact(banner=banner, local=ns)


@cli.command(name="block-transfers")
@click.argument("block_number", type=int)
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def block_transfers(block_number: int, output_json: bool) -> None:
    """
    List all ETH and ERC-20 transfers in a block.

    Transfer types: ETH_SIMPLE_TRANSFER, ETH_CALL_WITH_VALUE,
    CONTRACT_CREATION_WITH_VALUE, ERC20_TRANSFER.
    TransactionIndex from tx/receipt/block order (never from enumeration).

    Example:
      eth-tx-explorer block-transfers 19000000
    """
    w3 = get_web3()
    try:
        records = process_block_transfers(w3, block_number)
        if not records:
            click.echo(f"No transfers found in block {block_number}")
            return
        if output_json:
            out = []
            for r in records:
                tc = r.get("token_contract")
                o = {
                    "transfer_type": r["transfer_type"],
                    "tx_hash": r["tx_hash"],
                    "transaction_index": r["transaction_index"],
                    "envelope_type": r["envelope_type"],
                    "from_addr": str(r["from_addr"]) if r.get("from_addr") is not None else None,
                    "to_addr": str(r["to_addr"]) if r.get("to_addr") is not None else None,
                    "eth_value_wei": r.get("eth_value_wei"),
                    "token_contract": str(tc) if tc is not None else None,
                    "token_value": r.get("token_value"),
                    "gas": r.get("gas"),
                    "gasPrice": r.get("gasPrice"),
                    "maxFeePerGas": r.get("maxFeePerGas"),
                    "maxPriorityFeePerGas": r.get("maxPriorityFeePerGas"),
                    "gasUsed": r.get("gasUsed"),
                    "effectiveGasPrice": r.get("effectiveGasPrice"),
                    "tx_type": r.get("tx_type"),
                }
                out.append(o)
            click.echo(json.dumps(out, indent=2, default=str))
        else:
            click.echo(f"Block {block_number} — {len(records)} transfer(s) found")
            click.echo("=" * 60)
            for r in records:
                click.echo(format_transfer_summary(w3, r))
                click.echo("-" * 60)
    except ValueError as e:
        raise click.UsageError(str(e))
    except Exception as e:
        raise click.ClickException(f"Error fetching block: {e}")
