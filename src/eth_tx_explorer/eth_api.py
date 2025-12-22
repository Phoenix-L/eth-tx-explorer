from __future__ import annotations

from typing import Any, Dict, Optional
from web3 import Web3


def fetch_block_info(w3: Web3, block_number: int, full_transactions: bool = False) -> Dict[str, Any]:
    """
    Fetch a block by number.

    full_transactions=False returns tx hashes (fast).
    full_transactions=True returns full tx objects (slower, but richer).
    """
    block = w3.eth.get_block(block_number, full_transactions=full_transactions)
    # Web3 returns an AttributeDict; convert to normal dict for easier handling
    return dict(block)


def fetch_tx_info(w3: Web3, tx_hash: str) -> Dict[str, Any]:
    """
    Fetch tx and receipt. Returns a combined dict.
    """
    tx = w3.eth.get_transaction(tx_hash)
    receipt = w3.eth.get_transaction_receipt(tx_hash)

    result: Dict[str, Any] = {
        "tx": dict(tx),
        "receipt": dict(receipt),
    }
    return result


def safe_get_block_timestamp(block_dict: Dict[str, Any]) -> Optional[int]:
    """
    Helper: some formatting wants timestamp, keep it safe.
    """
    ts = block_dict.get("timestamp")
    return int(ts) if ts is not None else None

