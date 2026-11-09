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

## Rebase, cherry-pick and releases
```bash
git rebase main              # replay my branch commits on top of the latest main (linear history)
git cherry-pick <commit>     # copy one commit from another branch onto this one
git tag -a v1.0 -m "Course complete"   # mark a milestone
git push origin v1.0         # share the tag (tags are not pushed by default)
```
Rule of thumb: `merge` to combine shared work, `rebase` only on your own unpushed branches.
A tagged release (`v1.0`) lets others cite exactly which version of the analysis they used.

## Working with remotes and clean history
```bash
git remote -v                      # which remotes does this repo know?
git branch -vv                     # local branches and the remote branch each one tracks
git push -u origin my-branch       # first push: also sets the upstream
git stash -u                       # shelve changes, including untracked files
git commit --amend --no-edit       # fold a forgotten file into the last (unpushed!) commit
git log --oneline --since="1 day ago"   # what did I do today?
```
A daily-commit habit: one small lesson, one commit, one pull request, merged the same day.

## Inspecting history and finding bugs
```bash
git log --oneline --graph --all    # draw the branch/merge history as a graph
git show <commit>                  # see exactly what one commit changed
git log -p -- path/to/file         # history of a single file, with diffs
git bisect start                   # binary-search for the commit that introduced a bug
git bisect bad                     # current commit is broken
git bisect good <old-commit>       # this old commit worked; git checks out the middle
git bisect reset                   # finish and return to your branch
git restore --source=<commit> file # recover an older version of one file
```
`bisect` finds a bug among 1000 commits in about 10 steps. Small, focused commits make it far more useful.

## Recovering lost work and saving time
```bash
git reflog                         # every place HEAD has been: your safety net after a bad reset
git reset --hard <reflog-entry>    # jump back to a state you thought was lost (e.g. HEAD@{2})
git config --global alias.lg "log --oneline --graph --all"   # now `git lg` is a shortcut
git clean -nd                      # DRY RUN: list untracked files that `git clean -fd` would delete
git restore --staged file          # unstage a file but keep your edits
```
Almost nothing committed is ever truly lost: `reflog` remembers for ~90 days. Always use `-n` (dry run) before a destructive command.

## Hooks, worktrees and .gitattributes
```bash
git worktree add ../course-fix fix-typo   # a 2nd working folder on another branch, no stashing needed
git worktree remove ../course-fix         # clean it up when done
echo '#!/bin/sh\npython -m pyflakes . || exit 1' > .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
git commit --no-verify                    # skip the hook in an emergency (use sparingly)
echo "*.pdf binary" >> .gitattributes     # tell git not to try to diff/merge PDFs as text
git log --stat -3                         # which files did the last 3 commits touch?
```
A **pre-commit hook** runs a check (tests, linter) before every commit: bad code never enters history.
A **worktree** lets you fix a bug on one branch while keeping your analysis open on another.
