
def format_tx_info(tx: dict) -> str:
    required_keys = [
        "hash",
        "from",
        "to",
        "value_eth",
        "gas_used",
        "fee_eth",
        "status",
        "block_number",
        "timestamp",
    ]
    
    missing_keys = [key for key in required_keys if key not in tx]

    if missing_keys:
        raise ValueError(
            f"format_tx_info missing required fields: {', '.join(missing_keys)}"
        )
    
    
    
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
