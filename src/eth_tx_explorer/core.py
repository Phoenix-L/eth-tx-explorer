from datetime import datetime
from web3 import Web3
from web3.types import HexBytes
from typing import Dict, Any, List, Tuple, Optional
from eth_utils import keccak, to_bytes


# ERC-20 Transfer event signature: Transfer(address,address,uint256)
TRANSFER_SIG = HexBytes(keccak(to_bytes(text="Transfer(address,address,uint256)")))

# Transfer types (Ethereum-correct)
ETH_SIMPLE_TRANSFER = "ETH_SIMPLE_TRANSFER"
ETH_CALL_WITH_VALUE = "ETH_CALL_WITH_VALUE"
CONTRACT_CREATION_WITH_VALUE = "CONTRACT_CREATION_WITH_VALUE"
ERC20_TRANSFER = "ERC20_TRANSFER"


def _get_attr(obj: Any, key: str, default: Any = None) -> Any:
    """Get attribute from obj via attribute or dict-style access."""
    v = getattr(obj, key, None)
    if v is not None:
        return v
    if hasattr(obj, "get") and callable(getattr(obj, "get")):
        try:
            return obj.get(key, default)
        except Exception:
            pass
    if hasattr(obj, "__getitem__"):
        try:
            return obj[key]
        except (KeyError, TypeError):
            pass
    return default


def _canonical_tx_hash(tx: Any) -> str:
    """Canonical hex hash for map keys and lookups (lowercase, 0x-prefixed)."""
    h = getattr(tx, "hash", None) or (tx.get("hash") if hasattr(tx, "get") else None)
    if h is None:
        return ""
    return Web3.to_hex(h).lower()


def envelope_type(tx: Any) -> str:
    """Transaction envelope type from tx.type (Legacy | EIP-2930 | EIP-1559)."""
    t = _get_attr(tx, "type", 0)
    if t == 1:
        return "EIP-2930"
    if t == 2:
        return "EIP-1559"
    return "Legacy"


def _transaction_index_from_obj(obj: Any) -> Optional[int]:
    """Read transactionIndex from tx or receipt; try camelCase and snake_case."""
    for key in ("transactionIndex", "transaction_index"):
        v = _get_attr(obj, key, None)
        if v is not None:
            return int(v)
    return None


def get_transaction_index(
    tx: Any,
    receipt: Any,
    tx_hash_to_index: Dict[str, int],
    tx_hash_hex: str,
) -> int:
    """
    Resolve transactionIndex from block order, then tx, then receipt.
    Block position (tx_hash_to_index) is primary; never use enumeration order.
    """
    # 1. Block position (canonical): we control this, always correct when key exists
    idx = tx_hash_to_index.get(tx_hash_hex)
    if idx is not None:
        return idx
    # 2. Tx, then receipt
    idx = _transaction_index_from_obj(tx)
    if idx is not None:
        return idx
    idx = _transaction_index_from_obj(receipt)
    if idx is not None:
        return idx
    return 0


def is_contract(w3: Web3, address: Any, cache: Dict[str, bool]) -> bool:
    """Return True if address has code (contract). Uses per-block cache."""
    addr = Web3.to_checksum_address(address) if address else None
    if not addr:
        return False
    key = addr.lower()
    if key in cache:
        return cache[key]
    code = w3.eth.get_code(addr)
    has_code = bool(code and len(code) > 2)
    cache[key] = has_code
    return has_code


def compute_gas_summary(tx: Any, receipt: Any) -> Dict[str, Any]:
    """Extract gas-related fields from transaction and receipt."""
    t = _get_attr(tx, "type", 0)
    gas = _get_attr(tx, "gas")
    gas_used = _get_attr(receipt, "gasUsed")
    effective = _get_attr(receipt, "effectiveGasPrice")
    if t == 2:
        return {
            "gas": gas,
            "gasPrice": None,
            "maxFeePerGas": _get_attr(tx, "maxFeePerGas"),
            "maxPriorityFeePerGas": _get_attr(tx, "maxPriorityFeePerGas"),
            "gasUsed": gas_used,
            "effectiveGasPrice": effective,
            "tx_type": t,
        }
    return {
        "gas": gas,
        "gasPrice": _get_attr(tx, "gasPrice"),
        "maxFeePerGas": None,
        "maxPriorityFeePerGas": None,
        "gasUsed": gas_used,
        "effectiveGasPrice": effective,
        "tx_type": t,
    }


def fetch_block_transfers(w3: Web3, block_number: int) -> Tuple[Dict[str, Any], List[Any]]:
    """Fetch block with full transactions. Returns (block_dict, list of tx objects)."""
    block = w3.eth.get_block(block_number, full_transactions=True)
    if not block:
        raise ValueError(f"Block {block_number} not found")
    block_dict = {"number": block.number, "timestamp": block.timestamp}
    return block_dict, list(block.transactions)


def fetch_transfer_receipts(w3: Web3, transactions: List[Any]) -> List[Tuple[Any, Any]]:
    """Fetch receipts for each tx. Order not guaranteed to match block order."""
    out: List[Tuple[Any, Any]] = []
    for tx in transactions:
        tx_hash = _canonical_tx_hash(tx)
        if not tx_hash:
            continue
        try:
            r = w3.eth.get_transaction_receipt(tx_hash)
            out.append((tx, r))
        except Exception:
            continue
    return out


def _extract_eth_transfer(
    w3: Web3,
    tx: Any,
    receipt: Any,
    tx_index: int,
    env_type: str,
    gas_summary: Dict[str, Any],
    contract_cache: Dict[str, bool],
) -> Optional[Dict[str, Any]]:
    """At most one ETH transfer per tx when tx.value > 0."""
    value = _get_attr(tx, "value", 0) or 0
    if value == 0:
        return None
    from_addr = _get_attr(tx, "from")
    to_addr = _get_attr(tx, "to")
    if to_addr is None:
        transfer_type = CONTRACT_CREATION_WITH_VALUE
        to_display = "(contract creation)"
    else:
        to_checksum = Web3.to_checksum_address(to_addr) if to_addr else None
        if is_contract(w3, to_checksum or to_addr, contract_cache):
            transfer_type = ETH_CALL_WITH_VALUE
            to_display = to_checksum or to_addr
        else:
            transfer_type = ETH_SIMPLE_TRANSFER
            to_display = to_checksum or to_addr
    return {
        "transfer_type": transfer_type,
        "tx_hash": Web3.to_hex(tx.hash),
        "transaction_index": tx_index,
        "envelope_type": env_type,
        "from_addr": from_addr,
        "to_addr": to_display,
        "eth_value_wei": value,
        "token_contract": None,
        "token_value": None,
        **gas_summary,
    }


def _extract_erc20_transfers(
    tx: Any,
    receipt: Any,
    tx_index: int,
    env_type: str,
    gas_summary: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """One ERC20_TRANSFER record per Transfer(address,address,uint256) log."""
    records: List[Dict[str, Any]] = []
    for log in receipt.logs or []:
        if not log.topics or len(log.topics) < 3:
            continue
        if log.topics[0] != TRANSFER_SIG:
            continue
        from_addr = "0x" + (log.topics[1].hex() if hasattr(log.topics[1], "hex") else str(log.topics[1]))[-40:]
        to_addr = "0x" + (log.topics[2].hex() if hasattr(log.topics[2], "hex") else str(log.topics[2]))[-40:]
        amount = int(log.data.hex(), 16) if log.data else 0
        records.append({
            "transfer_type": ERC20_TRANSFER,
            "tx_hash": Web3.to_hex(tx.hash),
            "transaction_index": tx_index,
            "envelope_type": env_type,
            "from_addr": from_addr,
            "to_addr": to_addr,
            "eth_value_wei": None,
            "token_contract": log.address,
            "token_value": amount,
            **gas_summary,
        })
    return records


def process_block_transfers(w3: Web3, block_number: int) -> List[Dict[str, Any]]:
    """
    Identify all transfers in a block. Each transfer is a separate record.
    transactionIndex from block order (primary), then tx/receipt.
    """
    block, transactions = fetch_block_transfers(w3, block_number)
    if not transactions:
        return []
    tx_hash_to_index = {_canonical_tx_hash(t): i for i, t in enumerate(transactions)}
    tx_receipt_pairs = fetch_transfer_receipts(w3, transactions)
    contract_cache: Dict[str, bool] = {}
    all_records: List[Dict[str, Any]] = []

    for tx, receipt in tx_receipt_pairs:
        tx_hash_hex = _canonical_tx_hash(tx)
        tx_index = get_transaction_index(tx, receipt, tx_hash_to_index, tx_hash_hex)
        # tx_index = receipt.transactionIndex
        env_type = envelope_type(tx)
        gas_summary = compute_gas_summary(tx, receipt)

        eth_rec = _extract_eth_transfer(w3, tx, receipt, tx_index, env_type, gas_summary, contract_cache)
        if eth_rec:
            all_records.append(eth_rec)
        erc20_records = _extract_erc20_transfers(tx, receipt, tx_index, env_type, gas_summary)
        all_records.extend(erc20_records)

    return all_records


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
