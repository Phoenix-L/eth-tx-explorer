# ETH Transaction Explorer

A minimal, well-structured Python CLI for inspecting Ethereum transactions and blocks using **Web3.py**.

Designed as a **learning-grade Ethereum tooling project** that mirrors real open-source Ethereum repos:

- clean separation of concerns
- unit-testable core logic
- no RPC calls inside tests
- production-style layout used by real Ethereum projects

This tool is built with awareness of Ethereum’s resource pricing model, distinguishing between short-term flow costs (execution, bandwidth)
and long-term stock costs (state growth), as discussed in Vitalik Buterin’s Blockchain Resource Pricing.
**to be digested and further fine tuned**

## Features
- Inspect a transaction by hash
- Inspect a block by block number
- Show value, gas usage, fees, status, and timestamp
- Show raw event logs for a transaction
- Scan a block and print receipts that contain ERC-20 `Transfer` events
- Strict input validation with clear error messages
- Pure unit tests (no Ethereum node required)


## Project Structure
src/eth_tx_explorer/
├── cli.py          # CLI commands (Click)
├── rpc.py          # Web3 + RPC connection
├── core.py         # Fetch + compute logic
├── formatters.py   # Validation + formatting
│
tests/
├─ test_formatters.py  # Unit tests (pure Python)
│
├─ pyproject.toml  
├─ requirements.txt

### File Responsibilities (Non-Negotiable)
cli.py
**Owns**
- @click.group
- CLI commands and arguments
- Printing formatted output
**Must NOT**
- Call w3.eth.* directly (goal; some legacy commands still do this today—see roadmap)
- Compute gas fees
- Format Ethereum objects

rpc.py
**Owns**
- get_web3()
- RPC provider setup
- Connection validation
**Must NOT**
- Know about CLI
- Print anything

core.py
**Owns**
- fetch_block_info(w3, block_number)
- fetch_tx_info(w3, tx_hash)
- Ethereum data fetching and computation
**Designed to be unit-testable**

formatters.py
**Owns**
- format_tx_info(tx_info)
- Validation of required fields
- Human-readable output formatting



## Installation
**Prerequisites**
- Python ≥ 3.10
- An Ethereum RPC endpoint (Alchemy, Infura, Ankr, etc.)

**Setup**
Copy the example file:
run `cp .env.example .env`

Add your Ethereum RPC URL:
```env:
ETH_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
```
Install dependencies and the CLI in editable (dev) mode:
run `pip install -e .`
This installs the `eth-tx-explorer` command into your environment.


## Usage

**Sanity check**
run `eth-tx-explorer hello`

Expected output:
```text
eth-tx-explorer: hello!
```


**Inspect a transaction by hash**
run `eth-tx-explorer inspect 0xTRANSACTION_HASH`

This prints a formatted summary:
- From / To
- Value (ETH)
- Gas used and fee (ETH)
- Status (`SUCCESS` / `REVERTED`)
- Block number and timestamp (UTC)

**Inspect a block by number**
run `eth-tx-explorer inspect --block 19000000`

This prints:
- Block number
- Timestamp (UTC)
- Transaction count

**Inspect the latest block (and print each tx summary)**
run `eth-tx-explorer inspect`

If you run `inspect` with no arguments, it fetches the latest block (with full transactions) and prints each transaction’s summary:

**Show raw event logs for a transaction**
run `eth-tx-explorer logs 0xTRANSACTION_HASH`

This prints the receipt’s logs (topics + data) using `print_receipt_logs(receipt)`.

**Scan a block for ERC-20 Transfer logs**
run `eth-tx-explorer erc20-logs 19000000`

This iterates all transactions in the block, fetches each receipt, and prints the receipt logs only when a log matches the ERC-20 `Transfer(address,address,uint256)` event signature.



**Running Tests**

Tests are **pure unit tests** and do **not** require an Ethereum node.
run `pytest -v`

What is tested:
- Correct formatting of transaction output
- Validation of missing required fields
- Clear error messages instead of raw `KeyError`

## Design Philosophy

This project follows real Ethereum client/tooling conventions:
- Logic is separated from IO
- RPC access is isolated
- Formatting is deterministic
- Tests never touch the network

This makes the code:
- easier to test
- easier to extend
- easier to contribute to open source

- CLI ≠ logic ≠ RPC
- No formatting inside business logic
- No RPC calls inside tests
- Deterministic, testable output
This mirrors how real Ethereum tooling and clients are structured.

## Roadmap ~ Next Steps
- Add `format_block_info`
- Add unit tests for `core.py` with mocked Web3
- Refactor CLI commands to avoid direct `w3.eth.*` calls (route through `core.py`)
- Add JSON output mode (`--json`)
- Rich console output (tables / colors)