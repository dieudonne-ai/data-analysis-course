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

## Merge conflicts
A conflict happens when two branches change the same lines. Git marks them:
```
<<<<<<< HEAD
price = 1.5
=======
price = 1.6
>>>>>>> fix-prices
```
Edit the file to keep the right version, remove the markers, then:
```bash
git add file.py
git commit          # completes the merge
```

## Useful extras
```bash
git stash           # park unfinished work, git stash pop to restore
git log --oneline --graph --all
git commit --amend  # fix the last (unpushed) commit message
```
