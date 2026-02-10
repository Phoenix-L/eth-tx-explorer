"""Tests for core block-transfers logic (get_transaction_index, etc.)."""

import pytest

from eth_tx_explorer.core import (
    _canonical_tx_hash,
    get_transaction_index,
    _transaction_index_from_obj,
)


def test_canonical_tx_hash():
    """_canonical_tx_hash returns lowercase 0x-prefixed hex."""
    class T:
        hash = bytes.fromhex("ab" * 32)
    # Web3.to_hex(bytes) typically returns 0x + hex
    out = _canonical_tx_hash(T())
    assert out.startswith("0x")
    assert out == out.lower()


def test_transaction_index_from_obj_missing():
    """When tx/receipt lack transactionIndex, we get None."""
    assert _transaction_index_from_obj(object()) is None
    assert _transaction_index_from_obj({}) is None


def test_transaction_index_from_obj_camel():
    """Read transactionIndex (camelCase)."""
    class R:
        transactionIndex = 3
    assert _transaction_index_from_obj(R()) == 3


def test_transaction_index_from_obj_snake():
    """Read transaction_index (snake_case)."""
    assert _transaction_index_from_obj({"transaction_index": 5}) == 5


def test_get_transaction_index_block_position_primary():
    """transactionIndex comes from block map first; tx/receipt lack it."""
    class Tx:
        hash = bytes.fromhex("ab" * 32)
    class Receipt:
        pass
    tx_hash_to_index = {_canonical_tx_hash(Tx()): 7}
    idx = get_transaction_index(Tx(), Receipt(), tx_hash_to_index, _canonical_tx_hash(Tx()))
    assert idx == 7


def test_get_transaction_index_fallback_to_receipt():
    """When not in map, use receipt.transactionIndex."""
    class Tx:
        hash = bytes.fromhex("cd" * 32)
    class Receipt:
        transactionIndex = 2
    tx_hash_to_index = {}  # no block mapping
    tx_hash = _canonical_tx_hash(Tx())
    idx = get_transaction_index(Tx(), Receipt(), tx_hash_to_index, tx_hash)
    assert idx == 2


def test_get_transaction_index_block_overrides_receipt():
    """Block position wins over receipt when both exist."""
    class Tx:
        hash = bytes.fromhex("ef" * 32)
    class Receipt:
        transactionIndex = 99
    tx_hash = _canonical_tx_hash(Tx())
    tx_hash_to_index = {tx_hash: 1}
    idx = get_transaction_index(Tx(), Receipt(), tx_hash_to_index, tx_hash)
    assert idx == 1
