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
        blk = w3.eth.get_block(block)

        ts = datetime.utcfromtimestamp(blk.timestamp)

        click.echo(f"Block: {blk.number}")
        click.echo(f"Timestamp (UTC): {ts}")
        click.echo(f"Transaction count: {len(blk.transactions)}")

        return

    if tx_hash:
        tx = w3.eth.get_transaction(tx_hash)

        blk = w3.eth.get_block(tx.blockNumber)
     
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        value_eth = w3.from_wei(tx.value, "ether")
        gas_fee_eth = w3.from_wei(
            receipt.gasUsed * receipt.effectiveGasPrice,
            "ether"
        )

        ts = datetime.utcfromtimestamp(blk.timestamp)

        click.echo(f"Transaction: {tx_hash}")
        click.echo(f"From: {tx['from']}")
        click.echo(f"To: {tx.to}")
        click.echo(f"Value: {value_eth} ETH")
        click.echo(f"Gas used: {receipt.gasUsed}")
        click.echo(f"Fee: {gas_fee_eth} ETH")
        click.echo(f"Status: {'SUCCESS' if receipt.status == 1 else 'REVERTED'}")
        click.echo(f"Block: {tx.blockNumber}")
        click.echo(f"Timestamp (UTC): {ts}")
  
    elif tx_hash==None:
        block = w3.eth.get_block("latest", full_transactions=True)
        click.echo(f"Block {block.number} has {len(block.transactions)} txs")
        for tx in block.transactions:
            blk = w3.eth.get_block(tx.blockNumber)
     
            receipt = w3.eth.get_transaction_receipt(tx.hash)
            value_eth = w3.from_wei(tx.value, "ether")
            gas_fee_eth = w3.from_wei(
                receipt.gasUsed * receipt.effectiveGasPrice,
                "ether"
            )

            ts = datetime.utcfromtimestamp(blk.timestamp)

            click.echo(f"Transaction: {tx.hash}")
            click.echo(f"From: {tx['from']}")
            click.echo(f"To: {tx.to}")
            click.echo(f"Value: {value_eth} ETH")
            click.echo(f"Gas used: {receipt.gasUsed}")
            click.echo(f"Fee: {gas_fee_eth} ETH")
            click.echo(f"Status: {'SUCCESS' if receipt.status == 1 else 'REVERTED'}")
            click.echo(f"Block: {tx.blockNumber}")
            click.echo(f"Timestamp (UTC): {ts}")
        
    return

    raise click.UsageError("Provide TX_HASH or --block.")

