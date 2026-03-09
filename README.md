# AI Agent (Python)

Lightweight CLI-based AI coding assistant built with the Gemini API and a sandboxed local tool layer.

This project lets an LLM inspect and modify files inside a constrained working directory, execute Python scripts, and iterate on tasks through function-calling.

## Highlights

- **Gemini function-calling loop** with iterative tool execution
- **Sandboxed filesystem access** (path traversal checks enforced)
- **Controlled Python execution** (`.py` files only, 30s timeout)
- **Configurable limits** for max iterations and max file read size
- **Simple calculator sandbox app** used as an execution target

## Architecture

The agent loop lives in `main.py` and delegates all tool invocations to `call_function.py`.

### Core flow

1. Read CLI prompt (`user_prompt`)
2. Send prompt + tool schemas + system prompt to Gemini
3. If Gemini returns tool calls, dispatch via `call_function()`
4. Append tool responses back to conversation state
5. Repeat until final natural-language response or max iterations reached

### Key modules

- `main.py` - CLI entrypoint and orchestration loop
- `call_function.py` - tool schema registration + runtime dispatcher
- `functions/` - local tools exposed to the model:
  - `get_files_info`
  - `get_file_content`
  - `run_python_file`
  - `write_file`
- `config.py` - runtime constraints (`MAX_CHARS`, `WORKING_DIR`, `MAX_ITERS`)
- `prompts.py` - system instruction passed to Gemini
- `calculator/` - sample project used as the default sandbox

## Project structure

```text
aiagent/
├── main.py
├── call_function.py
├── config.py
├── prompts.py
├── functions/
│   ├── get_files_info.py
│   ├── get_file_content.py
│   ├── run_python_file.py
│   └── write_file.py
├── calculator/
│   ├── main.py
│   └── pkg/
│       ├── calculator.py
│       └── render.py
├── pyproject.toml
└── test_*.py
```

## Requirements

- Python **3.13+**
- Gemini API key

Dependencies are defined in `pyproject.toml`:

- `google-genai==1.12.1`
- `python-dotenv==1.1.0`

## Setup

### 1) Install dependencies

Using `uv`:

```bash
uv sync
```

Or with `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2) Configure environment

Create a `.env` file in the repository root:

```env
GEMINI_API_KEY=your_api_key_here
```

## Usage

Run the agent with a prompt:

```bash
python main.py "List files in the working directory"
```

Verbose mode:

```bash
python main.py "Read calculator/main.py and summarize it" --verbose
```

### CLI arguments

- `user_prompt` (required): user instruction sent to Gemini
- `--verbose` (optional): prints token usage and tool call details

## Tool behavior and safety constraints

All tools receive a `working_directory` (default: `./calculator`) injected by the runtime.

Safety controls implemented in tools:

- **Path confinement** via `os.path.commonpath(...) == working_directory`
- Reject operations outside sandbox directory
- Reject invalid targets (e.g., non-file reads, writing to directories)
- `run_python_file` only executes `*.py` and applies a **30-second timeout**
- `get_file_content` truncates content at `MAX_CHARS`

## Running the sample calculator

The bundled calculator can be run directly:

```bash
python calculator/main.py "3 + 5 * 2"
```

Expected output is JSON-formatted expression + result.

## Testing

Current test files are executable script-style checks (not pytest test suites).

Run them individually:

```bash
python test_get_files_info.py
python test_get_file_content.py
python test_run_python_file.py
python test_write_file.py
```

## Configuration

Edit `config.py` to tune behavior:

- `MAX_CHARS`: max bytes/chars returned by file-read tool
- `WORKING_DIR`: sandbox directory for tool operations
- `MAX_ITERS`: max model-tool interaction rounds

## Known limitations

- No streaming output in CLI
- Limited toolset (no rename/delete/search tools yet)
- Tests are integration-style scripts rather than isolated unit tests
- Error handling is functional but not yet standardized with custom exceptions

## Recommended next improvements

1. Add `pytest` + CI workflow for deterministic automated testing
2. Introduce structured logging and log levels
3. Move model/tool configuration to env-driven settings
4. Add richer toolset (search, patch/diff edits, safe delete/rename)
5. Add retry/backoff for transient API failures

## License

No license file is currently included. Add a `LICENSE` file before public distribution.
