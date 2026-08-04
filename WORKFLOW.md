# Team GitHub Workflow

## Branching Strategy

- The `main` branch always contains stable and releasable code.
- Every new feature is developed in its own feature branch.
- Branch naming convention:

```
feature/<short-description>
fix/<short-description>
docs/<short-description>
refactor/<short-description>
chore/<short-description>
```

- Feature branches are deleted after they are merged.

---

## Commit Message Convention

The team follows Conventional Commits.

Format

```
[type]: description
```

Examples

```
feat: add dashboard layout
fix: correct sidebar navigation
docs: update README
refactor: improve project structure
chore: update dependencies
```

---

## Pull Request Process

Every feature branch must be reviewed before merging into main.

Each PR should include:

- Summary
- Changes made
- Related Issue
- Testing

At least one reviewer approval is required before merging.

---

## GitHub Issues

Every feature starts with a GitHub Issue.

Each issue contains

- Title
- Description
- Label
- Assignee

Issues are closed automatically by referencing them in Pull Requests using

```
Closes #IssueNumber
```