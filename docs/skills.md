# Project skill catalog

These skills are committed under `.agents/skills/` for repository-local discovery.
They support the existing desktop app and the requested planning, API, and agent
workflows. They add development guidance, not runtime application dependencies.

| Skill | When it fits Luxious | Source |
| --- | --- | --- |
| [spec-kit-planning](../.agents/skills/spec-kit-planning/SKILL.md) | Assess ideas; specify survey features; plan architecture and tasks | Local adapter with GitHub Spec Kit templates |
| [architecture-designer](../.agents/skills/architecture-designer/SKILL.md) | Define module boundaries and record significant decisions | Jeffallan/claude-skills |
| [python-pro](../.agents/skills/python-pro/SKILL.md) | Python models, numerical code, hardware adapters, error handling | Jeffallan/claude-skills |
| [api-designer](../.agents/skills/api-designer/SKILL.md) | Design contracts when an API is requested | Jeffallan/claude-skills |
| [fastapi-expert](../.agents/skills/fastapi-expert/SKILL.md) | Implement an API if FastAPI is selected | Jeffallan/claude-skills |
| [ecosystem-primer](../.agents/skills/ecosystem-primer/SKILL.md) | Select a framework before requested agent work | langchain-ai/langchain-skills |
| [langchain-dependencies](../.agents/skills/langchain-dependencies/SKILL.md) | Resolve packages for a selected agent framework | langchain-ai/langchain-skills |
| [langchain-fundamentals](../.agents/skills/langchain-fundamentals/SKILL.md) | Implement a bounded agent with tools | langchain-ai/langchain-skills |
| [langgraph-fundamentals](../.agents/skills/langgraph-fundamentals/SKILL.md) | Build a pipeline with explicit state and routing | langchain-ai/langchain-skills |
| [langgraph-persistence](../.agents/skills/langgraph-persistence/SKILL.md) | Resume a pipeline and persist its state | langchain-ai/langchain-skills |
| [langgraph-human-in-the-loop](../.agents/skills/langgraph-human-in-the-loop/SKILL.md) | Review and resume proposals within an application pipeline | langchain-ai/langchain-skills |
| [frontend-craft](../.agents/skills/frontend-craft/SKILL.md) | Design and verify Qt survey interfaces and Matplotlib interactions | Adapted from the supplied frontend-skills.zip |
| [image-studio](../.agents/skills/image-studio/SKILL.md) | Create requested illustrative or promotional bitmap assets | Supplied frontend-skills.zip, with scope adaptation |

Use a skill by naming it in a request, for example:

- “Use spec-kit-planning to assess real Bluetooth acquisition and plan the work.”
- “Use frontend-craft to improve measurement entry in the existing desktop UI.”
- “Use api-designer to design a survey import API.”
- “Use ecosystem-primer and langgraph-fundamentals to plan an assistant pipeline.”

API and agent skills are available for future requested work. The current app
uses local JSON/CSV persistence, deterministic analysis, and native Qt widgets.
Specialized web stacks, databases, deployment tooling, RAG, Deep Agents, and
parallel-dispatch skills were omitted because there is no corresponding feature
in this project. If a future task selects one, inspect and add its relevant skill
then; ecosystem-primer's additional skill names are recommendations, not included
packages.

## Source and adaptation details

[sources.json](skills/sources.json) records immutable repository revisions, source
paths, and the supplied archive's SHA-256 digest. Upstream supporting references
are retained with the selected skills. MIT notices for copied GitHub content are
in [skills/licenses/](skills/licenses/).

Spec Kit's planning templates are wrapped in a Luxious-specific skill rather
than initializing its CLI. The retained assessment guide links to upstream docs;
its extension commands are examples, not installed commands in this repository.

The ZIP's frontend skill was adapted from web assumptions to PySide6 layouts,
Qt accessibility, translations, and desktop screenshot verification. Its
unconditional plan approval gate was removed so existing user authorization
continues to apply. Image Studio's scope is restricted to requested artwork;
scientific graphics remain derived from survey data. Its helper and presets are
retained, and dry-run execution does not call an image provider. Real generation
requires an authorized provider, credentials, and current API documentation.

The attachment's root AGENTS.md and loose duplicate files were not installed as
project instructions. No license was supplied for the ZIP; no third-party
license is inferred for those files.

## Updating the collection

Review changes at a specific upstream commit, copy the selected skill with all
of its required references, and update sources.json and the license notices.
Keep local adapters separate from upstream examples and describe any edits.
Validate SKILL.md frontmatter, check local reference paths, and dry-run any
changed helper before committing. Follow AGENTS.md for project-specific scope,
runtime compatibility, and verification.
