# MCP server plan (later)

Goal: any MCP-capable agent (Claude Code, Claude Desktop, Cursor, ...) can find, check and render music from this library without reading docs. Not built yet. The CLI (`src/musiclib`) already does the work, so the server is a thin wrapper.

## Shape

- Package: `src/musiclib/mcp_server.py`, entry point `musiclib-mcp` (stdio transport).
- Dependency: the official `mcp` Python SDK (`FastMCP`), as an optional extra: `pip install -e .[mcp]`. The core CLI stays stdlib only.
- Data: the same `Library` class (local checkout → `$MUSICLIB_BASE` → Pages). Read-only except render output.
- Client config:
  ```json
  {"mcpServers": {"musiclib": {"command": "musiclib-mcp", "env": {"MUSICLIB_ROOT": "/path/to/music-library"}}}}
  ```

## Tools

| tool | input | output | wraps |
|---|---|---|---|
| `search` | `query?`, `genre?`, `mood?`, `energy?`, `licence?[]`, `has_score?`, `has_recording?`, `renderable?`, `top?`, `limit=20` | catalog rows (id, title, composer, catalog, licence_status, flags, URLs) | `Library.search` |
| `get` | `id` | full item JSON | `Library.get` |
| `licence_check` | `id`, `use`: `recording` \| `render` \| `preview` | `{ok: bool, status, needs_credit, credit_text, caveats[]}`. `ok` = false for unverified / sharealike / flagged on the part actually used | new: small function over `recording_status` / `score_status` / `legal_flags` |
| `render` | `id` or `midi_path`, `start?`, `duration?`, `format=mp3`, `lufs=-16`, `member?` | output file path + licence of the render | `audio.render` |
| `download` (optional) | `id`, `what` | local file paths | `cmd_download` logic |

Resources (optional): `musiclib://catalog` (catalog.json) and `musiclib://item/{id}`.

## Rules the server enforces

- `render` and `download` always return `licence_status` and `credit_text`; `unverified` items need `force: true`.
- Outputs go to a configurable directory (`$MUSICLIB_OUT`, default `./renders`); no paths outside it.
- No network writes, no secrets, nothing from MuseScore.com.

## Cost / when

About 150 lines plus tests, once the CLI interface settles (after expansion batch 1). Build it when a second agent besides Claude Code needs the library, or when `arrange` gets a real backend (an `arrange` tool would wrap `$MUSICLIB_ARRANGE_CMD`).
