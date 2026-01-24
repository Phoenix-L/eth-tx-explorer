"""REPL helper: Auto-setup Web3 instance and common imports.

Usage in Python REPL:
    from eth_tx_explorer.repl_helper import *
    
This will make available:
    - w3: Web3 instance (connected and ready to use)
    - fetch_block_info: Fetch block information
    - fetch_tx_info: Fetch transaction information
    - format_tx_info: Format transaction info as string
    - print_receipt_logs: Print receipt logs
    - print_erc20_logs: Print ERC-20 Transfer logs for a block
"""

from eth_tx_explorer.rpc import get_web3

# Create w3 instance in global namespace
w3 = get_web3()

# Import common functions from core.py
try:
    from eth_tx_explorer.core import (
        fetch_block_info,
        fetch_tx_info,
        print_receipt_logs,
        print_erc20_logs,
    )
    from eth_tx_explorer.formatters import format_tx_info
except ImportError as e:
    # Graceful handling if core.py doesn't exist or functions are missing
    import warnings
    warnings.warn(
        f"Could not import functions from core.py: {e}. "
        "Only 'w3' is available.",
        ImportWarning
    )
