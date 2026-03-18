import yaml
import sys


def load_mapping(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def find_rule(token, prev_token, next_token, rules):
    # Priority order: sequence rules (not implemented yet), context-aware rules, specific rules, value-only rules, type-only rules
    
    # First, try context-aware matches (with preceded_by or followed_by)
    for rule in rules:
        match = rule.get('match', {})
        # Check if this is a context-aware rule
        if 'preceded_by' in match or 'followed_by' in match or 'not_preceded_by' in match or 'not_followed_by' in match:
            if _matches_context_aware_rule(token, prev_token, next_token, match):
                return rule
    
    # Then try specific match (type + value)
    for rule in rules:
        match = rule.get('match', {})
        if 'type' in match and 'value' in match and 'preceded_by' not in match and 'followed_by' not in match and 'not_preceded_by' not in match and 'not_followed_by' not in match:
            if token.get('type') == match['type'] and token.get('value') == match['value']:
                return rule
    
    # Then try value-only match
    for rule in rules:
        match = rule.get('match', {})
        if 'value' in match and 'type' not in match and 'preceded_by' not in match and 'followed_by' not in match and 'not_preceded_by' not in match and 'not_followed_by' not in match:
            if token.get('value') == match['value']:
                return rule
    
    # Finally try general match (type only)
    for rule in rules:
        match = rule.get('match', {})
        if 'type' in match and 'value' not in match and 'preceded_by' not in match and 'followed_by' not in match and 'not_preceded_by' not in match and 'not_followed_by' not in match:
            if token.get('type') == match['type']:
                return rule
                
    return None


def _matches_context_aware_rule(token, prev_token, next_token, match):
    # Extract base match criteria (type and/or value)
    base_type = match.get('type')
    base_value = match.get('value')
    
    # Check if token matches the base criteria
    type_match = base_type is None or token.get('type') == base_type
    value_match = base_value is None or token.get('value') == base_value
    
    if not (type_match and value_match):
        return False
    
    # Check preceded_by condition
    preceded_by = match.get('preceded_by')
    if preceded_by:
        if prev_token is None:
            return False  # No previous token to match against
        preceded_type = preceded_by.get('type')
        preceded_value = preceded_by.get('value')
        
        if preceded_type and prev_token.get('type') != preceded_type:
            return False
        if preceded_value and prev_token.get('value') != preceded_value:
            return False
    
    # Check followed_by condition
    followed_by = match.get('followed_by')
    if followed_by:
        if next_token is None:
            return False  # No next token to match against
        followed_type = followed_by.get('type')
        followed_value = followed_by.get('value')
        
        if followed_type and next_token.get('type') != followed_type:
            return False
        if followed_value and next_token.get('value') != followed_value:
            return False
    
    # Check not_preceded_by condition
    not_preceded_by = match.get('not_preceded_by')
    if not_preceded_by:
        if prev_token is not None:  # Only check if there is a previous token
            not_preceded_type = not_preceded_by.get('type')
            not_preceded_value = not_preceded_by.get('value')
            
            # Check if the previous token matches the not_preceded_by criteria
            type_match = not_preceded_type is None or prev_token.get('type') == not_preceded_type
            value_match = not_preceded_value is None or prev_token.get('value') == not_preceded_value
            
            if type_match and value_match:
                return False  # Should not match if preceded by this token
    
    # Check not_followed_by condition
    not_followed_by = match.get('not_followed_by')
    if not_followed_by:
        if next_token is not None:  # Only check if there is a next token
            not_followed_type = not_followed_by.get('type')
            not_followed_value = not_followed_by.get('value')
            
            # Check if the next token matches the not_followed_by criteria
            type_match = not_followed_type is None or next_token.get('type') == not_followed_type
            value_match = not_followed_value is None or next_token.get('value') == not_followed_value
            
            if type_match and value_match:
                return False  # Should not match if followed by this token
    
    return True


def apply_mapping(tokens, rules, strict=False):
    new_tokens = []
    warnings = []
    
    # Process tokens with context awareness
    for i, token in enumerate(tokens):
        # Get previous and next tokens for context
        prev_token = tokens[i-1] if i > 0 else None
        next_token = tokens[i+1] if i < len(tokens) - 1 else None
        
        rule = find_rule(token, prev_token, next_token, rules)
        if rule is None:
            warnings.append(f"No mapping rule for token: {token}")
            if strict:
                return None, warnings
            new_tokens.append(token)
        else:
            emit = rule.get('emit', 'pass')
            if emit == 'pass':
                new_tokens.append(token)
            elif emit == 'discard':
                # Don't add the token to the output, and don't warn about it in strict mode
                continue
            elif isinstance(emit, list):
                # Handle multi-token emission
                for emitted_token in emit:
                    new_token = dict(token)  # Start with original token properties
                    if isinstance(emitted_token, dict):
                        # Override with properties from the emitted token definition
                        if 'value' in emitted_token:
                            new_token['value'] = emitted_token['value']
                        if 'type' in emitted_token:
                            new_token['type'] = emitted_token['type']
                        # Add any other fields from the emitted token definition
                        for key, value in emitted_token.items():
                            if key not in ['value', 'type']:
                                new_token[key] = value
                    else:
                        # If emitted token is not a dict, treat it as a simple value
                        new_token['value'] = str(emitted_token)
                    new_tokens.append(new_token)
            else:
                new_token = dict(token)
                if 'value' in emit:
                    new_token['value'] = emit['value']
                if 'type' in emit:
                    new_token['type'] = emit['type']
                new_tokens.append(new_token)
    
    return new_tokens, warnings
