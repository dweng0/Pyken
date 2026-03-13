import yaml
import sys


def load_mapping(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def find_rule(token, rules):
    # Try specific match first (type + value)
    for rule in rules:
        match = rule.get('match', {})
        if 'type' in match and 'value' in match:
            if token.get('type') == match['type'] and token.get('value') == match['value']:
                return rule
    # Try general match (type only)
    for rule in rules:
        match = rule.get('match', {})
        if 'type' in match and 'value' not in match:
            if token.get('type') == match['type']:
                return rule
    return None


def apply_mapping(tokens, rules, strict=False):
    new_tokens = []
    warnings = []
    for token in tokens:
        rule = find_rule(token, rules)
        if rule is None:
            warnings.append(f"No mapping rule for token: {token}")
            if strict:
                return None, warnings
            new_tokens.append(token)
        else:
            emit = rule.get('emit', 'pass')
            if emit == 'pass':
                new_tokens.append(token)
            else:
                new_token = dict(token)
                if 'value' in emit:
                    new_token['value'] = emit['value']
                if 'type' in emit:
                    new_token['type'] = emit['type']
                new_tokens.append(new_token)
    return new_tokens, warnings
