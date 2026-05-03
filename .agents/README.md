# Agent Skills

This directory is the portable agent-customization location used by current
agent tooling. Skills in `.agents/skills/` are plain-text workflow guidance and
reference templates only.

## Skill Catalog

The catalog intentionally keeps MATLAB and Simulink skills together because most
real workflows move between code, data, tests, simulation, models, and generated
artifacts. Context separation comes from each skill directory's `SKILL.md`,
`manifest.yaml`, and optional `reference/` folder.

Current imported skill groups:

- MATLAB core workflows: testing, debugging, code review, code modernization,
	Live Scripts, app building, product listing, and product installation.
- MATLAB database workflows: relational reads, relational writes, DuckDB, and
	Database Toolbox ORM mapping.
- Simulink and Model-Based Design workflows: model building, simulation,
	persistent tests, requirements drafts, algorithm specs, and plant specs.

## Relationship To `.github`

This repo intentionally uses both locations:

- `.agents/skills/` contains portable, task-oriented workflow skills for
	Simulink modeling, simulation, testing, specification, and requirements work.
- `.github/copilot-instructions.md` and `.github/instructions/` contain
	workspace instructions that apply broadly while editing this repository.
- `.github/skills/` contains repository-maintenance skills for MCP tool
	coverage, mode classification, and decision records.

Compatible agent clients can discover skills from both `.agents/skills/` and
`.github/skills/`. Keep instruction files in `.github`; they are a different
customization type than skills. If a single skill catalog becomes preferable,
move only the `.github/skills/*` directories into `.agents/skills/` and update
any paths that reference their bundled decision records.
