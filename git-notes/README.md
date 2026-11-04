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

## .gitignore and tags
```bash
echo "*.png" >> .gitignore    # ignore generated files; commit the code that makes them
git rm --cached file.png      # stop tracking a file already committed
git tag -a v0.6 -m "Modules 01-06"   # name a milestone
git push origin v0.6
```

## Stash, restore and revert
```bash
git stash                    # shelve uncommitted work to get a clean tree
git stash pop                # bring it back
git restore file.py          # throw away edits in one file
git revert <commit>          # undo a pushed commit by adding a new one (history stays intact)
git log -p -- file.py        # see how one file changed over time
```
Rule: never rewrite history that others have pulled; use `revert`, not `reset --hard`.

## Inspecting history: diff, blame, bisect
```bash
git diff main..my-branch     # what merging my-branch would change
git blame file.py            # who last changed each line, and in which commit
git log -S "revenue"         # find commits that added/removed the text "revenue"
git bisect start; git bisect bad; git bisect good <old-commit>   # binary-search for the commit that broke something
```

## Pull, fetch and keeping main up to date
```bash
git fetch origin             # download remote changes without touching your files
git pull origin main         # fetch + merge into the current branch
git switch -c module-10 main # start the next lesson from an up-to-date main
git merge --no-ff module-10  # merge it back, keeping a visible merge commit
git branch -d module-10      # delete the merged branch
```
Pull requests: push a branch, open a PR, review, then merge into `main`. Pull `main` again before starting new work.
