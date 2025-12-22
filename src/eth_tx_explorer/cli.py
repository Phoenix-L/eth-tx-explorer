# src/eth_tx_explorer/cli.py
from datetime import datetime
from eth_tx_explorer.rpc import get_web3
import click

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """eth-tx-explorer: minimal CLI stub."""
    pass

@cli.command()
def hello() -> None:
    """Sanity check command."""
    click.echo("eth-tx-explorer: hello!")
    

def fetch_block_info(w3, block_number: int):
    """
    Fetch a block and return (block, timestamp_utc).
    """
    blk = w3.eth.get_block(block_number)
    ts = datetime.utcfromtimestamp(blk.timestamp)
    return blk, ts

def fetch_tx_info(w3, tx_hash):
    """
    Fetch transaction, receipt, block, and timestamp.
    """
    tx = w3.eth.get_transaction(tx_hash)
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    blk = w3.eth.get_block(tx.blockNumber)
    ts = datetime.utcfromtimestamp(blk.timestamp)

    return tx, receipt, blk, ts


def format_tx_info(w3, tx, receipt, blk, ts):
    value_eth = w3.from_wei(tx.value, "ether")
    gas_fee_eth = w3.from_wei(
        receipt.gasUsed * receipt.effectiveGasPrice,
        "ether"
    )

    lines = [
        f"Transaction: {tx.hash}",
        f"From: {tx['from']}",
        f"To: {tx.to}",
        f"Value: {value_eth} ETH",
        f"Gas used: {receipt.gasUsed}",
        f"Fee: {gas_fee_eth} ETH",
        f"Status: {'SUCCESS' if receipt.status == 1 else 'REVERTED'}",
        f"Block: {tx.blockNumber}",
        f"Timestamp (UTC): {ts}",
    ]

    return lines



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

    w3 = get_web3()

    if block is not None:
        blk, ts = fetch_block_info(w3, block)

        click.echo(f"Block: {blk.number}")
        click.echo(f"Timestamp (UTC): {ts}")
        click.echo(f"Transaction count: {len(blk.transactions)}")

        return


    if tx_hash:
        tx, receipt, blk, ts = fetch_tx_info(w3, tx_hash)

        lines = format_tx_info(w3, tx, receipt, blk, ts)
        for line in lines:
            click.echo(line)
     
    elif tx_hash is None:
        block = w3.eth.get_block("latest", full_transactions=True)
        click.echo(f"Block {block.number} has {len(block.transactions)} txs")
        
        for tx in block.transactions:
            blk = w3.eth.get_block(tx.blockNumber)    
            receipt = w3.eth.get_transaction_receipt(tx.hash)
            ts = datetime.utcfromtimestamp(blk.timestamp)

            lines = format_tx_info(w3, tx, receipt, blk, ts)
            for line in lines:
                click.echo(line)
        
    return

    raise click.UsageError("Provide TX_HASH or --block.")

