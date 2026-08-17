# ticket-insights

A small internal knowledge base of past resolved support tickets, exposed
two ways:

- **`dashboard/app.py`** — a Streamlit page a person opens in a browser tab
  to search past resolutions before filing a new ticket.
- **`mcp_server/ticket_kb_server.py`** — the same data, exposed as an MCP
  server so an agent can query it directly instead of a human searching by
  hand. Standard library only, no SDK — see the file for why.

Both read `data/knowledge_base.json`.

## Run the dashboard

```bash
pip install streamlit
streamlit run dashboard/app.py
```

## Run the MCP server standalone (see the raw protocol)

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python3 mcp_server/ticket_kb_server.py
```

## Register it with Claude Code

```bash
claude mcp add ticket-kb -- python3 "$(pwd)/mcp_server/ticket_kb_server.py"
```

Then restart the session and check `/mcp` lists it.
