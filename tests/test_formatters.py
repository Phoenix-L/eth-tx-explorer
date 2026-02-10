from decimal import Decimal
from datetime import datetime

import pytest

from eth_tx_explorer.formatters import format_tx_info, format_transfer_summary


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


class _FakeW3:
    """Minimal Web3-like object for format_transfer_summary (from_wei only)."""

    @staticmethod
    def from_wei(value, unit):
        if unit == "ether":
            return Decimal(value) / Decimal(10**18)
        if unit == "gwei":
            return Decimal(value) / Decimal(10**9)
        return value


def test_format_transfer_summary_eth_simple():
    record = {
        "transfer_type": "ETH_SIMPLE_TRANSFER",
        "tx_hash": "0xabc",
        "transaction_index": 0,
        "envelope_type": "EIP-1559",
        "from_addr": "0xAlice",
        "to_addr": "0xBob",
        "eth_value_wei": 1_500_000_000_000_000_000,
        "token_contract": None,
        "token_value": None,
        "gas": 21000,
        "gasUsed": 21000,
        "gasPrice": None,
        "maxFeePerGas": 30_000_000_000,
        "maxPriorityFeePerGas": 1_000_000_000,
        "effectiveGasPrice": 25_000_000_000,
        "tx_type": 2,
    }
    out = format_transfer_summary(_FakeW3(), record)
    assert "TransferType: ETH_SIMPLE_TRANSFER" in out
    assert "Transaction: 0xabc" in out
    assert "TransactionIndex: 0" in out
    assert "EnvelopeType: EIP-1559" in out
    assert "From: 0xAlice" in out
    assert "To: 0xBob" in out
    assert "1.5" in out and "ETH" in out
    assert "Gas: 21000 limit | 21000 used" in out
    assert "Effective Price" in out


def test_format_transfer_summary_erc20():
    record = {
        "transfer_type": "ERC20_TRANSFER",
        "tx_hash": "0xdef",
        "transaction_index": 2,
        "envelope_type": "Legacy",
        "from_addr": "0xA",
        "to_addr": "0xB",
        "eth_value_wei": None,
        "token_contract": "0xToken",
        "token_value": 1000000,
        "gas": 100000,
        "gasUsed": 65000,
        "gasPrice": 20_000_000_000,
        "maxFeePerGas": None,
        "maxPriorityFeePerGas": None,
        "effectiveGasPrice": 18_000_000_000,
        "tx_type": 0,
    }
    out = format_transfer_summary(_FakeW3(), record)
    assert "TransferType: ERC20_TRANSFER" in out
    assert "TransactionIndex: 2" in out
    assert "EnvelopeType: Legacy" in out
    assert "Token Contract: 0xToken" in out
    assert "Token Amount: 1000000 (raw uint256)" in out
    assert "Type: Legacy" in out


def test_format_transfer_summary_contract_creation():
    record = {
        "transfer_type": "CONTRACT_CREATION_WITH_VALUE",
        "tx_hash": "0x789",
        "transaction_index": 1,
        "envelope_type": "EIP-2930",
        "from_addr": "0xDeployer",
        "to_addr": "(contract creation)",
        "eth_value_wei": 50_000_000_000_000_000,
        "token_contract": None,
        "token_value": None,
        "gas": 300000,
        "gasUsed": 245000,
        "gasPrice": None,
        "maxFeePerGas": None,
        "maxPriorityFeePerGas": None,
        "effectiveGasPrice": 20_000_000_000,
        "tx_type": 1,
    }
    out = format_transfer_summary(_FakeW3(), record)
    assert "CONTRACT_CREATION_WITH_VALUE" in out
    assert "To: (contract creation)" in out
    assert "0.05" in out and "ETH" in out
