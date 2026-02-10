def format_transfer_summary(w3, record: dict) -> str:
    """
    Format a single transfer record. Strict order:
    TransferType -> Transaction -> TransactionIndex -> EnvelopeType -> From/To -> Value or Token -> Gas.
    """
    lines = [
        f"TransferType: {record['transfer_type']}",
        f"Transaction: {record['tx_hash']}",
        f"TransactionIndex: {record['transaction_index']}",
        f"EnvelopeType: {record['envelope_type']}",
    ]
    from_addr = record.get("from_addr") or ""
    to_addr = record.get("to_addr") or "(contract creation)"
    lines.append(f"From: {from_addr} → To: {to_addr}")
    if record["transfer_type"] == "ERC20_TRANSFER":
        lines.append(f"Token Contract: {record['token_contract']}")
        lines.append(f"Token Amount: {record['token_value']} (raw uint256)")
    else:
        wei = record.get("eth_value_wei") or 0
        lines.append(f"Value: {w3.from_wei(wei, 'ether')} ETH")
    gas = record.get("gas") or 0
    gas_used = record.get("gasUsed") or 0
    lines.append(f"Gas: {gas} limit | {gas_used} used")
    t = record.get("tx_type", 0)
    if t == 2:
        lines.append("Type: EIP-1559")
        mf = record.get("maxFeePerGas")
        mp = record.get("maxPriorityFeePerGas")
        if mf is not None:
            lines.append(f"Max Fee: {w3.from_wei(mf, 'gwei')} gwei")
        if mp is not None:
            lines.append(f"Max Priority: {w3.from_wei(mp, 'gwei')} gwei")
    else:
        lines.append("Type: Legacy" if t == 0 else "Type: EIP-2930")
        gp = record.get("gasPrice")
        if gp is not None:
            lines.append(f"Gas Price: {w3.from_wei(gp, 'gwei')} gwei")
    eff = record.get("effectiveGasPrice")
    if eff is not None:
        lines.append(f"Effective Price: {w3.from_wei(eff, 'gwei')} gwei")
    return "\n".join(lines)


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
