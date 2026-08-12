Implement a function `parse_duration(s: str) -> int` in solution.py that
converts a duration string into total seconds.

Supported formats:
- "90s" -> 90
- "5m" -> 300
- "2h" -> 7200
- Combined: "1h30m" -> 5400, "2h15m10s" -> 8110

Raise ValueError for malformed input (e.g. empty string, no valid unit).
