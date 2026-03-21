import argparse
import json
import sys
import yaml
from mapper.mapper import load_mapping, apply_mapping


def main():
    parser = argparse.ArgumentParser(description="Transform a JSON token stream using a YAML mapping file.")
    parser.add_argument('mapping_file', type=str, help='Path to the YAML mapping file.')
    parser.add_argument('--input', type=str, default=None, help='Path to a JSON token stream file (default: stdin).')
    parser.add_argument('--tokens', action='store_true', help='Output a JSON token stream instead of source text.')
    parser.add_argument('--strict', action='store_true', help='Fail if any token has no mapping rule.')
    args = parser.parse_args()

    # Load mapping
    try:
        mapping = load_mapping(args.mapping_file)
    except FileNotFoundError:
        print(f"Error: mapping file not found: {args.mapping_file}", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: failed to parse YAML mapping file: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    rules = mapping.get('rules', [])

    # Load tokens
    try:
        if args.input:
            with open(args.input, 'r') as f:
                raw = f.read()
        else:
            raw = sys.stdin.read()
        tokens = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Error: failed to parse JSON token stream: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Validate that tokens is an array
    if not isinstance(tokens, list):
        print("Error: token stream must be a JSON array", file=sys.stderr)
        sys.exit(1)

    # Validate token shape - each token must be a dict with 'type' and 'value' keys
    for i, token in enumerate(tokens):
        if not isinstance(token, dict):
            print(f"Error: token at index {i} is not a JSON object: got {type(token).__name__}", file=sys.stderr)
            sys.exit(1)
        if 'type' not in token:
            print(f"Error: token at index {i} is missing required 'type' key", file=sys.stderr)
            sys.exit(1)
        if 'value' not in token:
            print(f"Error: token at index {i} is missing required 'value' key", file=sys.stderr)
            sys.exit(1)

    # Apply mapping
    new_tokens, warnings = apply_mapping(tokens, rules, strict=args.strict)

    for w in warnings:
        print(f"Warning: {w}", file=sys.stderr)

    if new_tokens is None:
        # strict mode failure
        sys.exit(1)

    # Output
    if args.tokens:
        print(json.dumps(new_tokens))
    else:
        print(''.join(t['value'] for t in new_tokens), end='')


if __name__ == '__main__':
    main()
