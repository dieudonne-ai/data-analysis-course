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
Diagram: [`git_undo.pdf`](git_undo.pdf)
```bash
git restore file.py           # discard unstaged edits
git restore --staged file.py  # unstage, keep the edits
git commit --amend            # fix the last commit message (before pushing only)
git revert <commit>           # safe undo: creates a new commit
```
Avoid `git reset --hard` and force-push unless you fully understand them.

## Remotes (GitHub)
```bash
git remote add origin https://github.com/<you>/data-analysis-course.git
git push -u origin main       # first push; later just `git push`
git pull                      # fetch + merge the remote changes
git clone <url>               # copy a repository
```

## .gitignore
Files listed in `.gitignore` are never committed. In this course:
```text
.venv/
__pycache__/
*/examples/output/    # generated charts and reports
```
Never commit passwords, API keys or private data. Large datasets: keep them out of Git (or use Git LFS).

## Tags
Mark milestones, e.g. a finished course version:
```bash
git tag -a v1.0 -m "Course complete: modules 01-10"
git push origin v1.0
```

## Useful inspection commands
```bash
git log --oneline --graph --all   # history as a graph
git show <commit>                 # what one commit changed
git diff main..feature/cleaning   # compare two branches
git blame file.py                 # who changed each line
```

## Tip for data projects
Commit code and small datasets; add large or private data to `.gitignore`.
Commit after each analysis step - the history documents your reasoning.
