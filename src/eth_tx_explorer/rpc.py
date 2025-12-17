from web3 import Web3
from dotenv import load_dotenv
from pathlib import Path
import os


# Load .env from project root (once)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def get_web3() -> Web3:
    """
    Create and return a Web3 instance using ETH_RPC_URL from .env.
    """
    rpc_url = os.getenv("ETH_RPC_URL")
    if not rpc_url:
        raise RuntimeError(
            "ETH_RPC_URL environment variable not set"
        )

    w3 = Web3(Web3.HTTPProvider(rpc_url))

    if not w3.is_connected():
        raise RuntimeError("Failed to connect to Ethereum RPC")

    return w3

