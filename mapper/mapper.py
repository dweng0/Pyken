import yaml
import sys
import re


def load_mapping(path):
    with open(path, 'r') as f:
        mapping = yaml.safe_load(f)
    
    # Validate mapping rules
    if 'rules' in mapping:
        rules = mapping['rules']
        for i, rule in enumerate(rules):
            # Check if rule has a match block
            if 'match' not in rule:
                # Rule missing match block - skip with warning (this is handled by pyken.py)
                continue
            
            # Validate emit mode
            emit = rule.get('emit', 'pass')
            
            # Check if emit is a string
            if isinstance(emit, str):
                valid_emit_strings = ['pass', 'discard']
                if emit not in valid_emit_strings:
                    raise ValueError(f"Unknown emit string value '{emit}' in rule {i}: valid values are {valid_emit_strings}")
            
            # Check if emit is a dict
            elif isinstance(emit, dict):
                valid_emit_keys = ['value', 'type', 'value_regex']
                unknown_keys = [k for k in emit.keys() if k not in valid_emit_keys]
                if unknown_keys:
                    raise ValueError(f"Unknown emit key(s) '{unknown_keys}' in rule {i}: valid keys are {valid_emit_keys}")
            
            # emit could be a string, dict, or list
    
    return mapping


def interpolate_value(value, token, matched_tokens=None, sequence_start_pos=None):
    """
    Interpolate {{value}} and {{tokens[N].value}} placeholders in emit values.
    Returns the interpolated value string.
    """
    if not isinstance(value, str):
        return value
    
    result = value
    
    # Replace {{value}} with the matched token's value
    if '{{value}}' in result:
        result = result.replace('{{value}}', token.get('value', ''))
    
    # Replace {{tokens[N].value}} with values from matched sequence tokens
    # Pattern: {{tokens[0].value}}, {{tokens[1].value}}, etc.
    token_pattern = re.compile(r'\{\{tokens\[(\d+)\]\.value\}\}')
    matches = token_pattern.findall(result)
    for idx_str in matches:
        idx = int(idx_str)
        if matched_tokens and sequence_start_pos is not None:
            actual_idx = sequence_start_pos + idx
            if 0 <= actual_idx < len(matched_tokens):
                token_value = matched_tokens[actual_idx].get('value', '')
                result = result.replace(f'{{{{tokens[{idx}].value}}}}', token_value)
    
    return result


def apply_value_regex(value, token, matched_tokens=None, sequence_start_pos=None):
    """
    Apply value_regex substitution to a value string.
    Returns the transformed value string.
    """
    if not isinstance(value, dict):
        return value
    
    value_regex = value.get('value_regex')
    if not value_regex:
        return value
    
    pattern = value_regex.get('pattern')
    replacement = value_regex.get('replacement')
    
    if not pattern or not replacement:
        return value
    
    # Get the source value to apply regex to
    source_value = token.get('value', '')
    
    # Interpolate {{value}} in replacement string
    if '{{value}}' in replacement:
        replacement = replacement.replace('{{value}}', source_value)
    
    # Apply the regex substitution
    try:
        result = re.sub(pattern, replacement, source_value)
    except re.error:
        # If regex is invalid, return original
        return value
    
    return result


def find_rule(token, prev_token, next_token, rules, tokens=None, pos=None):
    # Priority order: sequence rules, context-aware rules, specific rules, value-only rules, type-only rules
    
    # First, try sequence matches (highest priority)
    for rule in rules:
        match = rule.get('match', {})
        if 'sequence' in match:
            if tokens and pos is not None:
                seq_match_result = _matches_sequence_rule(pos, tokens, match['sequence'])
                if seq_match_result:
                    return rule, seq_match_result  # Return rule and match length
    
    # Then, try context-aware matches (with preceded_by or followed_by)
    for rule in rules:
        match = rule.get('match', {})
        # Check if this is a context-aware rule
        if 'preceded_by' in match or 'followed_by' in match or 'not_preceded_by' in match or 'not_followed_by' in match:
            if _matches_context_aware_rule(token, prev_token, next_token, match):
                return rule, 1  # Return rule and match length of 1
    
    # Then try specific match (type + value)
    for rule in rules:
        match = rule.get('match', {})
        if 'type' in match and 'value' in match and 'preceded_by' not in match and 'followed_by' not in match and 'not_preceded_by' not in match and 'not_followed_by' not in match and 'sequence' not in match:
            if token.get('type') == match['type'] and token.get('value') == match['value']:
                return rule, 1  # Return rule and match length of 1
    
    # Then try value-only match
    for rule in rules:
        match = rule.get('match', {})
        if 'value' in match and 'type' not in match and 'preceded_by' not in match and 'followed_by' not in match and 'not_preceded_by' not in match and 'not_followed_by' not in match and 'sequence' not in match:
            if token.get('value') == match['value']:
                return rule, 1  # Return rule and match length of 1
    
    # Finally try general match (type only)
    for rule in rules:
        match = rule.get('match', {})
        if 'type' in match and 'value' not in match and 'preceded_by' not in match and 'followed_by' not in match and 'not_preceded_by' not in match and 'not_followed_by' not in match and 'sequence' not in match:
            if token.get('type') == match['type']:
                return rule, 1  # Return rule and match length of 1
                
    return None, 1  # Return None and default match length of 1


def _matches_sequence_rule(start_pos, tokens, sequence_pattern):
    """
    Check if tokens starting at start_pos match the given sequence pattern.
    Returns the number of tokens matched, or 0 if no match.
    """
    if start_pos + len(sequence_pattern) > len(tokens):
        return 0  # Not enough tokens left to match the sequence
    
    for i, pattern_item in enumerate(sequence_pattern):
        token = tokens[start_pos + i]
        
        # Check type match
        if 'type' in pattern_item:
            if token.get('type') != pattern_item['type']:
                return 0
        
        # Check value match
        if 'value' in pattern_item:
            if token.get('value') != pattern_item['value']:
                return 0
    
    return len(sequence_pattern)  # Return the number of tokens matched


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
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        # Get previous and next tokens for context
        prev_token = tokens[i-1] if i > 0 else None
        # For sequence matching, we need to consider the possibility of multi-token matches
        # We'll get the next token based on whether this token is part of a sequence match
        next_token = tokens[i+1] if i + 1 < len(tokens) else None
        
        rule, match_len = find_rule(token, prev_token, next_token, rules, tokens, i)
        
        if rule is None:
            warnings.append(f"No mapping rule for token: {token}")
            if strict:
                return None, warnings
            new_tokens.append(token)
            i += 1
        else:
            # If this is a sequence match, process all the matched tokens together
            if match_len > 1:
                # Get the matched tokens for potential use in emit processing
                matched_tokens = tokens[i:i+match_len]
                
                emit = rule.get('emit', 'pass')
                if emit == 'pass':
                    # With pass_through, keep all matched tokens
                    new_tokens.extend(matched_tokens)
                elif emit == 'discard':
                    # Don't add any of the matched tokens to the output
                    pass  # Just skip adding them
                elif isinstance(emit, list):
                    # Handle multi-token emission
                    for emitted_token in emit:
                        # For sequence matches, use the matched_tokens for interpolation
                        new_token = {}
                        if isinstance(emitted_token, dict):
                            # Copy base properties from first matched token (or current token)
                            if matched_tokens:
                                new_token = dict(matched_tokens[0])
                            else:
                                new_token = dict(token)
                            
                            # Apply emit definition with value interpolation
                            # First check if emit contains value_regex
                            if 'value_regex' in emitted_token:
                                # value_regex is present - apply it to the matched token
                                processed_value = apply_value_regex(
                                    emitted_token,  # Pass the whole emit dict
                                    matched_tokens[0] if matched_tokens else token,
                                    matched_tokens,
                                    i if matched_tokens else None
                                )
                                if isinstance(processed_value, str):
                                    new_token['value'] = interpolate_value(
                                        processed_value,
                                        matched_tokens[0] if matched_tokens else token,
                                        matched_tokens,
                                        i if matched_tokens else None
                                    )
                                else:
                                    new_token['value'] = processed_value
                            elif 'value' in emitted_token:
                                # value is present - use it directly with interpolation
                                new_token['value'] = interpolate_value(
                                    emitted_token['value'],
                                    matched_tokens[0] if matched_tokens else token,
                                    matched_tokens,
                                    i if matched_tokens else None
                                )
                            if 'type' in emitted_token:
                                new_token['type'] = emitted_token['type']
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
                    # Single token emission for the entire sequence
                    new_token = {}
                    if matched_tokens:
                        new_token = dict(matched_tokens[0])  # Start with first token properties
                    else:
                        new_token = dict(token)
                    
                    # Handle value_regex first (it produces a string, not a dict)
                    if 'value_regex' in emit:
                        processed_value = apply_value_regex(
                            emit,
                            matched_tokens[0] if matched_tokens else token,
                            matched_tokens,
                            i if matched_tokens else None
                        )
                        if isinstance(processed_value, str):
                            new_token['value'] = interpolate_value(
                                processed_value,
                                matched_tokens[0] if matched_tokens else token,
                                matched_tokens,
                                i if matched_tokens else None
                            )
                        else:
                            new_token['value'] = processed_value
                    elif 'value' in emit:
                        processed_value = apply_value_regex(
                            emit['value'],
                            matched_tokens[0] if matched_tokens else token,
                            matched_tokens,
                            i if matched_tokens else None
                        )
                        # processed_value should be a string from interpolation or direct result
                        if isinstance(processed_value, str):
                            new_token['value'] = interpolate_value(
                                processed_value,
                                matched_tokens[0] if matched_tokens else token,
                                matched_tokens,
                                i if matched_tokens else None
                            )
                        else:
                            new_token['value'] = processed_value
                    
                    if 'type' in emit:
                        new_token['type'] = emit['type']
                    new_tokens.append(new_token)
                
                # Advance the counter by the number of matched tokens
                i += match_len
            else:
                # Regular single-token processing
                emit = rule.get('emit', 'pass')
                if emit == 'pass':
                    new_tokens.append(token)
                elif emit == 'discard':
                    # Don't add the token to the output, and don't warn about it in strict mode
                    pass
                elif isinstance(emit, list):
                    # Handle multi-token emission
                    for emitted_token in emit:
                        new_token = dict(token)  # Start with original token properties
                        if isinstance(emitted_token, dict):
                            # Override with properties from the emitted token definition
                            # Check for value_regex first
                            if 'value_regex' in emitted_token:
                                processed_value = apply_value_regex(
                                    emitted_token,
                                    token,
                                    None,
                                    None
                                )
                                if isinstance(processed_value, str):
                                    new_token['value'] = interpolate_value(
                                        processed_value,
                                        token,
                                        None,
                                        None
                                    )
                                else:
                                    new_token['value'] = processed_value
                            elif 'value' in emitted_token:
                                processed_value = apply_value_regex(
                                    emitted_token['value'], 
                                    token,
                                    None,
                                    None
                                )
                                if isinstance(processed_value, str):
                                    new_token['value'] = interpolate_value(
                                        processed_value,
                                        token,
                                        None,
                                        None
                                    )
                                else:
                                    new_token['value'] = processed_value
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
                    # Handle value_regex first (it's a dict with 'pattern' and 'replacement')
                    if 'value_regex' in emit:
                        processed_value = apply_value_regex(
                            emit,
                            token,
                            None,
                            None
                        )
                        if isinstance(processed_value, str):
                            new_token['value'] = interpolate_value(
                                processed_value,
                                token,
                                None,
                                None
                            )
                        else:
                            new_token['value'] = processed_value
                    elif 'value' in emit:
                        processed_value = apply_value_regex(
                            emit['value'],
                            token,
                            None,
                            None
                        )
                        if isinstance(processed_value, str):
                            new_token['value'] = interpolate_value(
                                processed_value,
                                token,
                                None,
                                None
                            )
                        else:
                            new_token['value'] = processed_value
                    if 'type' in emit:
                        new_token['type'] = emit['type']
                    new_tokens.append(new_token)
                
                i += 1
    
    return new_tokens, warnings
