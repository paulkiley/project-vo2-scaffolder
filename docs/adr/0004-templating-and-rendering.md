# ADR 0004: Templating and Rendering with Jinja2 and Copier

Date: 2025-09-15

## Status

Accepted

## Context

The scaffold includes documentation and artifacts that vary by project (names, versions, governance). We need a flexible, repeatable templating approach.

## Decision

- Author templates as `.j2` (Jinja2) files under `data_files/templates/`
- Provide `render.py` for direct rendering with `--strict`, YAML/JSON contexts
- Provide `copier.yml` to manage template application and updates over time

## Consequences

- Pros: mature ecosystem; strict undefined checks; easy local and CI rendering
- Cons: adds dependencies (`jinja2`, `pyyaml`); need to manage variable schema

## Alternatives Considered

- Cookiecutter: widely used; Copier chosen for better update story
- Homegrown templating: higher maintenance, fewer features
