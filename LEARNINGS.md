## Context-aware token matching — 2026-03-18 14:57
Implemented context-aware matching with preceded_by and followed_by conditions. Key insight: needed to pass both previous and next tokens to the rule matching function to enable full context awareness. The algorithm needed to be modified to look ahead when processing each token.

## Multi-token emission — 2026-03-18 14:57
Learned that emit can be an array of tokens, not just a single token or scalar value. Each emitted token inherits properties from the original token but can override type and value fields. This enables powerful transformations where one source construct becomes multiple target constructs.