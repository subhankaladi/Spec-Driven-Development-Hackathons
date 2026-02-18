---
id: '001'
title: 'Debug Agent Tool Calling MCP Missing'
stage: misc
date_iso: '2026-01-18'
surface: agent
model: 'claude-sonnet-4-5-20250929'
feature: general
branch: '007-chatkit-frontend'
user: 'subhankaladi15'
command: '/sp.phr --title \"Debug agent tool calling - MCP missing\" --stage misc --feature general'
labels: ['debug', 'agent', 'tool-calling', 'mcp', 'fastapi', 'openai']
links_spec: null
links_ticket: null
links_adr: null
links_pr: null
files_yaml: |
  - none
tests_yaml: |
  - none
---

## Prompt Text (Verbatim)
--title "Debug agent tool calling - MCP missing" --stage misc --feature general

## Response Text
Identified root cause: Agent uses OpenAI with tools that POST to missing MCP server (localhost:8001). "hello" works (no tool), "add task" fails silently (tool error). Backend/frontend solid, auth works, but servers not running due to cd errors (already in backend dir). Proposed MCP impl or direct DB patch.

## Outcome/Impact
- Diagnosed tool calling failure
- Confirmed auth/chat flow works when MCP present
- Servers ready to restart without cd backend

## Tests Summary
- none

## Files Summary
- none

## Next Prompts
- Implement MCP server on :8001 with /tools/*
- Patch agent_service.py to call task_service directly
- Restart servers: source venv/bin/activate && python -m src.main

## Reflection Note
MCP dependency undocumented; agent hardcoded to external service without fallback.

**Failure modes observed:** No .specify/scripts/bash/create-phr.sh; used agent-native Write. No PHR template found.
**Next experiment:** Add standard phr-template.prompt.md to project.