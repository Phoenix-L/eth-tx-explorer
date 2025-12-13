"""Configuration management for the ETH Transaction Explorer."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_rpc_url() -> str:
    """Get the Ethereum RPC URL from environment variables."""
    rpc_url = os.getenv("RPC_URL")
    if not rpc_url:
        raise ValueError("RPC_URL not set in environment variables. Please check your .env file.")
    return rpc_url


