issue_number: [N]
status: won'tfix
comment: The test assertion `output_tokens[2]['value'] == 'PUNCT'` was incorrect because token index 2 is whitespace, not punctuation. The punctuation token is at index 8 and correctly maps to 'PUNCT'. The test has been fixed by changing the index from 2 to 8.
