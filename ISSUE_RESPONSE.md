issue_number: [self]
status: fixed
comment: Fixed `value_regex` processing in emit rules. The code was checking for `'value'` in the emit dict, but when `value_regex` is used, the structure is `{'value_regex': {...}, 'type': ...}`. Added checks for `'value_regex'` before `'value'` in the emit processing logic.
