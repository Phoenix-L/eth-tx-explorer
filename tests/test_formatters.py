from datetime import datetime

import pytest

from eth_tx_explorer.formatters import format_tx_info


def make_good_tx() -> dict:
    """Helper: returns a valid tx dict with all required fields."""
    return {
        "hash": "0xabc123",
        "from": "0xFromAddress",
        "to": "0xToAddress",
        "value_eth": 1.234,
        "gas_used": 21000,
        "fee_eth": 0.00105,
        "status": "SUCCESS",
        "block_number": 12345678,
        "timestamp": datetime(2024, 1, 1, 0, 0, 0),
    }


def test_format_tx_info_basic():
    # Arrange: fake tx data (no Web3, no RPC)
    tx = make_good_tx()

    # Act
    output = format_tx_info(tx)

    # Assert
    assert "Transaction: 0xabc123" in output
    assert "From: 0xFromAddress" in output
    assert "To: 0xToAddress" in output
    assert "Value: 1.234 ETH" in output
    assert "Gas used: 21000" in output
    assert "Fee: 0.00105 ETH" in output
    assert "Status: SUCCESS" in output
    assert "Block: 12345678" in output
    assert "Timestamp (UTC): 2024-01-01 00:00:00" in output


def test_format_tx_info_missing_hash():
    tx = {
        # "hash" is missing
        "from": "0xFromAddress",
        "to": "0xToAddress",
        "value_eth": 1.234,
        "gas_used": 21000,
        "fee_eth": 0.00105,
        "status": "SUCCESS",
        "block_number": 12345678,
        "timestamp": datetime(2024, 1, 1),
    }

    with pytest.raises(ValueError):
        format_tx_info(tx)


def test_format_tx_info_missing_timestamp():
    tx = {
        "hash": "0xabc123",
        "from": "0xFromAddress",
        "to": "0xToAddress",
        "value_eth": 1.234,
        "gas_used": 21000,
        "fee_eth": 0.00105,
        "status": "SUCCESS",
        "block_number": 12345678,
        # "timestamp" missing
    }

    with pytest.raises(ValueError):
        format_tx_info(tx)


def test_format_tx_info_missing_multiple_fields():
    tx = {
        "hash": "0xabc123",
        # everything else missing
    }

    with pytest.raises(ValueError) as exc_info:
        format_tx_info(tx)

    msg = str(exc_info.value)

    # hash should NOT be missing
    assert "hash" not in msg

    # these SHOULD be missing
    assert "from" in msg
    assert "to" in msg
    assert "value_eth" in msg
    assert "gas_used" in msg
    assert "fee_eth" in msg
    assert "status" in msg
    assert "block_number" in msg
    assert "timestamp" in msg

@pytest.mark.parametrize(
    "missing_key",
    [
        "hash",
        "from",
        "to",
        "value_eth",
        "gas_used",
        "fee_eth",
        "status",
        "block_number",
        "timestamp",
    ],
)
def test_format_tx_info_missing_required_field_raises_valueerror(missing_key: str):
    # Arrange: start with a valid tx, then remove one required field
    tx = make_good_tx()
    tx.pop(missing_key)

    # Act + Assert: formatter should crash with ValueError
    with pytest.raises(ValueError) as exc_info:
        format_tx_info(tx)
        
    assert missing_key in str(exc_info.value)    

def test_format_tx_info_missing_field():
    tx = {
        # "hash" is intentionally missing
        "from": "0xFromAddress",
        "to": "0xToAddress",
        "value_eth": 1.0,
        "gas_used": 21000,
        "fee_eth": 0.001,
        "status": "SUCCESS",
        "block_number": 123,
        "timestamp": datetime(2024, 1, 1),
    }

    with pytest.raises(ValueError) as exc_info:
        format_tx_info(tx)

    assert "missing required fields" in str(exc_info.value)
    assert "hash" in str(exc_info.value)
