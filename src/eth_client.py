"""Ethereum client for interacting with the blockchain."""

from typing import Optional
from eth_tx_explorer.config import get_rpc_url


class EthClient:
    """Client for interacting with Ethereum blockchain."""

    def __init__(self, rpc_url: Optional[str] = None):
        """Initialize the Ethereum client.
        
        Args:
            rpc_url: Optional RPC URL. If not provided, will use RPC_URL from config.
        """
        self.rpc_url = rpc_url or get_rpc_url()
        # TODO: Initialize web3 connection here

    def get_transaction(self, tx_hash: str):
        """Get transaction details by hash.
        
        Args:
            tx_hash: Transaction hash to look up.
            
        Returns:
            Transaction details.
        """
        # TODO: Implement transaction lookup
        raise NotImplementedError("Transaction lookup not yet implemented")


