# ADR 1: Use Editable Install for Local Module Resolution

## Status
Accepted

## Context
I encountered `unresolved-import` errors when trying to import utility modules 
(like `src.utils.logging_config`) into extraction scripts. Python's default 
path resolution was not recognizing the `src` directory as a package.

## Decision
I decided to install the project in "editable mode" using `uv pip install -e .`.
This creates a link between the local source code and the virtual environment.

## Consequences
- Pros: Resolves all import issues; changes in source code are reflected immediately.
- Cons: Requires a one-time setup step for new developers.
