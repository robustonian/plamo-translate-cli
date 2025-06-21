# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `plamo-translate-cli`, a command-line interface for translation using the plamo-2-translate model with local execution. The project provides:

- Translation between 16+ languages using PLaMo-2-translate model
- MLX backend optimized for macOS Apple Silicon
- MCP (Model Context Protocol) server for integration with Claude Desktop and other MCP clients
- Both interactive and batch translation modes

## Architecture

The codebase follows a client-server architecture:

### Core Components

- **main.py**: Entry point and CLI argument parsing, handles both client and server modes
- **servers/mlx/server.py**: FastMCP server implementation using MLX framework for model inference
- **clients/translate.py**: MCP client that communicates with the server via HTTP
- **servers/utils.py**: Shared utilities, configuration management, and data structures

### Key Design Patterns

- **Client-Server Model**: The CLI can start a background MCP server process and communicate with it via HTTP, allowing model loading to be amortized across multiple translation requests
- **Streaming Support**: Both server and client support streaming translation output for real-time feedback
- **Auto-Detection**: If no server is running, the CLI automatically starts one in daemon mode
- **Port Management**: Automatic port detection and configuration persistence

## Development Commands

### Setup
```bash
uv sync
source .venv/bin/activate
```

### Testing
```bash
pytest tests/
```

### Linting
```bash
ruff check src/ tests/
```

### Building and Deployment
```bash
bash scripts/deploy.sh
```

## Configuration

Environment variables for tuning model behavior:
- `PLAMO_TRANSLATE_CLI_TEMP`: Temperature for text generation
- `PLAMO_TRANSLATE_CLI_TOP_P`: Top-p sampling probability  
- `PLAMO_TRANSLATE_CLI_TOP_K`: Top-k sampling number
- `PLAMO_TRANSLATE_CLI_REPETITION_PENALTY`: Repetition penalty
- `PLAMO_TRANSLATE_CLI_REPETITION_CONTEXT_SIZE`: Context size for repetition penalty
- `PLAMO_TRANSLATE_CLI_SERVER_START_PORT`/`PLAMO_TRANSLATE_CLI_SERVER_END_PORT`: Port range for server

## Key Implementation Details

- Model loading uses MLX-LM with custom chat template from `assets/chat_template.jinja2`
- Server configuration is persisted and shared between client/server instances
- Interactive mode includes readline history support
- Supports both streaming and batch translation modes
- MLX backend supports multiple precisions: 4bit, 8bit, bf16