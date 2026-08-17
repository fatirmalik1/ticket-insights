#!/usr/bin/env python3
"""
ticket_kb_server.py — a minimal MCP server, standard library only.

This is deliberately NOT built with the official MCP Python SDK (FastMCP).
The point of this file is to make the wire protocol visible: MCP over stdio
is just JSON-RPC 2.0 messages, one per line, on stdin/stdout. No framework
sits between you and that.

It exposes two tools (the "Tools" primitive — model-controlled, Claude
decides when to call them) backed by data/knowledge_base.json:

  - list_known_issues()          -> every past resolved ticket, briefly
  - find_similar_ticket(query)   -> the closest-matching past ticket to a
                                     new report, by simple keyword overlap

Run it standalone to see the raw protocol:
  echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python3 ticket_kb_server.py

Register it with Claude Code / Claude Desktop's Code tab:
  claude mcp add ticket-kb -- python3 /absolute/path/to/ticket_kb_server.py
"""

import json
import re
import sys
from pathlib import Path

KB_PATH = Path(__file__).resolve().parent.parent / "data" / "knowledge_base.json"
SERVER_NAME = "ticket-kb"
SERVER_VERSION = "0.1.0"
PROTOCOL_VERSION = "2024-11-05"

TOOLS = [
    {
        "name": "list_known_issues",
        "description": "List every past resolved ticket in the internal knowledge base, with id, title and tags.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "find_similar_ticket",
        "description": "Find the closest-matching resolved ticket in the internal knowledge base for a new incoming report, using simple keyword overlap. Returns the best match and how it was fixed.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A short description of the new issue, in the reporter's own words.",
                }
            },
            "required": ["query"],
        },
    },
]


def load_kb():
    return json.loads(KB_PATH.read_text())


def tokenize(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def find_similar(query):
    kb = load_kb()
    query_tokens = tokenize(query)
    best, best_score = None, 0
    for entry in kb:
        haystack = " ".join([entry["title"], entry["symptom"], " ".join(entry["tags"])])
        score = len(query_tokens & tokenize(haystack))
        if score > best_score:
            best, best_score = entry, score
    if best is None or best_score == 0:
        return {"match": None, "message": "No similar past ticket found in the knowledge base."}
    return {"match": best, "overlap_score": best_score}


def handle_tool_call(name, arguments):
    if name == "list_known_issues":
        kb = load_kb()
        summary = [{"id": e["id"], "title": e["title"], "tags": e["tags"]} for e in kb]
        return {"content": [{"type": "text", "text": json.dumps(summary, indent=2)}]}
    if name == "find_similar_ticket":
        result = find_similar(arguments.get("query", ""))
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
    return {
        "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
        "isError": True,
    }


def handle_request(msg):
    method = msg.get("method")
    msg_id = msg.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = msg.get("params", {})
        result = handle_tool_call(params.get("name"), params.get("arguments", {}))
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}
    if method in ("notifications/initialized", "notifications/cancelled"):
        return None  # notifications get no response
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        response = handle_request(msg)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
