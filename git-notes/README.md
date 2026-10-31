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

## Merging and pull requests
```bash
git fetch origin                      # download remote changes without applying them
git pull origin main                  # fetch + merge into the current branch
git switch main && git merge --no-ff my-branch   # keep an explicit merge commit
```
A **pull request** is a request to merge your branch into the main branch on the remote,
so others can review it first. Each lesson branch -> pull request -> merge into main.

## Branching in practice
```bash
git switch -c module-05      # create + switch to a new branch
git branch -a                # list local and remote branches
git log --oneline --graph    # visualize history
git switch main && git merge module-05 && git branch -d module-05
```
Tip: keep each branch small and focused (one lesson = one branch), so merges stay conflict-free.
