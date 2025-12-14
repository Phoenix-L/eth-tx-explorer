"""Command-line interface for ETH Transaction Explorer."""

import argparse
from eth_tx_explorer.eth_client import EthClient


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Explore Ethereum transactions"
    )
    parser.add_argument(
        "tx_hash",
        nargs="?",
        help="Transaction hash to explore"
    )
    
    args = parser.parse_args()
    
    if args.tx_hash:
        client = EthClient()
        # TODO: Implement transaction exploration
        print(f"Exploring transaction: {args.tx_hash}")
    else:
        parser.print_help()


