# Git Notes — Branching and Merging

Diagram: [`git_branching.pdf`](git_branching.pdf)

A **branch** is a movable pointer to a commit. Branches let you try an idea
(for example a new chart style) without touching the stable `main` history.

```bash
git switch -c cleaning-experiment     # create and switch
# ...edit, then...
git add -A && git commit -m "Try median imputation"
git switch main
git merge cleaning-experiment         # bring the work into main
git branch -d cleaning-experiment     # delete the merged branch
```

## Merge conflicts
A conflict happens when two branches changed the same lines. Git marks them:
```
<<<<<<< HEAD
price = df["price"].median()
=======
price = df["price"].mean()
>>>>>>> cleaning-experiment
```
Edit the file to keep what you want, remove the markers, then
`git add file && git commit`.

## Useful extras
```bash
git log --oneline --graph --all   # see branches as a graph
git tag v1.0                      # name an important commit
git stash                         # park unfinished changes
git stash pop                     # bring them back
```
