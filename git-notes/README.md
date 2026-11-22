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

## Cherry-pick, grep, shortlog and resolving conflicts
```bash
git cherry-pick <commit>           # copy ONE commit from another branch onto the current one
git grep "read_csv"                # search the text of every tracked file (faster than grep -r)
git shortlog -sn                   # commits per author: who contributed what
git log --author="Ada" --oneline   # filter history by person
git merge feature                  # if it stops with "CONFLICT", open the file and look for markers:
#   <<<<<<< HEAD        your version
#   =======
#   >>>>>>> feature     their version
git add file && git commit         # after editing out the markers, mark it resolved
git merge --abort                  # give up and return to before the merge
```
A **conflict** is not an error: two branches changed the same lines and git asks you to choose. Keep both, one, or write something new, then commit.

## Amend, find-by-content, submodules and signed tags
```bash
git commit --amend -m "Better message"   # rewrite the LAST commit (only if not pushed yet!)
git commit --amend --no-edit             # add forgotten files to the last commit: git add file first
git log -S"kmeans" --oneline             # which commits added or removed the text "kmeans"?
git log -p -- 16-clustering/README.md    # full history of one file with the diffs
git show HEAD~2:README.md                # print a file as it was 2 commits ago
git tag -a v1.0 -m "Course complete"     # annotated tag: stores author, date and message
git submodule add <url> libs/tool        # embed another repository at a fixed commit
```
`--amend` replaces a commit with a new one (new hash), so never amend commits others already pulled. `log -S` is the "pickaxe": ideal to find *when* a function or a column name appeared.

## Archive, bundle, describe and clean
```bash
git archive -o course.zip HEAD            # zip of the current files only, without .git
git archive --format=tar HEAD 17-pca | gzip > pca.tgz   # export just one folder
git bundle create course.bundle --all     # the WHOLE repo in one file (send it by email / USB, no server needed)
git clone course.bundle copy              # restore a repository from a bundle
git describe --tags                       # name the commit from the nearest tag, e.g. v1.0-12-g3a1f9c2
git clean -nd                             # DRY RUN: list untracked files/folders that would be deleted
git clean -fd                             # actually delete them (cannot be undone!)
```
`archive` is how you share a clean copy of the course; `bundle` is an offline backup of the full history. `describe` gives human-friendly version names for builds and reports. Like `reset --hard`, `clean -f` is destructive: always run `-n` first.

## Sparse-checkout, notes, rerere and shallow clones
```bash
git clone --depth 1 <url>                 # shallow clone: only the latest commit (fast for big repos)
git sparse-checkout set 18-feature-engineering   # work tree shows only this folder
git sparse-checkout disable               # bring every folder back
git notes add -m "reviewed by Ada" HEAD   # attach a comment to a commit WITHOUT changing its hash
git log --show-notes                      # display those comments
git config rerere.enabled true            # "reuse recorded resolution": git remembers how you fixed a conflict
git rev-list --count HEAD                 # how many commits are in the history?
```
`--depth 1` saves time and disk; `sparse-checkout` is useful in a repo with many modules when you only edit one. `notes` annotate history after the fact, and `rerere` replays a conflict fix automatically when the same conflict appears again (handy when rebasing repeatedly).

## Stash-patch, patch mode and interactive staging
```bash
git add -p                       # review each change ("hunk") and stage only the ones you want: y / n / s (split) / q
git restore -p file.py           # discard only some hunks of a file
git stash -p                     # stash only selected hunks
git stash push -m "wip: cv" -- 19-cross-validation   # stash just one folder, with a name
git diff --stat                  # summary: files changed and +/- line counts
git diff --staged --name-only    # list the files that are about to be committed
git commit --fixup <hash>        # create a commit meant to be squashed into <hash> later
git rebase -i --autosquash       # squash the fixup commits automatically
```
`add -p` is the tool for **clean commits**: when you edited two unrelated things in one file, stage them separately so each commit has one purpose. Just like cross-validation, small honest steps give a history you can trust.

## Revision ranges, merge-base and custom log formats
```bash
git log main..feature            # commits in feature that are NOT in main (what a PR would add)
git log main...feature --left-right --oneline   # commits on either side but not both (< = main, > = feature)
git diff main...feature          # changes on feature since it branched off (what GitHub shows in a PR)
git merge-base main feature      # the common ancestor commit where the two branches split
git log --pretty=format:"%h %an %ad %s" --date=short   # custom one-line log: hash, author, date, subject
git log --since="2 weeks ago" -- 20-decision-trees     # recent history of one folder
git range-diff main~3..old main~3..new   # compare two versions of a branch after a rebase
```
Think of it like a decision tree for history: each range is a **question** you ask git ("what is here but not there?"). Two dots = *reachable from B but not A*; three dots = *the symmetric difference* for `log`, but *since the merge-base* for `diff`.

## Tracing history: log -L, blame -C and show rev:path
```bash
git log -L :boost:21-gradient-boosting/examples/boosting_demo.py   # every change to the function boost()
git log -L 40,60:README.md                # history of lines 40-60 only
git blame -w -C -C README.md              # who wrote each line, ignoring whitespace and following moved/copied code
git blame --ignore-rev <hash> file.py     # skip a big "reformat" commit in blame
git show HEAD~3:data/churn.csv | head     # print a file as it was 3 commits ago (no checkout needed)
git restore --source=HEAD~3 -- file.py    # bring back that old version into your working tree
git log --follow -- new_name.py           # keep the history across a rename
```
Like boosting, a codebase is built from many small corrections stacked on top of each other. `log -L` shows you that chain of corrections for one function, so you can see *why* each step was added, while `show rev:path` lets you peek at any earlier "round" without leaving your branch.

## Looking inside git: cat-file, ls-tree, rev-parse and gc
```bash
git rev-parse HEAD                     # full hash of the current commit
git rev-parse --short HEAD~2           # short hash of 2 commits ago
git cat-file -t HEAD                   # type of an object -> "commit"
git cat-file -p HEAD                   # print it: tree hash, parent(s), author, message
git ls-tree HEAD 22-interpretability/  # the tree: one line per file/folder with its blob/tree hash
git cat-file -p HEAD:README.md | head  # print a blob (file content) straight from the database
git hash-object README.md              # the hash git WOULD give this file - same content = same hash
git count-objects -vH                  # how many objects and how much disk the repo uses
git gc                                 # pack loose objects, prune garbage -> smaller, faster repo
git fsck                               # check that every object is intact and reachable
```
Git itself is a small, interpretable model: a **commit** points to a **tree** (a folder), which points to **blobs** (file contents) and other trees, all named by the SHA hash of their content (see `22-interpretability/diagrams/git_objects.pdf`). Because names come from content, an unchanged PDF is stored only once no matter how many commits include it – which is why committing diagrams in every lesson costs little space.

## Filtering history and finding unusual commits
```bash
git log --author="Claude" --oneline       # only commits by one author (regex, matches name or email)
git log --grep="module 2[0-9]" -i         # commits whose message matches a pattern
git log --since=2026-11-01 --until=2026-11-15 --oneline   # a date window
git log --diff-filter=A --name-only       # commits that ADDED files (D = deleted, R = renamed)
git log --numstat -1                      # lines added/deleted per file, last commit
git log --shortstat --oneline             # "3 files changed, 120 insertions(+)" per commit
git log --min-parents=2 --oneline         # merges only (= --merges); --max-parents=1 hides them
git log --format="%h %(trailers:key=Co-Authored-By,valueonly)"   # read commit trailers
git commit --trailer "Reviewed-by: Ana <ana@example.com>"        # add a trailer when committing
```
This is anomaly detection for your history: filter down to a window, compute a size per commit with `--numstat`, and look at the extremes (see `23-anomaly-detection/diagrams/git_commit_outliers.pdf`). A huge commit can be a data file (fine – or better tracked with Git LFS), a generated file that belongs in `.gitignore`, or several unrelated changes squashed together that should have been split. Trailers like `Co-Authored-By:` or `Reviewed-by:` are key/value lines at the end of the message that tools can read reliably.

## Co-change analysis, word-diff and maintenance
```bash
git log --no-merges --name-only --pretty=format:@     # commits as "baskets" of files (split on @)
git log --stat -5                       # files + insertions/deletions bar per commit
git log --format= --name-only | sort | uniq -c | sort -rn | head   # most frequently changed files ("hot spots")
git diff --word-diff HEAD~1             # changes word by word: ideal for Markdown lessons and reports
git diff --word-diff=color --word-diff-regex='[^[:space:],]+'      # treat each CSV cell as a "word"
git diff --color-moved=zebra HEAD~1     # blocks that were moved, not rewritten, get their own colour
git diff --ignore-all-space             # (-w) ignore indentation-only changes
git maintenance start                   # schedule background gc/prefetch/commit-graph for this repo
git maintenance run --task=commit-graph # speed up git log on big histories right now
```
Market basket analysis (module 24) works on history too: each commit is a receipt, each file an item. A file pair with high **lift** is coupled – change one, check the other. A file that appears in almost every commit (like this README) has high confidence with everything but lift ≈ 1, so it tells you nothing: the same popularity trap as milk in a supermarket. `--word-diff` makes reviewing prose and CSV changes much easier than line diffs, and `git maintenance` keeps a long-lived repository fast without thinking about it.

## Branch housekeeping: for-each-ref, --merged and prune
```bash
git for-each-ref --sort=-committerdate refs/heads \
    --format='%(refname:short) %(committerdate:relative) %(authorname)'   # branches by last activity
git branch --sort=-committerdate          # the same, short version
git branch --merged main                  # already in main -> safe to delete with git branch -d
git branch --no-merged main               # unfinished work: review or finish it
git branch -vv                            # each branch with its upstream and ahead/behind counts
git fetch --prune                         # (-p) drop remote-tracking branches deleted on the server
git config --global fetch.prune true      # ...and do it on every fetch
git push origin --delete old-branch       # delete a branch on GitHub from the command line
git log --date=format:'%Y-%m' --format=%ad | sort | uniq -c   # commits per month
```
Like customer cohorts (module 25), branches have a start date and an end date (the merge). Short-lived branches – one lesson, one PR, merged the same day – are easy to review and almost never conflict. Clean up regularly: `--merged` tells you what is safe to delete, `--no-merged` shows work that is still open, and `fetch --prune` keeps your list of remote branches in sync with GitHub.
