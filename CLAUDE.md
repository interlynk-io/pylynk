# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`pylynk` is a command-line utility for interfacing with Interlynk's SAAS platform. It provides functionality to manage products, versions, and SBOMs (Software Bill of Materials) through a GraphQL API.

## Development Setup

### Install dependencies
```bash
pip3 install -r requirements.txt
```

### Running the application
```bash
python3 pylynk.py --help
```

### Docker usage
```bash
docker build -t pylynk .
docker run -e INTERLYNK_SECURITY_TOKEN ghcr.io/interlynk-io/pylynk <command>
```

## Architecture Overview

The codebase is now organized into a modular structure:

```
pylynk/
├── __main__.py           # Main entry point
├── cli/
│   ├── parser.py         # Argument parsing logic
│   └── commands/         # Individual command implementations
│       ├── products.py   # Products listing
│       ├── versions.py   # Versions listing
│       ├── status.py     # SBOM status
│       ├── upload.py     # SBOM upload
│       └── download.py   # SBOM download
├── api/
│   ├── client.py         # API client (refactored from LynkContext)
│   ├── queries.py        # GraphQL query definitions
│   └── mutations.py      # GraphQL mutation definitions
├── formatters/
│   ├── json_formatter.py # JSON output formatting
│   └── table_formatter.py # Table output formatting
├── utils/
│   ├── time.py          # Time conversion utilities
│   ├── config.py        # Configuration management
│   └── validators.py    # Input validation
└── constants.py         # Constants and defaults
```

### Key Components:

1. **API Layer** (`api/`):
   - `client.py`: Clean API client interface with methods for all operations
   - `queries.py`: GraphQL queries separated for maintainability
   - `mutations.py`: GraphQL mutations for upload operations

2. **CLI Layer** (`cli/`):
   - `parser.py`: Centralized argument parsing
   - `commands/`: Separate modules for each subcommand

3. **Utilities** (`utils/`):
   - `config.py`: Configuration management from args and environment
   - `validators.py`: Input validation logic
   - `time.py`: Time formatting utilities

4. **Formatters** (`formatters/`):
   - Separate modules for JSON and table output formatting

## Key Environment Variables

- `INTERLYNK_SECURITY_TOKEN` - Required for authentication
- `INTERLYNK_API_URL` - Override API endpoint (default: https://api.interlynk.io/lynkapi)

## Common Development Tasks

### Adding a new command
1. Add the subcommand parser in `cli/parser.py`
2. Create a new command module in `cli/commands/`
3. Add any required GraphQL queries to `api/queries.py` or mutations to `api/mutations.py`
4. Implement the API interaction method in `api/client.py`
5. Add the command execution in `__main__.py`

### Error handling patterns
- API errors are logged using the logging module
- HTTP status codes are checked for all requests
- GraphQL errors are extracted from response JSON
- Input validation is handled in `utils/validators.py`

### Testing API changes locally
```bash
export INTERLYNK_API_URL=http://localhost:3000/lynkapi
export INTERLYNK_SECURITY_TOKEN=your_test_token
python3 pylynk.py prods --verbose
```

### Module imports
The modular structure allows for clean imports:
```python
from pylynk.api.client import LynkAPIClient
from pylynk.utils.config import Config
from pylynk.formatters.json_formatter import format_json
```