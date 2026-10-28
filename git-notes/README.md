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

## Branch diagram
See [`git_branches.pdf`](git_branches.pdf): work on a `feature` branch, then merge it back
into `main` so unfinished work never breaks the stable version.

## .gitignore
A `.gitignore` file lists what Git must not track:
```gitignore
.venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
data/private/
```
Files already committed stay tracked: remove them with `git rm --cached <file>`.

## Inspecting history
```bash
git log --oneline --graph   # compact history with branches
git show <commit>           # what a commit changed
git blame file.py           # who changed each line
git diff main..feature      # compare two branches
```

## Stash and tags
```bash
git stash          # park unfinished edits
git stash pop      # bring them back
git tag v1.0       # label a milestone (e.g. "course released")
```

## Merge conflicts
When two branches edit the same lines, Git marks the file:
```text
<<<<<<< HEAD
price = 1.5
=======
price = 1.6
>>>>>>> feature
```
Edit the file to keep the right version, delete the markers, then `git add file` and
`git commit`.
