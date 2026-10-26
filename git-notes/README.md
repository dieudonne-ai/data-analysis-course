# Git Notes for Analysts

Short notes on the Git habits used in this course (one commit per lesson).
Diagram: [`git_workflow.pdf`](git_workflow.pdf)

## The three areas
Working directory -> (`git add`) -> staging area -> (`git commit`) -> local repository -> (`git push`) -> remote.

## Everyday commands
```bash
git status                  # what changed?
git add 03-data-loading/    # stage a folder
git commit -m "Add module 03: data loading"
git log --oneline           # compact history
git diff                    # unstaged changes
git push -u origin main     # publish
```

## Good commit messages
- Imperative mood: "Add module 04", not "Added".
- One logical change per commit — here, one lesson.
- Example: `Add module 04: data cleaning with missing values`.

## Branches
```bash
git switch -c fix-typos     # create + switch
git switch main
git merge fix-typos
```

## Undoing things
```bash
git restore file.py         # discard unstaged edits
git restore --staged file.py  # unstage
git revert <commit>         # safe undo: creates a new commit
```

## Tip for data projects
Commit code and small datasets; add large or private data to `.gitignore`.

## Never commit generated or private files (`.gitignore`)
Cleaned outputs and virtual environments should not pollute history:
```gitignore
.venv/
__pycache__/
*.pyc
```
Raw data stays committed (reproducibility); big or private datasets do not.
