# Contributing to NewtCode

Thank you for your interest in contributing to NewtCode.

This project accepts contributions selectively to keep the codebase coherent, maintainable, and technically justified.

Please read this guide before opening an issue or pull request.

---

## Project Standards

Contributions should be:

- technically correct;
- clearly motivated;
- small enough to review;
- consistent with the current project structure and goals;
- backed by tests or strong justification when tests are not applicable.

Contributions may be declined if they add noise, unnecessary abstraction, speculative features, or low-value cleanup.

---

## Contribution Types

Contributions are welcome when they:

- fix a real bug;
- improve reliability, correctness, or maintainability;
- add a useful feature aligned with project scope;
- improve documentation that affects real usage or contributor workflow;
- improve tests, type safety, or developer tooling.

If a contribution creates more review burden than project value, it is likely to be closed.

---

## Before pull requests

For anything non-trivial, open an issue or discussion first, if you wish to:

- add a new feature;
- change public behavior;
- introduce a new dependency;
- modify project structure or architecture;
- affect multiple modules.

Small, obvious fixes may be submitted directly as pull requests.

---

## Branch Naming

Use short, descriptive branch names with one of these prefixes:

```text
feature/<short-description>
fix/<short-description>
docs/<short-description>
chore/<short-description>
refactor/<short-description>
test/<short-description>
```

Examples:

```text
fix/path-normalization
feature/sql-parser
docs/update-installation
```

---

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) format with a type, optional scope, and concise description:

```text
feat(parser): add a new feature
fix(cli): correct a bug
docs(readme): update installation
test(api): add or update a test
refactor(core): simplify internal logic
chore(scope): update dependencies
```

Rules:

- Use the imperative mood: add, fix, update; not added or fixed.
- Keep the subject small, concise and specific.
- Make commits atomic: one logical change per commit.
- Do not mix refactoring, formatting, and behavior changes in one commit.

---

## Pull Request Rules

Every Pull Request should:

- target a single problem or change set;
- explain what changed and why;
- reference the relevant issue or discussion when applicable;
- include tests for behavior changes, bug fixes, or new features;
- update documentation when user-facing behavior changes;
- pass all relevant checks before review.

Pull Requests may be closed without merge if they are:

- too broad;
- poorly explained;
- not aligned with project direction;
- missing tests without justification;
- based on subjective cleanup rather than a concrete need;
- generated mechanically and not meaningfully reviewed by the author.

---

## Testing

Quality is required. If your change affects behavior, you are expected to prove it.

General rules:

- Add or update tests for bug fixes and new features.
- Prefer small, deterministic tests.
- Use `pytest` for Python tests.

Minimum expectations:

- Bug fix: include a regression test when possible.
- New feature: include at least one test for expected behavior and one edge case where reasonable.
- Refactor: no behavior change; existing tests must still pass, and new tests may be required if coverage was previously weak.
- Docs/config-only changes: tests are not always required, but the change must still be accurate and justified.

Run tests before submitting:

```bash
pytest tests/
```

If additional commands are required in this repository, document them in the pull request.

---

## Code Quality Expectations

Submitted code must be intentional, readable, and maintainable.

Required standards:

- Prefer simple solutions over clever ones.
- Preserve the existing architecture unless there is a strong reason to change it.
- Avoid premature abstraction.
- Avoid dead code, commented-out code, and placeholder implementations.
- Avoid broad rewrites when a targeted fix is enough.
- Use explicit names.
- Keep functions and modules cohesive.
- Public functions must have type hints.
- New code should include or preserve meaningful docstrings where appropriate.
- Use explicit imports; do not use wildcard imports.

Python-specific rules:

- Include `from __future__ import annotations` where the project standard requires it.
- Provide explicit type hints for public APIs.
- Prefer clear, testable functions over implicit side effects.
- Keep module-level behavior minimal.
- Check for guidelines for more details and examples:
  - [guidelines/code-style-python.md](https://github.com/AnnaBurova/dev-configs/blob/main/guidelines/projects/code-style-python.md)
  - [guidelines/docstring.py](https://github.com/AnnaBurova/dev-configs/blob/main/guidelines/projects/docstring.py)
  - [guidelines/script.py](https://github.com/AnnaBurova/dev-configs/blob/main/guidelines/projects/script.py)

Not acceptable:

- code that works but is hard to understand;
- code copied from AI tools without adaptation;
- unnecessary wrappers, layers, or factories;
- changes that increase complexity without measurable benefit;
- code that does not match surrounding style and design choices.

---

## Documentation Changes

Documentation contributions are welcome when they improve actual understanding or usage.

Good documentation changes:

- clarify installation or usage;
- explain non-obvious behavior;
- document limitations, edge cases, or workflow;
- keep examples accurate and minimal.

Documentation-only Pull Requests may be rejected if they are verbose, generic, redundant, or disconnected from the real project.

---

## Security and Secrets

Never commit:

- API keys;
- tokens;
- passwords;
- `.env` files with real values;
- private credentials or internal endpoints.

If you notice a security issue, do not open a public issue with sensitive details. Report it privately through the appropriate project contact method. Check for email or other contact information in the [AUTHORS](AUTHORS) file.

---

## Review and Merge Policy

All contributions are reviewed before merge.

Please expect feedback. Review comments are part of the process, not a personal attack.

Maintainers reserve the right to reject contributions that do not fit the project, even if they are technically functional.

Opening a pull request does not guarantee merge.

---

## Contributor Checklist

Before opening a pull request, make sure you have:

- read this file;
- checked that the change fits project scope;
- kept the Pull Request focused;
- written a clear commit history;
- added or updated tests when needed;
- updated docs when behavior changed;
- removed debug code and temporary files;
- verified that no secrets or local artifacts are included.

---

## Final Notes

The best contributions solve a real problem with the smallest justified change.

If your pull request is thoughtful, technically sound, and easy to review, it is welcome.

❤️ Thank You
