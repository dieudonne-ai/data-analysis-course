# Git Basics for Analysts

Git records the history of your work so you can go back, compare, and collaborate.
This course uses it: **one commit per lesson**.

![Git workflow](diagrams/git-workflow.pdf) — see [`diagrams/git-workflow.pdf`](diagrams/git-workflow.pdf).

## The four areas
| Area | What it holds |
|------|---------------|
| Working directory | Your files as you edit them |
| Staging area | Changes selected for the next commit |
| Local repository | Saved commits (the history) |
| Remote | A shared copy, e.g. on GitHub |

## Everyday commands
```bash
git status                 # what changed?
git add 03-data-loading/   # stage a folder (or a single file)
git commit -m "Add module 03: data loading"   # save a snapshot
git log --oneline          # list past commits
git diff                   # see unstaged changes
git push -u origin main    # send commits to the remote
git pull                   # fetch + merge remote changes
```

## Good commit messages
- Start with a verb: `Add`, `Fix`, `Update`.
- Say *what* and *why*, in under ~70 characters.
- One logical change per commit — easier to review and to undo.

## Branches (next lessons)
A branch is a parallel line of work: `git switch -c cleaning-notes`, then merge it back.

## Ignoring files
List files Git must not track in `.gitignore` (this repo ignores `.venv/` and `__pycache__/`).
Never commit passwords or very large raw datasets.

## Exercise
Change one value in `data/sales.csv`, run `git diff`, then commit it with a clear message and inspect `git log --oneline`.
