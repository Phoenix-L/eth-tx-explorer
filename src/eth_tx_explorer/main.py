from web3 import Web3
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
#from pathlib import Path

# Load .env located in project root
#env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv() # load .env file if present

def get_web3():
    rpc_url = os.getenv("ETH_RPC_URL")
    if not rpc_url:
        raise RuntimeError("ETH_RPC_URL env var not set")
    return Web3(Web3.HTTPProvider(rpc_url))

import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--block", type=int, help="Block number")
    return parser.parse_args()


def main():
    print("eth-tx-explorer: hello Ethereum!")
    
    web3 = get_web3()
    args = parse_args()
    block_number = args.block if args.block is not None else web3.eth.block_number
    block = web3.eth.get_block(block_number)

    ts = datetime.fromtimestamp(block["timestamp"], tz=timezone.utc)
    tx_count = len(block["transactions"])

    print(f"Block {block['number']}")
    print(f"\nTimestamp: {ts.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"\nTx count: {tx_count}")

if __name__ == "__main__":
    main()
