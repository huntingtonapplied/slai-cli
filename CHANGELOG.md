# Changelog

All notable changes to the SLAI CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Pre-1.0 policy:** Minor versions (0.x) may include breaking changes.

## [0.1.0] - Unreleased

### Added
- `slai login` command — authenticate and store API key
- `slai loads list/get/delete` commands for supply chain loads
- `slai shipments list/get` commands
- `slai metrics portfolio` command
- `slai status` command — show system status
- `slai doctor` command — checks Python, config, API connectivity, auth, and shell completion
- `slai api-keys` commands for API key management
- `slai completion` — shell completion for bash, zsh, and fish
- Rich terminal output with table, JSON, and YAML formats
- `--verbose/-v` flag for INFO-level logging to stderr
- `--debug` flag for DEBUG-level logging (HTTP requests)
- `--ci` flag for CI/CD pipeline usage (no color, no spinners, no prompts); auto-detected from `CI`, `GITHUB_ACTIONS`, `GITLAB_CI` env vars
- Distinct exit codes: 2 (auth), 3 (not found), 4 (validation), 5 (network), 6 (server), 130 (SIGINT), 143 (SIGTERM)
- Config validation with typo detection on startup
- Configurable request timeout and retries via `SLAI_TIMEOUT` / `SLAI_MAX_RETRIES` env vars
- SIGTERM signal handling across all commands (clean exit with code 143)
- Top-level KeyboardInterrupt handler as safety net for all commands
- Non-blocking version update check (background thread, 24h throttle, disabled in CI)
- Nuitka standalone binary builds published via SEGA downloads infrastructure
