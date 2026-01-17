---
id: "001"
title: Update CLAUDE.md with specialized agent guidelines
stage: general
date: 2026-01-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: a
command: Update CLAUDE.md file with agent usage guidelines
labels: ["configuration","agents","documentation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - /mnt/c/Users/a/Documents/GitHub/YT-Hackathon-II/phase-II/CLAUDE.md
tests:
  - None
---

## Prompt

Update the `claude.md` file based on my project requirements.
In this file:**
- Use Auth Agent for authentication
- Use Frontend Agent for frontend development (e.g., Next.js)
- Use DB Agent for database design and operations
- Use Backend Agent for FastAPI development

Below are my project requirements:
```"""   Phase II: Todo Full-Stack Web Application
Basic Level Functionality
Objective: Using Claude Code and Spec-Kit Plus transform the console app into a modern multi-user web application with persistent storage.
Development Approach: Use the Agentic Dev Stack workflow: Write spec → Generate plan → Break into tasks → Implement via Claude Code. No manual coding allowed. We will review the process, prompts, and iterations to judge each phase and project.
Requirements
Implement all 5 Basic Level features as a web application
Create RESTful API endpoints
Build responsive frontend interface
Store data in Neon Serverless PostgreSQL database
Authentication – Implement user signup/signin using Better Auth
Technology Stack
Layer
Technology
Frontend
Next.js 16+ (App Router)
Backend
Python FastAPI
ORM
SQLModel
Database
Neon Serverless PostgreSQL
Spec-Driven
Claude Code + Spec-Kit Plus
Authentication
Better Auth

Better Auth can be configured to issue JWT (JSON Web Token) tokens when users log in. These tokens are self-contained credentials that include user information and can be verified by any service that knows the secret key.
How It Works
User logs in on Frontend → Better Auth creates a session and issues a JWT token
Frontend makes API call → Includes the JWT token in the Authorization: Bearer <token> header
Backend receives request → Extracts token from header, verifies signature using shared secret
Backend identifies user → Decodes token to get user ID, email, etc. and matches it with the user ID in the URL
Backend filters data → Returns only tasks belonging to that user

 """```

## Response snapshot

- Added "Specialized Agent Guidelines" section to CLAUDE.md
- Documented Auth Agent for authentication tasks (Better Auth, JWT, sessions)
- Documented Frontend Agent for Next.js development
- Documented Database Agent for PostgreSQL/SQLModel tasks
- Documented Backend Agent for FastAPI REST API tasks
- Added technology stack reference table mapping layers to agents

## Outcome

- ✅ Impact: Updated CLAUDE.md with specialized agent guidelines for Phase II Todo project
- 🧪 Tests: None
- 📁 Files: CLAUDE.md updated with agent guidelines section
- 🔁 Next prompts: Continue with spec creation for Phase II features
- 🧠 Reflection: Added clear agent routing guidelines to help future development follow the Agentic Dev Stack workflow

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (if applicable): N/A
