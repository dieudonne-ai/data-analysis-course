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

## Branches and merging
A branch is a movable pointer to a commit: cheap to create, safe to experiment on.
Diagram: [`git_branching.pdf`](git_branching.pdf)
```bash
git switch -c feature/cleaning   # create + switch
# ...edit, git add, git commit (twice)...
git switch main
git merge feature/cleaning       # bring the work into main
git branch -d feature/cleaning   # delete the merged branch
```
Analyst use case: try a new cleaning strategy on a branch; merge only if the results are better.

### Merge conflicts
If both branches changed the same lines, Git stops and marks the file:
```text
<<<<<<< HEAD
df["price"].fillna(df["price"].mean())
=======
df["price"].fillna(df["price"].median())
>>>>>>> feature/cleaning
```
Edit the file to keep the right version, remove the markers, then `git add file && git commit`.

## Undoing things
```bash
git restore file.py         # discard unstaged edits
git restore --staged file.py  # unstage
git revert <commit>         # safe undo: creates a new commit
```

## Tip for data projects
Commit code and small datasets; add large or private data to `.gitignore`.
