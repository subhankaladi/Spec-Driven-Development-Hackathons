# Complete Guide: Sub-Agents in Claude Code

## Table of Contents
1. [What are Sub-Agents?](#what-are-sub-agents)
2. [Why Use Sub-Agents?](#why-use-sub-agents)
3. [Built-in Sub-Agents](#built-in-sub-agents)
4. [Real-World Examples](#real-world-examples)
5. [How Sub-Agents Work](#how-sub-agents-work)
6. [Creating Sub-Agents](#creating-sub-agents)
7. [Best Practices](#best-practices)
8. [Advanced Features](#advanced-features)
9. [Docusaurus Project Sub-Agents](#docusaurus-project-sub-agents)
10. [How to Create Your Own Sub-Agent in Claude Code](#how-to-create-your-own-sub-agent-in-claude-code)

---

## What are Sub-Agents?

Think of sub-agents as **specialized team members** working under Claude Code. Instead of having one AI trying to do everything, you create focused "experts" - each with their own role, knowledge, and toolset.

### Real-world Analogy
Imagine managing a software project. You wouldn't ask one person to do architecture, coding, testing, AND security reviews. You'd have:
-  An architect to plan
-  Developers to code  
-  Testers to validate
-  Security experts to audit

**Sub-agents work the same way!**

### Key Characteristics
Each sub-agent has:
- **Specific purpose and expertise area**
- **Own context window** (separate from main conversation)
- **Custom system prompt** that guides behavior
- **Specific tools** it's allowed to use
- **Can be configured with different AI models** (Sonnet, Opus, Haiku)

When Claude Code encounters a task matching a sub-agent's expertise, it delegates that task to the specialized sub-agent, which works independently and returns results.

---

## Why Use Sub-Agents?

### 1. Context Preservation 
Each sub-agent has its **own separate context window**. This means:
- Your main conversation stays clean and focused on high-level goals
- Sub-agents don't clutter the main thread with detailed research
- You can have longer, more productive sessions
- **No context pollution** between different tasks

**Example**: When the Explore sub-agent searches your codebase, all the file contents it reads stay in *its* context, not your main conversation. You only see the final results!

### 2. Specialized Expertise 
Each sub-agent can be fine-tuned for specific tasks:
- **Custom system prompts** guide their behavior
- **Specific tool access** limits what they can do
- **Domain-specific knowledge** embedded in prompts
- **Higher success rates** on designated tasks

**Example**: A debugging sub-agent knows to capture stack traces, check recent changes, and test hypotheses systematically - because you trained it that way!

### 3. Reusability & Sharing 
- Create once, **use across all projects**
- **Share with your team** for consistent workflows
- **Version control** them in your repository
- **Plugin system** allows importing community agents

**Example**: Your team's "code-reviewer" agent ensures everyone follows the same review standards, automatically.

### 4. Flexible Permissions 
Control what each sub-agent can access:
- **Limit powerful tools** to specific agents
- Some agents **only read**, others can write
- **Different agents for different security levels**
- **MCP server tools** can be granted selectively

**Example**: Your "security-auditor" agent only has read access and security scanning tools - it can't accidentally modify your code.

### 5. Performance Optimization
- **Different models for different tasks**: Use fast Haiku for searches, powerful Sonnet for complex reasoning
- **Parallel processing**: Multiple sub-agents can work on different tasks
- **Reduced latency**: Lightweight agents respond faster
- **Cost optimization**: Use cheaper models where appropriate

---

## Built-in Sub-Agents

Claude Code comes with three powerful built-in agents:

### 1. Explore Agent 

**Purpose**: Fast, lightweight agent optimized for searching and analyzing codebases

**Characteristics**:
- **Model**: Haiku (fast, low-latency)
- **Mode**: Strictly **read-only** - cannot create, modify, or delete files
- **Tools available**:
  - `Glob` - File pattern matching
  - `Grep` - Content searching with regex
  - `Read` - Reading file contents
  - `Bash` - Read-only commands (ls, git status, git log, git diff, find, cat, head, tail)

**Thoroughness Levels**:
- **Quick** - Basic searches, fastest results
- **Medium** - Moderate exploration, balanced
- **Very thorough** - Comprehensive analysis across multiple locations

**When Claude uses it**:
- Searching or understanding codebases
- Finding specific patterns or implementations
- Mapping directory structures
- When you don't need to make changes



### 2. General-Purpose Agent 

**Purpose**: Capable agent for complex, multi-step tasks requiring both exploration and action

**Characteristics**:
- **Model**: Sonnet (more capable reasoning)
- **Mode**: Can **read AND write** files
- **Tools**: Has access to **all tools**
- **Purpose**: Complex research, multi-step operations, code modifications

**When Claude uses it**:
- Tasks require both exploration and modification
- Complex reasoning needed to interpret results
- Multiple strategies may be needed
- Multi-step tasks with dependencies



### 3. Plan Agent 

**Purpose**: Specialized agent used during plan mode for codebase research

**Characteristics**:
- **Model**: Sonnet (for capable analysis)
- **Tools**: Read, Glob, Grep, Bash (for exploration)
- **Purpose**: Searches files, analyzes code structure, gathers context
- **Automatic invocation**: Used when in plan mode

**How it works**:
When you're in plan mode and Claude needs to understand your codebase to create a plan, it delegates research tasks to the Plan subagent. This prevents infinite nesting of agents while still allowing Claude to gather necessary context.

**Example scenario**:
```bash
User: [In plan mode] "Help me refactor the authentication module"

Claude: "Let me research your authentication implementation first..."
[Internally invokes Plan subagent to explore auth-related files]
[Plan subagent searches codebase and returns findings]

Claude: "Based on my research, here's my proposed plan..."
```

**Note**: The Plan subagent is **only used in plan mode**. In normal execution mode, Claude uses the general-purpose agent or your custom subagents.

---

## Real-World Examples

Here are practical sub-agents you can create for various development tasks:

### Code Reviewer

**Purpose**: Ensures code quality, security, and maintainability

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is simple and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Input validation implemented
- Good test coverage
- Performance considerations addressed

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)

Include specific examples of how to fix issues.
```

**What it does**: 
- Runs `git diff` to see changes
- Checks modified files for quality issues
- Provides organized feedback by priority
- Includes specific fix examples

**Use case**: After implementing a feature or making changes

---

## How Sub-Agents Work

### Automatic Delegation 

Claude Code proactively delegates tasks based on:
- **The task description** in your request
- **The `description` field** in subagent configurations
- **Current context** and available tools
- **Matching expertise** to the task at hand

**To encourage more proactive use**, include phrases in your `description` field like:
- "use PROACTIVELY"
- "MUST BE USED"
- "Use immediately after..."
- "Always invoke when..."

**Example**:
```markdown
---
name: security-scanner
description: MUST BE USED whenever authentication, authorization, or security-related code is modified. Proactively scans for security vulnerabilities.
---
```

## Explicit Invocation

You can **request a specific subagent** by mentioning it:

```bash
> Use the test-runner subagent to fix failing tests

> Have the code-reviewer subagent look at my recent changes

> Ask the debugger subagent to investigate this error

> Get kevin-architect to plan the refactoring
```

### How Claude Decides

Claude evaluates:
1. **Task requirements** - What needs to be done?
2. **Available subagents** - Which agents match?
3. **Agent descriptions** - Which is most appropriate?
4. **Tool requirements** - Does the agent have needed tools?
5. **Context needs** - Does it benefit from a clean context?

---

## Creating Sub-Agents

### Method 1: Interactive Command (Recommended) 

The **easiest and most powerful** way to create subagents:



**Recommended workflow**:
1. Run `/agents`
2. Select "Create New Agent"
3. Choose project-level or user-level
4. **Describe your subagent to Claude** - let it generate the initial version
5. **Customize the generated agent** to make it yours
6. Select tools from the comprehensive list
7. Save and start using!

**Why this is best**:
- Claude generates a solid foundation
- Interactive tool selection is easy
- You get immediate feedback
- Can edit in your preferred editor (press `e`)

### Method 2: Manual Files 

Create subagent files directly in the filesystem:

#### **Project-level subagents** (available in current project only):
```bash
.claude/agents/your-agent.md
```

#### **User-level subagents** (available across all projects):
```bash
~/.claude/agents/your-agent.md
```

**Priority order** when names conflict:
1. **Project subagents** (highest priority)
2. **CLI-defined subagents**
3. **User subagents** (lowest priority)

#### Creating manually:

```bash
# Create project subagent directory
mkdir -p .claude/agents

# Create the subagent file
cat > .claude/agents/test-runner.md << 'EOF'
---
name: test-runner
description: Use proactively to run tests and fix failures
tools: Read, Write, Bash
model: sonnet
---

You are a test automation expert. When you see code changes, 
proactively run the appropriate tests. If tests fail, analyze 
the failures and fix them while preserving the original test intent.
EOF
```

**Note**: Manually created subagents are loaded on next Claude Code session start. To use immediately, create via `/agents` command instead.

### Method 3: CLI-Based Configuration 

Define subagents dynamically using the `--agents` CLI flag:

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on code quality, security, and best practices.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

**When to use CLI method**:
- ✅ Quick testing of subagent configurations
- ✅ Session-specific subagents (don't need to be saved)
- ✅ Automation scripts with custom subagents
- ✅ Sharing subagent definitions in documentation

**Priority**: CLI-defined subagents have **higher priority** than user-level but **lower priority** than project-level.

---

## File Format

Each subagent is defined in a **Markdown file with YAML frontmatter**:

```markdown
---
name: your-sub-agent-name
description: Description of when this subagent should be invoked
tools: tool1, tool2, tool3  # Optional - inherits all tools if omitted
model: sonnet  # Optional - specify model alias or 'inherit'
permissionMode: default  # Optional - permission mode
skills: skill1, skill2  # Optional - skills to auto-load
---

Your subagent's system prompt goes here. This can be multiple paragraphs
and should clearly define the subagent's role, capabilities, and approach
to solving problems.

Include specific instructions, best practices, and any constraints
the subagent should follow.
```

### Configuration Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | ✅ Yes | Unique identifier (lowercase letters and hyphens) |
| `description` | ✅ Yes | Natural language description of purpose (this is what Claude reads to decide when to use it!) |
| `tools` | ❌ No | Comma-separated list. If omitted, inherits **all tools** from main thread |
| `model` | ❌ No | Model alias (`sonnet`, `opus`, `haiku`) or `'inherit'`. Default: configured subagent model |
| `permissionMode` | ❌ No | Permission handling: `default`, `acceptEdits`, `bypassPermissions`, `plan`, `ignore` |
| `skills` | ❌ No | Comma-separated skill names to auto-load |

### Model Selection

The `model` field controls which AI model the subagent uses:

- **`sonnet`** - Most capable, balanced (default for subagents)
- **`opus`** - Most powerful, for complex reasoning
- **`haiku`** - Fastest, most cost-effective
- **`'inherit'`** - Use same model as main conversation

**Example use cases**:
```markdown
model: haiku     # Fast search agent
model: sonnet    # Code review agent
model: opus      # Complex architecture planning
model: 'inherit' # Match main conversation's capabilities
```

### Available Tools

Subagents can access any of Claude Code's internal tools. **Tool configuration options**:

1. **Omit `tools` field** (recommended) - Inherits **all tools** from main thread, including:
   - Built-in tools (Read, Write, Edit, Bash, Grep, Glob, etc.)
   - Connected MCP server tools
   
2. **Specify individual tools** - For granular control:
   ```markdown
   tools: Read, Grep, Glob, Bash
   ```

**Common tools**:
- `Read` - Read file contents
- `Write` - Create new files
- `Edit` - Modify existing files
- `Bash` - Execute shell commands
- `Grep` - Search file contents with regex
- `Glob` - Find files matching patterns
- `Git` - Git operations

**MCP Tools**: When connected to MCP servers (like Supabase, GitHub, Slack), subagents can access these tools too!

**Tip**: Use `/agents` command to see and select from **all available tools** in an interactive interface.

---

## Best Practices

### 1. Start with Claude-Generated Agents 

**Highly recommended**: Generate your initial subagent with Claude, then iterate:

```bash
/agents → Create New Agent → Describe to Claude → Customize
```

**Why this works best**:
- Claude creates a solid foundation
- You get best practices built-in
- Saves time and prevents common mistakes
- You customize to your specific needs

### 2. Design Focused Subagents 

Create subagents with **single, clear responsibilities**:

✅ **Good**:
- `code-reviewer` - Reviews code quality
- `test-runner` - Runs and fixes tests
- `security-scanner` - Finds security issues

❌ **Bad**:
- `do-everything` - Reviews, tests, deploys, documents...

**Why**: Focused agents are more predictable, performant, and maintainable.

### 3. Write Detailed Prompts 

Include **specific instructions, examples, and constraints**:

```markdown
---
name: api-documenter
---

You are an API documentation expert.

When invoked:
1. Analyze the API endpoint code
2. Generate OpenAPI/Swagger documentation
3. Include request/response examples
4. Document error responses
5. Add usage notes

Format: Use OpenAPI 3.0 specification
Style: Clear, concise, developer-friendly
Examples: Include curl commands and response samples
```

**The more guidance you provide, the better the subagent performs.**

### 4. Limit Tool Access 

Only grant **tools necessary** for the subagent's purpose:

```markdown
# Security auditor - read-only
tools: Read, Grep, Glob, Bash

# Code modifier - can edit
tools: Read, Write, Edit, Bash

# Test runner - needs execution
tools: Read, Write, Bash
```

**Benefits**:
- Improves security
- Helps agent focus
- Prevents accidental modifications
- Clearer agent capabilities

### 5. Version Control Project Agents 

**Check project subagents into Git**:

```bash
git add .claude/agents/
git commit -m "Add custom subagents for team"
```

**Benefits**:
- Team collaboration
- Shared best practices
- Version history
- Consistent workflows across team

### 6. Use Descriptive Names 

Follow naming conventions:

✅ **Good**: `test-runner`, `code-reviewer`, `api-documenter`
❌ **Bad**: `agent1`, `helper`, `tool`

**Format**: lowercase with hyphens, descriptive of purpose

### 7. Test Incrementally 

When creating new subagents:
1. Start with simple tasks
2. Test with explicit invocation
3. Refine the prompt based on results
4. Add to automatic delegation
5. Monitor performance

### 8. Document Agent Purpose 

Add comments to your agent files:

```markdown
---
name: deployment-manager
description: Handles deployment to staging and production. Use when deploying or managing environments.
# Created: 2025-01-15
# Owner: DevOps Team
# Last Updated: 2025-01-20
---

<!-- 
This agent manages deployments and environment configurations.
It has access to deployment scripts and environment files.
Always runs pre-deployment checks before deploying.
-->

Your system prompt here...
```

---

## Advanced Features

### Chaining Sub-Agents 

For **complex workflows**, chain multiple subagents:

```bash
> First use the code-analyzer subagent to find performance issues,
  then use the optimizer subagent to fix them

> Have the security-scanner check the code, 
  then use code-reviewer for quality,
  and finally test-runner to verify
```

**How it works**:
1. Claude invokes first subagent
2. First subagent completes and returns results
3. Claude processes results
4. Claude invokes second subagent with context
5. Process continues...

**Use case**: Multi-stage workflows like security → review → test → deploy

### Dynamic Sub-Agent Selection 

Claude **intelligently selects subagents** based on context:

**What influences selection**:
- Keywords in your request
- Current file context
- Recent changes (git diff)
- Project type
- Previous subagent usage

**Make descriptions action-oriented**:

```markdown
# Good - Clear when to use
description: Use proactively after any authentication code changes to scan for security vulnerabilities

# Better - Even more specific
description: MUST BE USED when modifying files in src/auth/. Scans for OAuth vulnerabilities, token leaks, and authentication bypasses.
```

### Resumable Sub-Agents 

**Continue previous conversations** for long-running tasks:

#### How it works:

1. **Each subagent execution gets a unique `agentId`**
2. **Conversation stored in**: `agent-{agentId}.jsonl`
3. **Resume by providing the `agentId`**
4. **Agent continues with full context**

#### Example Workflow:

**Initial invocation**:
```bash
> Use the code-analyzer agent to start reviewing the authentication module

[Agent completes initial analysis]
Agent ID: abc123
```

**Tip**: Claude Code displays the agent ID when a subagent completes its work - save it!

---

## Docusaurus Project Sub-Agents

Here are **3 specialized sub-agents** for your Docusaurus project using AI/Spec-Driven Development:

### 1. Documentation Writer Agent 

```markdown
---
name: docs-writer
description: Creates and updates Docusaurus documentation. Use when writing new docs, creating tutorials, or updating existing documentation.
tools: Read, Write, Edit, Glob, Grep
model: sonnet
---

You are an expert technical writer specializing in Docusaurus documentation.

## Your Role

Create clear, comprehensive, and user-friendly documentation for developers.

## When Invoked

1. **Understand the topic**: Read related code, specs, or requirements
2. **Research existing docs**: Check for related documentation
3. **Plan structure**: Organize information logically
4. **Write content**: Create clear, concise documentation
5. **Add examples**: Include code samples and use cases
6. **Review and refine**: Ensure clarity and accuracy

## Documentation Standards

### Structure
- Clear page titles and descriptions
- Logical information hierarchy
- Table of contents for long pages
- Proper frontmatter metadata

### Writing Style
- **Active voice**: "Click the button" not "The button should be clicked"
- **Present tense**: "The system returns" not "The system will return"
- **Second person**: "You can configure" not "One can configure"
- **Short sentences**: Break complex ideas into digestible chunks
- **Concrete examples**: Show, don't just tell

### Markdown/MDX Best Practices
- Use proper heading hierarchy (h1 → h2 → h3)
- Include code blocks with language specification
- Add admonitions for tips, warnings, notes
- Use tables for structured data
- Include images with alt text
- Create internal links to related content

### Code Examples
- Include complete, runnable examples
- Add comments explaining key concepts
- Show both simple and advanced usage
- Include error handling examples
- Provide copy-paste ready code

## File Organization

Follow Docusaurus conventions:
- `/docs/` - Main documentation
- `/blog/` - Blog posts
- `/src/pages/` - Custom pages
- `/static/` - Static assets


```

---

### 2. Frontmatter Template


```markdown
---
id: unique-id
title: Page Title
sidebar_label: Short Label
sidebar_position: 1
description: Meta description for SEO
keywords: [keyword1, keyword2]
---


## Content Types You Create

### Tutorials
- Step-by-step instructions
- Progressive difficulty
- Clear learning objectives
- Practice exercises

### API Reference
- Endpoint documentation
- Parameter descriptions
- Request/response examples
- Error codes

### Guides
- Conceptual explanations
- Best practices
- Common patterns
- Troubleshooting

### Changelogs
- Version information
- New features
- Breaking changes
- Deprecations

Always ensure documentation is accurate, up-to-date, and helpful to your target audience.
```

---

### 3. Content Reviewer Agent 

```markdown
---
name: content-reviewer
description: Reviews Docusaurus documentation for clarity, accuracy, and consistency. Use after writing or updating documentation to ensure quality.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a meticulous content reviewer specializing in technical documentation quality.

## Your Mission

Ensure all documentation is clear, accurate, consistent, and follows best practices.

## Review Process

When invoked:

1. **Read the content**: Analyze new or updated documentation
2. **Check structure**: Verify proper organization and hierarchy
3. **Verify accuracy**: Ensure technical correctness
4. **Test examples**: Validate code samples work
5. **Check links**: Find broken internal/external links
6. **Review consistency**: Check style and terminology
7. **Assess readability**: Evaluate clarity and flow
8. **Report findings**: Provide organized feedback

## Review Checklist

### Content Quality
- [ ] Clear and concise writing
- [ ] Proper grammar and spelling
- [ ] Consistent terminology
- [ ] Active voice used
- [ ] Appropriate audience level

### Technical Accuracy
- [ ] Code examples work correctly
- [ ] API references are accurate
- [ ] Version numbers are current
- [ ] Deprecated features marke


```

# How to Create Your Own Sub-Agent in Claude Code

## Example Sub-Agent: UI Upgrading Agent
### What This Agent Does

This agent helps when:

- You want to improve UI/UX
- Upgrade design, layout, spacing, colors
- Make UI modern, clean, and responsive

We describe the role, responsibility, tools, and behavior in natural language, and Claude Code converts it into a sub-agent automatically.

## PROMPT 1: Docusaurus UI Upgrading Agent

```bash
Specifically for upgrading UI in Docusaurus-based documentation websites.

The agent should specialize in:
- Improving the UI and UX of Docusaurus sites
- Improving navbar, sidebar, footer, and docs pages UI
- Ensuring responsiveness for mobile, tablet, and desktop

The agent must understand:
- Docusaurus theme structure
- Docs, blog, and custom pages
- Markdown and MDX styling
-
Use this agent when:
- Redesigning or upgrading a Docusaurus site UI
- Making docs look modern without breaking structure


```

## PROMPT 2: Performance Optimization Agent

```bash

Focused on performance optimization.

This agent should analyze web application code and improve performance without changing features.

Responsibilities:
- Detect performance bottlenecks
- Optimize rendering and component structure
- Reduce unnecessary computations
- Improve asset loading and bundle size
- Suggest best practices clearly

Use this agent when the app feels slow or inefficient.

```
## Documentation Review & Improvement Agent

```bash

Reviewing and improving technical documentation.

The agent should:
- Review documentation for clarity, accuracy, and consistency
- Fix grammar and readability issues
- Verify technical correctness
- Ensure consistent terminology
- Improve structure for Docusaurus-style docs

Use this agent after writing or updating documentation.

```

### PRO TIP

Best practice: Write agent prompts like job descriptions — role, responsibilities, when to use, and constraints.

[Subscribe For More](https://www.youtube.com/@subhankaladi)