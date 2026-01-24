# Agents and Skills

This directory contains AI agent definitions and skill documentation for the ML Inference Platform.

## Structure

```
.agents/
├── README.md           # This file
├── agents/             # Subagent definitions
│   ├── model-reviewer.md
│   └── api-reviewer.md
└── skills/             # Best practices documentation
    ├── README.md
    ├── coding/
    ├── inference/
    └── workflows/
```

## Agents

Agents are specialized reviewers that auto-trigger based on file changes.

| Agent | Model | Triggers On |
|-------|-------|-------------|
| [model-reviewer](agents/model-reviewer.md) | opus | `models/`, `services/inference*` |
| [api-reviewer](agents/api-reviewer.md) | sonnet | `api/routes/`, `schemas/` |

## Skills

Skills are best-practice documentation organized by domain. Each skill directory contains:
- `SKILL.md` - Metadata and overview
- Supporting `.md` files - Detailed documentation

| Skill | Description |
|-------|-------------|
| [coding](skills/coding/) | Python coding standards, testing patterns |
| [inference](skills/inference/) | ML inference best practices |
| [workflows](skills/workflows/) | Development workflows, Docker, PRs |

## Usage

### Agents
Agents run automatically when relevant files are modified. They review changes and provide feedback before PR creation.

### Skills
Skills are referenced when working on related tasks. They provide context and standards to follow.
