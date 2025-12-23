
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
