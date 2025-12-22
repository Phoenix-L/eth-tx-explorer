from datetime import datetime
from web3 import Web3
from typing import Dict, Any


def fetch_block_info(w3: Web3, block_number: int) -> Dict[str, Any]:
    block = w3.eth.get_block(block_number)

    return {
        "number": block.number,
        "timestamp": datetime.utcfromtimestamp(block.timestamp),
        "tx_count": len(block.transactions),
    }


def fetch_tx_info(w3: Web3, tx_hash: str) -> Dict[str, Any]:
    tx = w3.eth.get_transaction(tx_hash)
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    block = w3.eth.get_block(tx.blockNumber)

    value_eth = w3.from_wei(tx.value, "ether")
    gas_fee_eth = w3.from_wei(
        receipt.gasUsed * receipt.effectiveGasPrice,
        "ether"
    )

    return {
        "hash": tx_hash,
        "from": tx["from"],
        "to": tx.to,
        "value_eth": value_eth,
        "gas_used": receipt.gasUsed,
        "fee_eth": gas_fee_eth,
        "status": "SUCCESS" if receipt.status == 1 else "REVERTED",
        "block_number": tx.blockNumber,
        "timestamp": datetime.utcfromtimestamp(block.timestamp),
    }

def format_tx_info(tx: dict) -> str:
    return (
        f"Transaction: {tx['hash']}\n"
        f"From: {tx['from']}\n"
        f"To: {tx['to']}\n"
        f"Value: {tx['value_eth']} ETH\n"
        f"Gas used: {tx['gas_used']}\n"
        f"Fee: {tx['fee_eth']} ETH\n"
        f"Status: {tx['status']}\n"
        f"Block: {tx['block_number']}\n"
        f"Timestamp (UTC): {tx['timestamp']}"
    )
