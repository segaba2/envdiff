# envdiff

A CLI tool to compare `.env` files across environments and flag missing or mismatched keys.

---

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/envdiff.git
cd envdiff && pip install .
```

---

## Usage

Compare two `.env` files and see what's different:

```bash
envdiff .env.development .env.production
```

**Example output:**

```
Missing in .env.production:
  - DEBUG
  - LOCAL_DB_URL

Mismatched keys:
  - APP_PORT: development=3000 | production=8080

✔ All other keys match.
```

### Options

| Flag | Description |
|------|-------------|
| `--strict` | Exit with non-zero code if any diff is found |
| `--keys-only` | Only compare key names, ignore values |
| `--output json` | Output results as JSON |

```bash
envdiff .env.staging .env.production --strict --output json
```

---

## Why envdiff?

Shipping to production with missing environment variables is a common source of bugs. `envdiff` makes it easy to catch configuration drift before it becomes an incident.

---

## License

[MIT](LICENSE) © 2024 yourname