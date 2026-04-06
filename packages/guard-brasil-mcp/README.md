# @egosbr/guard-brasil-mcp

> Model Context Protocol server for Guard Brasil — LGPD PII detection as a Claude tool

## Install

```bash
npm install -g @egosbr/guard-brasil-mcp
```

## Usage with Claude Code

```bash
claude mcp add guard-brasil -- npx @egosbr/guard-brasil-mcp
```

## Tools

### `guard_inspect`

Full PII inspection with ATRiAN ethics validation.

```json
{
  "text": "Meu CPF é 123.456.789-00"
}
```

### `guard_scan_pii`

Quick PII-only scan.

```json
{
  "text": "Texto para verificar"
}
```

### `guard_check_safe`

Boolean safety check.

```json
{
  "text": "Texto para verificar"
}
```

## License

MIT
