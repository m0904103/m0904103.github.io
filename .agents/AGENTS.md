# Behavioral Guidelines

## Preventing Hallucinations in Market Data
When generating simulated market views, influencer sentiments, or financial updates via prompts or scheduled tasks:
*   **NEVER** hallucinate or invent specific index point values (e.g., S&P 500 at 5400).
*   **ALWAYS** use relative terms like "key support level", "moving average", "recent highs", or "quarterly line" to describe the market position, UNLESS you have explicitly fetched live data to back up the exact numbers.
*   This prevents factual inaccuracies (such as quoting a 2024 index value for a 2026 update).
