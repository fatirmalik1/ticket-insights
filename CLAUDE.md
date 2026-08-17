# ticket-insights

Rules for working in this repository.

- `mcp_server/` is standard library only. Never add a third-party dependency
  here — the point of this server is that the MCP wire protocol needs
  nothing else.
- `dashboard/` may use `streamlit`. It is a separate, human-facing view of
  the same data in `data/knowledge_base.json` — it is not part of the MCP
  server and has no bearing on the stdlib rule above.
- `data/knowledge_base.json` is fixture data for a live demo. Don't
  "improve" its contents unless asked — the specific wording is chosen on
  purpose.
- Never widen the scope of a ticket. Unrelated problems get their own note.
- Plan before implementing.
