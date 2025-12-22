# ETH Transaction Explorer

A tool for exploring Ethereum transactions.

## Setup

1. Copy `.env.example` to `.env` and add your RPC URL:
   ```
   cp .env.example .env
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the CLI:
   ```
   python -m src.eth_tx_explorer
   ```

## Usage

12/13: This is clone from github.com

12/22: New Structure (Clean & Professional)

src/eth_tx_explorer/
│
├── cli.py          ← Click commands ONLY
├── rpc.py          ← Web3 connection ONLY
├── core.py         ← Fetch + compute logic
├── formatters.py   ← Text formatting


What Each File Owns (Non-Negotiable Boundaries)
cli.py

Owns
* @click.group
* @cli.command
* argument validation
* printing strings
Must NOT
* call w3.eth.* directly
* calculate gas fees
* format Ethereum objects

rpc.py

Owns
* get_web3()
* provider setup

Must NOT
* know about CLI
* print anything

core.py

Owns
* fetch_block_info(w3, block_number)
* fetch_tx_info(w3, tx_hash)
* unit-testable logic

formatters.py

Owns
* format_tx_info(tx_info)
* format_block_info(block_info)