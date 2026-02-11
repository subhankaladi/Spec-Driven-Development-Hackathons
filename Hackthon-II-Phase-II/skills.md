# Claude Code Skills Guide

## What are Skills?

**Skills** are instruction manuals that teach Claude HOW to do specific tasks. They're passive knowledge stored as markdown files that Claude reads when needed.

Think of Skills as **recipes** - Claude reads them and follows the instructions in your main conversation.

---

## Skills vs Sub-agents

### ⚡ Quick Comparison: Skills vs Sub-Agents

| Aspect | 🧩 Skills | 🤖 Sub-Agents |
|------|---------|-------------|
| **Role** | Instructions & knowledge | Specialized AI workers |
| **Behavior** | Claude reads and follows rules | Agent actively performs tasks |
| **Context** | Uses main conversation | Has its own context window |
| **How they run** | Automatic (Claude decides) | Automatic or called explicitly |
| **Setup level** | Simple (single file) | Advanced (full configuration) |
| **Best for** | Repeated patterns & steps | Large multi-step workflows |

> **Memory tip:**  
> 🧩 *Skills guide Claude*  
> 🤖 *Sub-Agents do the work*


### Real Example

**Skill**: "How to create a glassmorphism button"
- Claude reads the instructions
- Applies them in your current chat
- Uses it as a reference

**Sub-agent**: "Complete website upgrader"
- Takes over the entire task
- Uses multiple Skills
- Works separately and returns results

---

## When to Use Each

### Use Skills When:
✅ Teaching a specific pattern or workflow  
✅ Providing templates or references  
✅ Sharing team conventions (commit messages, code style)  
✅ Reusable design components (buttons, navbars, footers)  
✅ Single, focused instructions  

### Use Sub-agents When:
✅ Complete products or features  
✅ Complex multi-step workflows  
✅ Need separate context to keep main chat clean  
✅ Want to coordinate multiple Skills  
✅ Need specific tool restrictions  

---

## Creating Skills

### File Structure

Skills are stored in:
- **Personal**: `~/.claude/skills/skill-name/`
- **Project**: `.claude/skills/skill-name/`

Each Skill needs a `SKILL.md` file:

```
.claude/skills/
└── modern-button/
    └── SKILL.md
```

### SKILL.md Format

```markdown
---
name: skill-name
description: When to use this Skill and what it does
---

# Skill Title

## Instructions
Step-by-step guidance for Claude.

## Examples
Show concrete examples.
```

### Required Fields

- **name**: lowercase-with-hyphens (max 64 chars)
- **description**: Brief description including when to use it (max 1024 chars)

---

## Example Skills

### Simple Button Skill

```markdown
---
name: modern-button
description: Create trendy glassmorphism buttons. Use when user wants modern button designs.
---

# Modern Button Design

## Instructions
Create buttons with these features:

1. **Glassmorphism effect**
   - Semi-transparent background
   - Backdrop blur filter
   - Subtle border

2. **Hover animations**
   - Smooth scale transform
   - Color transition
   - Shadow elevation

3. **Responsive design**
   - Works on all screen sizes
   - Touch-friendly on mobile

## Example Code
```css
.glass-button {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.glass-button:hover {
  transform: scale(1.05);
  background: rgba(255, 255, 255, 0.2);
}
```
```

### Hero Section Skill

```markdown
---
name: hero-section
description: Build modern landing page hero sections with animations. Use for homepage designs.
---

# Hero Section Design

## Instructions

1. **Layout structure**
   - Full viewport height
   - Centered content
   - Eye-catching headline

2. **Visual elements**
   - Gradient background
   - Animated elements
   - CTA button

3. **Animations**
   - Fade in on load
   - Parallax effects
   - Smooth scrolling

## Best Practices
- Keep headline under 10 words
- Use high-contrast text
- Single clear call-to-action
- Mobile-first approach

## Example Structure
```html
<section class="hero">
  <div class="hero-content">
    <h1 class="animate-fade-in">Your Headline</h1>
    <p class="animate-fade-in-delay">Supporting text</p>
    <button class="cta-button">Get Started</button>
  </div>
</section>
```
```

---

## How Claude Uses Skills

### Automatic Activation

Claude reads your Skill descriptions and automatically uses them when relevant:

```
User: "Add a modern button to my page"

Claude: [Reads modern-button Skill]
        [Applies the instructions]
        [Creates the button]
```

### Progressive Disclosure

Claude only reads what it needs:
1. First checks Skill descriptions
2. Loads SKILL.md if relevant
3. Reads supporting files if referenced

---

## Multi-File Skills

You can add supporting files:

```
.claude/skills/design-system/
├── SKILL.md          (main instructions)
├── colors.md         (color palette)
├── typography.md     (font guidelines)
└── components.md     (component library)
```

Reference them in SKILL.md:
```markdown
For color palette, see [colors.md](colors.md).
For typography rules, see [typography.md](typography.md).
```

---

## Skill Tool Restrictions

Limit which tools Claude can use with a Skill:

```markdown
---
name: safe-reader
description: Read files without making changes
allowed-tools: Read, Grep, Glob
---
```

When this Skill is active, Claude can only:
- Read files
- Search with Grep  
- Find files with Glob

**No editing, writing, or bash commands.**

---

## Creating Your Skills

### Method 1: Ask Claude (Recommended for Beginners)

Simply describe what you need in natural language. Here are **3 different prompt examples**:

#### Prompt Example 1: Simple & Direct
```
Create a Skill for responsive navbar designs with mobile menu.
Save it to .claude/skills/navbar-design/
```

#### Prompt Example 2: Detailed with Requirements
```
I need a Skill for modern card components. Include:
- Shadow effects and hover animations
- Responsive grid layouts
- Image optimization techniques
- Best practices for accessibility

Save it as .claude/skills/card-component/
```

#### Prompt Example 3: Context-Rich with Use Cases
```
Create a Skill that teaches how to build API integration patterns.
This should cover:
- Error handling strategies
- Retry logic with exponential backoff
- Response caching
- Rate limiting best practices

Use it when I'm connecting to third-party APIs or building API clients.
Save to .claude/skills/api-integration/
```

**What Claude will do:**
- ✅ Create the folder structure
- ✅ Write SKILL.md with correct YAML format
- ✅ Add detailed instructions and examples
- ✅ Include best practices

### Method 2: Manual Creation

```bash
mkdir -p .claude/skills/navbar-design
nano .claude/skills/navbar-design/SKILL.md
```

Then write your SKILL.md content.

---

## Real-World Example: Web Design Library

### Your Skills (Design Components)

```
.claude/skills/
├── modern-button/      → Button designs
├── navbar-design/      → Navigation patterns
├── hero-section/       → Landing page heroes
├── footer-design/      → Footer layouts
└── card-component/     → Card designs
```

### Your Sub-agent (Uses All Skills)

```markdown
---
name: website-upgrader
description: Complete website redesign
---

You upgrade entire websites by:
1. Using modern-button Skill for all buttons
2. Using navbar-design Skill for navigation
3. Using hero-section Skill for landing page
4. Using footer-design Skill for footer
5. Ensuring design consistency
```

**Skills = Your Lego pieces**  
**Sub-agent = Builds the complete structure**

---

## Testing Skills

After creating a Skill, test it:

```
"Can you create a modern button for my homepage?"
```

Claude should:
1. Recognize the request matches your Skill
2. Load the Skill instructions
3. Apply them to create the button

---

## Debugging Skills

### Skill Not Working?

**Check description specificity:**

❌ Too vague:
```yaml
description: Helps with buttons
```

✅ Specific:
```yaml
description: Create modern glassmorphism buttons with hover effects. Use when user wants trendy button designs.
```

**Verify file location:**
```bash
ls .claude/skills/your-skill/SKILL.md
```

**Check YAML syntax:**
```bash
cat .claude/skills/your-skill/SKILL.md | head -n 10
```

Ensure:
- Opening `---` on line 1
- Closing `---` before content
- Valid YAML (no tabs, correct indentation)

---

## Best Practices

### 1. Keep Skills Focused
One Skill = One capability

✅ Good:
- "Modern button designs"
- "Hero section layouts"
- "Responsive navbar"

❌ Too broad:
- "All designs" (split into separate Skills)

### 2. Write Clear Descriptions
Include WHAT and WHEN:

```yaml
description: Create responsive navigation bars with mobile menus. Use when building site navigation or updating navbar designs.
```

### 3. Add Examples
Show concrete code examples in your Skills.

### 4. Share with Team
Commit project Skills to git:

```bash
git add .claude/skills/
git commit -m "Add design system Skills"
git push
```

Team members get them automatically!

---

## Skills vs Sub-agents Decision Tree

```
Need to do something?
│
├─ Single pattern/component?
│  └─ Use SKILL
│     Examples: button, navbar, footer
│
└─ Complete task/product?
   └─ Use SUB-AGENT
      Examples: full redesign, complex feature
```

---

## Quick Reference

### Create a Skill
```bash
# Ask Claude (easiest)
"Create a Skill for [what you need]"

# Or manually
mkdir -p .claude/skills/skill-name
code .claude/skills/skill-name/SKILL.md
```

### Skill Template
```markdown
---
name: your-skill-name
description: What it does and when to use it
---

# Skill Title

## Instructions
Your step-by-step guidance

## Examples
Concrete examples
```

### View Available Skills
```
"What Skills are available?"
```

---

## Summary

**Skills** are your reusable knowledge library:
- Individual components and patterns
- Instructions Claude reads and follows
- Quick to create and use
- Build your library over time

**Sub-agents** coordinate Skills for complex work:
- Complete products and features  
- Use multiple Skills together
- Keep main conversation clean
- Handle multi-step workflows

**Start with Skills, graduate to Sub-agents as needed!**

---

## Next Steps

1. **Create your first Skill** for something you do often
2. **Build a Skills library** for your common patterns
3. **Create a Sub-agent** when you need to coordinate multiple Skills
4. **Share with your team** via git

Need help? Just ask Subhan Kaladi 😁

[Subscribe My YT Channel](https://www.youtube.com/@subhankaladi)