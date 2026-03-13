# SmartShiksha — Lessons Learned

## Patterns to Avoid
- **asyncpg version pinning**: asyncpg 0.29.0 has no Windows wheel for Python 3.13. Use 0.31.0+
- **Background terminal CWD**: `isBackground=true` starts from workspace root, not subdirectory. Always prepend `cd backend;` when running backend commands
- **PowerShell string escaping**: f-strings with curly braces in Python one-liners break in PowerShell. Avoid complex f-strings in `curl | python -c` chains
- **Orphaned code after replacements**: When replacing large code blocks, verify no leftover code remains below the new code

## Architecture Decisions
- **MongoDB adapter approach**: MongoSession parses SQLAlchemy Select internals (`_order_by_clauses`, `_limit_clause`, etc.) — fragile but covers all patterns in this codebase. Pinned SQLAlchemy 2.0.25.
- **No local LLM**: User explicitly rejected Ollama. AI features use Groq Cloud API only.
- **SQLite default**: SQLite is the default DB for development and offline use.
