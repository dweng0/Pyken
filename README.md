[![Evolution](https://github.com/dweng0/Pyken/actions/workflows/evolve.yml/badge.svg)](https://github.com/dweng0/Pyken/actions/workflows/evolve.yml)
[![BAADD](baadd.svg)](https://github.com/dweng0/BAADD)

# Pyken

A token stream transformer. Pyken takes a JSON token stream — from [PyLex](https://github.com/dweng0/PyLex) or any compatible tokenizer — and remaps tokens according to a YAML mapping file, enabling token-level transpilation between languages or dialects.

### Features

- **Language-agnostic** — works with any `[{"type": "...", "value": "..."}]` JSON token stream
- **YAML-configured mappings** — define remapping rules without touching code
- **Two output modes** — reconstructed source text or a new JSON token stream
- **Pipeline-friendly** — designed to chain with PyLex and other tools
- **Strict mode** — fail fast if any token has no mapping rule
- **Bundled mappings** — Python → JavaScript, JavaScript → TypeScript, Python → Pseudocode

---

## Installation

```bash
git clone https://github.com/dweng0/Pyken.git
cd Pyken
pip install -r requirements.txt
```

---

## Usage

Pyken reads a JSON token stream from **stdin** (or `--input`) and writes transformed output to **stdout**.

### With PyLex

```bash
# Tokenise Python source, remap to JavaScript
python3 main.py hello.py lexers/python.yaml | python3 pyken.py mappings/python-to-javascript.yaml

# Tokenise Python source, remap to pseudocode
python3 main.py hello.py lexers/python.yaml | python3 pyken.py mappings/python-to-pseudocode.yaml
```

### From a token file

```bash
# Save tokens first
python3 main.py hello.py lexers/python.yaml > tokens.json

# Then remap
python3 pyken.py mappings/python-to-javascript.yaml --input tokens.json
```

### Output a new token stream instead of source text

```bash
python3 main.py foo.py lexers/python.yaml | python3 pyken.py mappings/python-to-javascript.yaml --tokens
```

This is useful for chaining multiple remapping steps:

```bash
python3 main.py foo.py lexers/python.yaml \
  | python3 pyken.py mappings/python-to-javascript.yaml --tokens \
  | python3 pyken.py mappings/javascript-to-typescript.yaml
```

### Strict mode

By default, tokens with no matching rule pass through unchanged with a warning on stderr. Use `--strict` to treat unmapped tokens as errors:

```bash
python3 main.py foo.py lexers/python.yaml | python3 pyken.py mappings/my-mapping.yaml --strict
```

---

## Example

**Input (Python):**
```python
def greet(name):
    if name:
        print("Hello " + name)
    return True
```

**After remapping with `python-to-javascript.yaml`:**
```javascript
function greet(name):
    if name:
        console.log("Hello " + name)
    return true
```

**After remapping with `python-to-pseudocode.yaml`:**
```
FUNCTION greet(name):
    IF name:
        OUTPUT("Hello " + name)
    RETURN YES
```

---

## Bundled Mappings

| File | From | To | What it does |
|------|------|----|--------------|
| `python-to-javascript.yaml` | Python | JavaScript | Remaps keywords: `def`→`function`, `elif`→`else if`, `True`→`true`, `None`→`null`, `print`→`console.log`, etc. |
| `javascript-to-typescript.yaml` | JavaScript | TypeScript | Remaps `var`→`let`, passes everything else through |
| `python-to-pseudocode.yaml` | Python | Pseudocode | Replaces keywords with plain English: `def`→`FUNCTION`, `if`→`IF`, `return`→`RETURN`, etc. |

---

## Writing Your Own Mapping

A mapping file is a YAML file with a list of rules. Each rule has a `match` block and an `emit` block.

```yaml
from: python
to: javascript
rules:
  # Match by type AND value (specific)
  - match:
      type: keyword
      value: "def"
    emit:
      value: "function"

  # Match by type only (general — catches anything not matched above)
  - match:
      type: keyword
    emit: pass

  # Pass whitespace and identifiers through unchanged
  - match:
      type: whitespace
    emit: pass
  - match:
      type: identifier
    emit: pass
```

**Rule matching:**
- Specific rules (type + value) are always tried before general rules (type only)
- `emit: pass` passes the token through unchanged
- Omitting `value` in `emit` keeps the original value
- Omitting `type` in `emit` keeps the original type

---

### Emit modes

#### `emit: pass` — keep the token unchanged

```yaml
- match:
    type: identifier
  emit: pass
```

#### `emit: discard` — remove the token entirely

Use this to drop tokens that have no equivalent in the target language.

```yaml
# Remove Python's trailing colon from block statements
- match:
    type: punctuation
    value: ":"
  emit: discard
```

The token is silently removed from the output. No warning is printed.

#### Replace value and/or type

```yaml
- match:
    type: keyword
    value: "def"
  emit:
    value: "function"       # replace value, keep type

- match:
    type: keyword
    value: "True"
  emit:
    type: boolean           # replace type, keep value

- match:
    type: keyword
    value: "None"
  emit:
    type: keyword
    value: "null"           # replace both
```

#### `emit: tokens` — expand one token into many

Use this when a single source token maps to multiple target tokens. The matched token is replaced by the full list.

```yaml
# Python INDENT becomes "{\n" in JavaScript
- match:
    type: indent
  emit:
    tokens:
      - type: punctuation
        value: " {"
      - type: newline
        value: "\n"

# Python DEDENT becomes a closing brace
- match:
    type: dedent
  emit:
    tokens:
      - type: punctuation
        value: "}"
      - type: newline
        value: "\n"
```

---

### Context-aware matching

Add `preceded_by` to a rule to match a token only when a specific token immediately precedes it. This lets you apply different rules to the same token type and value depending on where it appears.

```yaml
# Remove ":" only when it closes a block header (preceded by ")")
# Leaves ":" in dict literals alone
- match:
    type: punctuation
    value: ":"
    preceded_by:
      type: punctuation
      value: ")"
  emit: discard

# All other ":" (e.g. in dicts) pass through unchanged
- match:
    type: punctuation
    value: ":"
  emit: pass
```

**Rule priority** (highest to lowest):
1. Context-aware rules (type + value + `preceded_by`) — most specific
2. Specific rules (type + value)
3. General rules (type only)

---

## Running Tests

```bash
python3 -m pytest tests/ -v
```

---

## How It Works

Pyken is intentionally minimal. The core pipeline is:

1. Read a `[{"type": "...", "value": "..."}]` JSON array from stdin or a file
2. For each token, find the best matching rule in the mapping YAML (specific before general)
3. Apply the `emit` transformation to produce a new token
4. Output either the reconstructed source text (join all values) or a new JSON token stream

Because Pyken only cares about the `{type, value}` contract, it works with PyLex or any other tokenizer that produces compatible output.

---

## Project Roadmap

| Stage | Description | Status |
|-------|-------------|--------|
| Token-level remapping | Remap keyword values and types via YAML | Done |
| Bundled language mappings | Python→JS, JS→TS, Python→Pseudocode | Done |
| Pipeline chaining | `--tokens` output for multi-step transforms | Done |
| Discard tokens | `emit: discard` to drop tokens with no target equivalent | In progress |
| Multi-token emission | One source token expands to multiple target tokens | In progress |
| Context-aware matching | `preceded_by` to disambiguate same token in different contexts | In progress |
| Custom output language | Define a new language target from scratch | Planned |

---

## Contributing

Contributions are welcome — especially new mapping files for language pairs not yet covered.

Fork the repo, add your mapping under `mappings/`, and open a pull request.

---

## License

MIT
