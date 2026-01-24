from datetime import datetime
from web3 import Web3
from web3.types import HexBytes
from typing import Dict, Any
from eth_utils import keccak, to_bytes


# ERC-20 Transfer event signature: Transfer(address,address,uint256)
TRANSFER_SIG = HexBytes(keccak(to_bytes(text="Transfer(address,address,uint256)")))


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
        "hash": Web3.to_hex(tx.hash),
        "from": tx["from"],
        "to": tx.to,
        "value_eth": value_eth,
        "gas_used": receipt.gasUsed,
        "fee_eth": gas_fee_eth,
        "status": "SUCCESS" if receipt.status == 1 else "REVERTED",
        "block_number": tx.blockNumber,
        "timestamp": datetime.utcfromtimestamp(block.timestamp),
    }


def print_receipt_logs(receipt) -> None:
    
    logs = receipt.logs

    if not logs:
        print("No logs found.")
        return

    print(f"{len(logs)} log(s) found:")
    print("-" * 60)

    for i, log in enumerate(logs):
        print(f"Log #{i}")
        print(f"  Address: {log.address}")
        print(f"  LogIndex: {log.logIndex}")

        print("  Topics:")
        for topic in log.topics:
            print(f"    {topic.hex()}")

        print(f"  Data: {log.data.hex()}")
        print("-" * 60)


def print_erc20_logs(w3: Web3, block_number: int) -> None:
    """
    Print logs for all transactions in a block that contain ERC-20 Transfer events.
    
    Args:
        w3: Web3 instance connected to Ethereum node
        block_number: Block number to inspect
    """
    # Fetch the block
    block = w3.eth.get_block(block_number)
    
    # Iterate through all transactions in the block
    for tx_hash in block.transactions:
        # Fetch the receipt for each transaction
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        
        # Inspect logs in the receipt
        if receipt.logs:
            # Check if any log has topics[0] == TRANSFER_SIG
            has_transfer = False
            for log in receipt.logs:
                if log.topics and len(log.topics) > 0:
                    if log.topics[0] == TRANSFER_SIG:
                        has_transfer = True
                        break
            
            # If any log matches TRANSFER_SIG, print all logs for this receipt
            if has_transfer:
                print_receipt_logs(receipt)
